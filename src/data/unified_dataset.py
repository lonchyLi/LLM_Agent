from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import jsonschema
from PIL import Image

from src.common.json_io import load_json


REPO_ROOT = Path(__file__).resolve().parents[2]


def _resolve_dataset_layout() -> dict[str, Path]:
    candidates = [REPO_ROOT / "data_set_v2", REPO_ROOT / "data_set"]
    for root in candidates:
        direct_manifest = root / "dataset_manifest.json"
        if direct_manifest.exists():
            return {
                "root": root,
                "manifest": direct_manifest,
                "samples": root / "sample_records.json",
                "questions": root / "question_records.json",
                "schema_dir": root / "schema",
                "images_dir": root / "images",
            }

        legacy_manifest = root / "examples" / "dataset_manifest_demo.json"
        if legacy_manifest.exists():
            return {
                "root": root,
                "manifest": legacy_manifest,
                "samples": root / "examples" / "sample_records_demo.json",
                "questions": root / "examples" / "question_records_demo.json",
                "schema_dir": root / "schema",
                "images_dir": root / "images",
            }

    raise FileNotFoundError("No supported dataset layout found under data_set_v2 or data_set.")


DATASET_LAYOUT = _resolve_dataset_layout()
DATASET_ROOT = DATASET_LAYOUT["root"]
MANIFEST_PATH = DATASET_LAYOUT["manifest"]
SAMPLE_RECORDS_PATH = DATASET_LAYOUT["samples"]
QUESTION_RECORDS_PATH = DATASET_LAYOUT["questions"]
SCHEMA_DIR = DATASET_LAYOUT["schema_dir"]
IMAGES_DIR = DATASET_LAYOUT["images_dir"]


def load_manifest() -> dict[str, Any]:
    return load_json(MANIFEST_PATH)


def load_sample_records() -> list[dict[str, Any]]:
    return load_json(SAMPLE_RECORDS_PATH)


def load_question_records() -> list[dict[str, Any]]:
    return load_json(QUESTION_RECORDS_PATH)


def load_schema(schema_name: str) -> dict[str, Any]:
    return load_json(SCHEMA_DIR / schema_name)


def validate_dataset() -> list[str]:
    errors: list[str] = []
    manifest = load_manifest()
    samples = load_sample_records()
    questions = load_question_records()

    try:
        jsonschema.validate(manifest, load_schema("dataset_manifest.schema.json"))
    except jsonschema.ValidationError as exc:
        errors.append(f"manifest: {exc.message}")

    sample_schema = load_schema("sample_record.schema.json")
    for idx, sample in enumerate(samples):
        try:
            jsonschema.validate(sample, sample_schema)
        except jsonschema.ValidationError as exc:
            errors.append(f"sample[{idx}] {sample.get('sample_id')}: {exc.message}")

    question_schema = load_schema("question_record.schema.json")
    for idx, question in enumerate(questions):
        try:
            jsonschema.validate(question, question_schema)
        except jsonschema.ValidationError as exc:
            errors.append(
                f"question[{idx}] {question.get('question_id')}: {exc.message}"
            )

    return errors


def build_question_index(
    question_records: list[dict[str, Any]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    questions = question_records or load_question_records()
    index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for question in questions:
        index[str(question["sample_id"])].append(question)
    return dict(index)


def resolve_sample_paths(sample: dict[str, Any]) -> dict[str, Path]:
    path_fields = [
        "image_path",
        "original_path",
        "tampered_path",
        "mask_path",
        "source_crop_path",
        "target_crop_path",
    ]
    resolved: dict[str, Path] = {}
    for field in path_fields:
        rel = sample.get(field)
        if rel:
            resolved[field] = DATASET_ROOT / rel
    return resolved


def image_info(path: Path) -> dict[str, Any]:
    with Image.open(path) as img:
        return {
            "width": img.width,
            "height": img.height,
            "mode": img.mode,
        }


def derived_from_sample_id(sample: dict[str, Any]) -> str | None:
    value = sample.get("raw_meta", {}).get("derived_from_sample")
    if value is None:
        return None
    return str(value)


def split_group_id(sample: dict[str, Any]) -> str:
    return derived_from_sample_id(sample) or str(sample["sample_id"])


def split_bucket(sample: dict[str, Any], sample_by_id: dict[str, dict[str, Any]]) -> str:
    parent_id = derived_from_sample_id(sample)
    if parent_id:
        parent = sample_by_id.get(parent_id)
        if parent:
            return str(parent["tamper_type_l2"])
    return str(sample["tamper_type_l2"])


def summarize_sample(sample: dict[str, Any]) -> str:
    attributes = sample.get("attributes", {})
    parts = [
        f"sample_id={sample['sample_id']}",
        f"dataset={sample['source_dataset']}",
        f"task_mode={sample['task_mode']}",
        f"l1={sample['tamper_status_l1']}",
        f"l2={sample['tamper_type_l2']}",
    ]
    derived_from = derived_from_sample_id(sample)
    if derived_from:
        parts.append(f"derived_from={derived_from}")
    object_class = attributes.get("object_class")
    if object_class:
        parts.append(f"object_class={object_class}")
    tampered_bucket = attributes.get("tampered_area_bucket")
    if tampered_bucket:
        parts.append(f"tampered_area={tampered_bucket}")
    if sample.get("caption"):
        parts.append(f"caption={sample['caption'][:120]}...")
    return "; ".join(parts)


def route_candidates_for_type(tamper_type: str) -> list[dict[str, Any]]:
    candidates_map = {
        "none": [
            ("none", 0.84),
            ("aigc_global", 0.07),
            ("splice", 0.04),
        ],
        "copy_move": [
            ("copy_move", 0.78),
            ("splice", 0.12),
            ("inpainting_replacement", 0.06),
        ],
        "splice": [
            ("splice", 0.74),
            ("inpainting_replacement", 0.14),
            ("copy_move", 0.08),
        ],
        "inpainting_removal": [
            ("inpainting_removal", 0.76),
            ("inpainting_replacement", 0.14),
            ("splice", 0.06),
        ],
        "inpainting_replacement": [
            ("inpainting_replacement", 0.75),
            ("splice", 0.15),
            ("inpainting_removal", 0.06),
        ],
        "aigc_global": [
            ("aigc_global", 0.81),
            ("none", 0.08),
            ("inpainting_replacement", 0.05),
        ],
    }
    return [
        {"label": label, "score": score}
        for label, score in candidates_map.get(
            tamper_type,
            [("uncertain", 0.5), ("splice", 0.2), ("aigc_global", 0.1)],
        )
    ]


def default_tool_candidates(tamper_type: str) -> list[dict[str, Any]]:
    tool_map = {
        "none": [
            ("FakeShield", 1, "优先验证是否存在明显生成或篡改痕迹"),
            ("ForgeryGPT", 2, "补充是否存在局部异常的语义解释"),
        ],
        "copy_move": [
            ("SelfSimilarityDetector", 1, "复制区域检测优先"),
            ("ForgeryGPT", 1, "需要语义和区域关系解释"),
            ("MaskSegmentor", 2, "输出像素级掩码"),
        ],
        "splice": [
            ("FakeShield", 1, "需要真假与边界异常证据"),
            ("FFTArtifactDetector", 1, "频域异常验证"),
            ("EdgeBoundaryDetector", 2, "边界融合检查"),
        ],
        "inpainting_removal": [
            ("ForgeryGPT", 1, "需要纹理补全语义解释"),
            ("NoiseResidualDetector", 1, "局部纹理异常验证"),
            ("MaskSegmentor", 2, "输出掩码"),
        ],
        "inpainting_replacement": [
            ("ForgeryGPT", 1, "需要语义替换解释"),
            ("FakeShield", 2, "补充视觉异常证据"),
            ("MaskSegmentor", 2, "输出掩码"),
        ],
        "aigc_global": [
            ("FakeShield", 1, "全图真假判断"),
            ("FFTArtifactDetector", 2, "全图频域异常"),
            ("SceneLayoutChecker", 2, "场景结构合理性检查"),
        ],
    }
    return [
        {"tool": tool, "priority": priority, "reason": reason}
        for tool, priority, reason in tool_map.get(tamper_type, [])
    ]


def make_router_target(sample: dict[str, Any]) -> dict[str, Any]:
    coarse_label = sample["tamper_status_l1"]
    tamper_type = sample["tamper_type_l2"]
    task_mode = sample["task_mode"]
    uncertainty = {
        "none": 0.08,
        "aigc_global": 0.11,
    }.get(tamper_type, 0.18)
    reasoning = {
        "none": [
            "样本为 classification 模式且无定位真值，更适合作为真实图或全图异常的粗判任务。",
            "当前没有显式局部监督信号，优先验证是否缺少篡改和生成痕迹。",
            "建议调用 FakeShield 做真假粗检，再用 ForgeryGPT 补充局部异常解释。",
        ],
        "copy_move": [
            "样本存在源区域与目标区域成对信息，优先怀疑 copy_move。",
            "需要重复纹理与区域关系证据。",
            "建议调用 self-similarity 和掩码工具。",
        ],
        "splice": [
            "样本为局部篡改且缺少 source-target 成对区域，更像 splice。",
            "需要边界和频域证据交叉验证。",
            "建议调用 FakeShield 和 FFT 类工具。",
        ],
        "inpainting_removal": [
            "样本更像目标移除后补全的局部异常。",
            "需要纹理连续性和噪声残差证据。",
            "建议调用 ForgeryGPT 和 NoiseResidualDetector。",
        ],
        "inpainting_replacement": [
            "样本更像语义替换型局部篡改。",
            "需要语义解释和区域异常证据。",
            "建议调用 ForgeryGPT、FakeShield 与掩码工具。",
        ],
        "aigc_global": [
            "样本为 classification 模式且没有定位真值，优先视为全图生成检测。",
            "需要全图真假和频域证据。",
            "建议调用 FakeShield 与全图检测工具。",
        ],
    }
    task_description_map = {
        "none": "判断该遥感图像是否为真实未篡改图像",
        "aigc_global": "判断该遥感图像是否存在全图生成痕迹",
    }
    return {
        "sample_id": str(sample["sample_id"]),
        "round_id": 1,
        "task_mode": task_mode,
        "modality": "remote_sensing_rgb",
        "coarse_label": coarse_label,
        "coarse_type_candidates": route_candidates_for_type(tamper_type),
        "uncertainty": uncertainty,
        "task_description": task_description_map.get(
            tamper_type,
            "判断该遥感图像是否存在局部篡改，并输出可疑区域",
        ),
        "tool_candidates": default_tool_candidates(tamper_type),
        "need_next_round": True,
        "reasoning_summary": reasoning[tamper_type],
    }


def build_classification_dataset(
    records: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    samples = records or load_sample_records()
    splits = deterministic_splits(samples)
    split_by_id = {
        sample_id: split_name
        for split_name, sample_ids in splits.items()
        for sample_id in sample_ids
    }
    rows: list[dict[str, Any]] = []
    for sample in samples:
        rows.append(
            {
                "sample_id": str(sample["sample_id"]),
                "split": split_by_id[str(sample["sample_id"])],
                "image_path": sample["image_path"],
                "source_dataset": sample["source_dataset"],
                "task_mode": sample["task_mode"],
                "label_l1": sample["tamper_status_l1"],
                "label_l2": sample["tamper_type_l2"],
                "group_id": split_group_id(sample),
                "metadata_summary": summarize_sample(sample),
            }
        )
    return rows


def build_localization_dataset(
    records: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    samples = records or load_sample_records()
    splits = deterministic_splits(samples)
    split_by_id = {
        sample_id: split_name
        for split_name, sample_ids in splits.items()
        for sample_id in sample_ids
    }
    rows: list[dict[str, Any]] = []
    for sample in samples:
        if sample["task_mode"] != "classification_localization":
            continue
        rows.append(
            {
                "sample_id": str(sample["sample_id"]),
                "split": split_by_id[str(sample["sample_id"])],
                "image_path": sample["image_path"],
                "mask_path": sample["mask_path"],
                "label_l2": sample["tamper_type_l2"],
                "group_id": split_group_id(sample),
                "metadata_summary": summarize_sample(sample),
            }
        )
    return rows


def build_sft_dataset(
    records: list[dict[str, Any]] | None = None,
    question_index: dict[str, list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    samples = records or load_sample_records()
    splits = deterministic_splits(samples)
    split_by_id = {
        sample_id: split_name
        for split_name, sample_ids in splits.items()
        for sample_id in sample_ids
    }
    q_index = question_index or build_question_index()
    rows: list[dict[str, Any]] = []
    for sample in samples:
        sample_questions = q_index.get(str(sample["sample_id"]), [])
        question_preview = [
            {
                "question_type": q["question_type"],
                "question": q["question"],
                "answer": q["answer"],
            }
            for q in sample_questions[:5]
        ]
        rows.append(
            {
                "sample_id": str(sample["sample_id"]),
                "split": split_by_id[str(sample["sample_id"])],
                "image_path": sample["image_path"],
                "input": {
                    "task_mode": sample["task_mode"],
                    "source_dataset": sample["source_dataset"],
                    "metadata_summary": summarize_sample(sample),
                    "question_preview": question_preview,
                },
                "target": make_router_target(sample),
            }
        )
    return rows


def _recommended_split_counts(group_count: int) -> tuple[int, int, int]:
    if group_count <= 1:
        return group_count, 0, 0
    if group_count == 2:
        return 1, 0, 1

    train = max(1, int(group_count * 0.6))
    val = max(1, int(group_count * 0.2))
    test = group_count - train - val

    if test <= 0:
        test = 1
        if train >= val and train > 1:
            train -= 1
        elif val > 1:
            val -= 1

    while train + val + test > group_count:
        if train >= val and train > 1:
            train -= 1
        elif val > 1:
            val -= 1
        else:
            test -= 1

    return train, val, test


def deterministic_splits(
    records: list[dict[str, Any]] | None = None,
) -> dict[str, list[str]]:
    samples = records or load_sample_records()
    sample_by_id = {str(sample["sample_id"]): sample for sample in samples}
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for sample in samples:
        bucket = split_bucket(sample, sample_by_id)
        group_id = split_group_id(sample)
        grouped[bucket][group_id].append(sample)

    split_map = {"train": [], "val": [], "test": []}
    for _, group_map in sorted(grouped.items()):
        ordered_groups = [
            group_map[group_id]
            for group_id in sorted(group_map, key=lambda item: int(str(item)))
        ]
        train_count, val_count, _ = _recommended_split_counts(len(ordered_groups))
        for index, group in enumerate(ordered_groups):
            if index < train_count:
                split_name = "train"
            elif index < train_count + val_count:
                split_name = "val"
            else:
                split_name = "test"
            split_map[split_name].extend(
                str(row["sample_id"])
                for row in sorted(group, key=lambda item: int(str(item["sample_id"])))
            )
    return split_map


def attach_split_to_records(
    records: list[dict[str, Any]], splits: dict[str, list[str]]
) -> list[dict[str, Any]]:
    split_by_id = {
        sample_id: split_name
        for split_name, sample_ids in splits.items()
        for sample_id in sample_ids
    }
    patched = []
    for record in records:
        updated = dict(record)
        updated["split"] = split_by_id[str(record["sample_id"])]
        patched.append(updated)
    return patched


def audit_dataset(
    records: list[dict[str, Any]] | None = None,
    question_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    samples = records or load_sample_records()
    questions = question_records or load_question_records()
    q_index = build_question_index(questions)
    sample_by_id = {str(sample["sample_id"]): sample for sample in samples}
    issues: list[str] = []

    per_l1 = Counter(sample["tamper_status_l1"] for sample in samples)
    per_type = Counter(sample["tamper_type_l2"] for sample in samples)
    per_mode = Counter(sample["task_mode"] for sample in samples)
    per_question_type = Counter(question["question_type"] for question in questions)
    sample_audits: list[dict[str, Any]] = []

    for sample in sorted(samples, key=lambda row: int(str(row["sample_id"]))):
        resolved = resolve_sample_paths(sample)
        missing_files = [
            field for field, path in resolved.items() if not path.exists()
        ]
        if missing_files:
            issues.append(
                f"{sample['sample_id']} missing files: {', '.join(sorted(missing_files))}"
            )

        if sample["task_mode"] == "classification" and sample["has_localization_gt"]:
            issues.append(
                f"{sample['sample_id']} classification sample should not have localization gt"
            )
        if (
            sample["task_mode"] == "classification_localization"
            and not sample["has_localization_gt"]
        ):
            issues.append(
                f"{sample['sample_id']} localization sample missing localization gt"
            )

        if sample["tamper_type_l2"] == "copy_move":
            if not sample.get("source_crop_path") or not sample.get("target_crop_path"):
                issues.append(f"{sample['sample_id']} copy_move missing crop paths")

        if sample["tamper_type_l2"] == "aigc_global" and sample.get("mask_path"):
            issues.append(f"{sample['sample_id']} aigc_global should not have mask_path")

        if sample["tamper_type_l2"] == "none":
            parent_id = derived_from_sample_id(sample)
            if not parent_id:
                issues.append(f"{sample['sample_id']} authentic sample missing derived_from_sample")
            elif parent_id not in sample_by_id:
                issues.append(
                    f"{sample['sample_id']} authentic sample refers to missing parent {parent_id}"
                )
            if sample.get("question_ids"):
                issues.append(f"{sample['sample_id']} authentic sample should not have question_ids")
            for field in ("tampered_path", "mask_path", "source_crop_path", "target_crop_path"):
                if sample.get(field):
                    issues.append(f"{sample['sample_id']} authentic sample should not have {field}")

        image_details = {}
        if "image_path" in resolved and resolved["image_path"].exists():
            image_details = image_info(resolved["image_path"])

        sample_questions = q_index.get(str(sample["sample_id"]), [])
        linked_question_ids = {str(q["question_id"]) for q in sample_questions}
        declared_question_ids = {str(qid) for qid in sample["question_ids"]}
        if linked_question_ids != declared_question_ids:
            issues.append(
                f"{sample['sample_id']} question linkage mismatch declared={len(declared_question_ids)} actual={len(linked_question_ids)}"
            )

        sample_audits.append(
            {
                "sample_id": str(sample["sample_id"]),
                "tamper_status_l1": sample["tamper_status_l1"],
                "tamper_type_l2": sample["tamper_type_l2"],
                "task_mode": sample["task_mode"],
                "question_count": len(sample_questions),
                "missing_files": missing_files,
                "image_details": image_details,
                "summary": summarize_sample(sample),
            }
        )

    return {
        "dataset_name": load_manifest()["dataset_name"],
        "dataset_root": str(DATASET_ROOT.relative_to(REPO_ROOT)),
        "sample_count": len(samples),
        "question_count": len(questions),
        "per_l1": dict(per_l1),
        "per_type": dict(per_type),
        "per_mode": dict(per_mode),
        "per_question_type": dict(sorted(per_question_type.items(), key=lambda x: x[0])),
        "issues": sorted(set(issues)),
        "sample_audits": sample_audits,
    }
