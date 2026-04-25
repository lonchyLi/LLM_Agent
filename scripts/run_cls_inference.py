#!/usr/bin/env python
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.classification import BaselineImageClassifierV1
from src.common.json_io import save_json, save_jsonl
from src.data.unified_dataset import DATASET_ROOT, build_classification_dataset, load_sample_records


def build_batch_log(predictions: list[dict]) -> str:
    split_counts = Counter(row["split"] for row in predictions)
    l1_correct = sum(int(row["predicted_l1"] == row["true_l1"]) for row in predictions)
    l2_correct = sum(int(row["predicted_l2"] == row["true_l2"]) for row in predictions)
    lines = [
        f"[{datetime.now().isoformat(timespec='seconds')}] classifier_baseline_v1 batch inference run",
        f"dataset_root={DATASET_ROOT}",
        f"prediction_count={len(predictions)}",
        f"split_counts={dict(sorted(split_counts.items()))}",
        f"overall_l1_accuracy={round(l1_correct / len(predictions), 6) if predictions else 0.0}",
        f"overall_l2_accuracy={round(l2_correct / len(predictions), 6) if predictions else 0.0}",
        "",
        "per_split_metrics:",
    ]
    for split_name in sorted(split_counts):
        split_rows = [row for row in predictions if row["split"] == split_name]
        split_l1 = sum(int(row["predicted_l1"] == row["true_l1"]) for row in split_rows)
        split_l2 = sum(int(row["predicted_l2"] == row["true_l2"]) for row in split_rows)
        lines.append(
            f"- {split_name}: count={len(split_rows)}, "
            f"l1_accuracy={round(split_l1 / len(split_rows), 6)}, "
            f"l2_accuracy={round(split_l2 / len(split_rows), 6)}"
        )
    errors = [
        row
        for row in predictions
        if row["predicted_l1"] != row["true_l1"] or row["predicted_l2"] != row["true_l2"]
    ]
    lines.extend(["", "sample_errors:"])
    if errors:
        for row in errors[:15]:
            lines.append(
                f"- sample_id={row['sample_id']}, split={row['split']}, "
                f"true=({row['true_l1']}, {row['true_l2']}), "
                f"pred=({row['predicted_l1']}, {row['predicted_l2']}), "
                f"confidence_l1={row['confidence_l1']}, confidence_l2={row['confidence_l2']}"
            )
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-id", default=None)
    parser.add_argument(
        "--model-dir",
        default=str(ROOT / "artifacts" / "models" / "classifier_baseline_v1"),
    )
    args = parser.parse_args()

    rows = build_classification_dataset(load_sample_records())
    model = BaselineImageClassifierV1.load(args.model_dir)

    if args.sample_id:
        row = next(row for row in rows if str(row["sample_id"]) == args.sample_id)
        prediction = model.predict(row["image_path"], sample_id=args.sample_id)
        prediction["split"] = row["split"]
        prediction["true_l1"] = row["label_l1"]
        prediction["true_l2"] = row["label_l2"]
        out_path = ROOT / "artifacts" / "classification" / f"{args.sample_id}_prediction.json"
        save_json(out_path, prediction)
        log_dir = ROOT / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"classifier_baseline_v1_inference_{args.sample_id}.log"
        log_path.write_text(
            "\n".join(
                [
                    f"[{datetime.now().isoformat(timespec='seconds')}] classifier_baseline_v1 single inference run",
                    f"dataset_root={DATASET_ROOT}",
                    f"sample_id={prediction['sample_id']}",
                    f"split={prediction['split']}",
                    f"true_l1={prediction['true_l1']}",
                    f"true_l2={prediction['true_l2']}",
                    f"predicted_l1={prediction['predicted_l1']}",
                    f"predicted_l2={prediction['predicted_l2']}",
                    f"confidence_l1={prediction['confidence_l1']}",
                    f"confidence_l2={prediction['confidence_l2']}",
                    f"neighbor_count={len(prediction['neighbors'])}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        print(out_path)
        print(log_path)
        return

    predictions = []
    for row in rows:
        prediction = model.predict(row["image_path"], sample_id=str(row["sample_id"]))
        prediction["split"] = row["split"]
        prediction["true_l1"] = row["label_l1"]
        prediction["true_l2"] = row["label_l2"]
        predictions.append(prediction)

    out_path = ROOT / "artifacts" / "classification" / "classification_predictions.jsonl"
    save_jsonl(out_path, predictions)
    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "classifier_baseline_v1_inference.log"
    log_path.write_text(build_batch_log(predictions), encoding="utf-8")
    print(out_path)
    print(log_path)


if __name__ == "__main__":
    main()
