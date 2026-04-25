#!/usr/bin/env python
from __future__ import annotations

from collections import Counter
from datetime import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.classification import BaselineImageClassifierV1
from src.common.json_io import save_json
from src.data.unified_dataset import DATASET_ROOT, build_classification_dataset, load_sample_records


def build_train_log(rows: list[dict], metrics: dict) -> str:
    split_counts = Counter(row["split"] for row in rows)
    l1_counts = Counter(row["label_l1"] for row in rows)
    l2_counts = Counter(row["label_l2"] for row in rows)
    lines = [
        f"[{datetime.now().isoformat(timespec='seconds')}] classifier_baseline_v1 training run",
        f"dataset_root={DATASET_ROOT}",
        f"sample_count={len(rows)}",
        f"split_counts={dict(sorted(split_counts.items()))}",
        f"label_l1_counts={dict(sorted(l1_counts.items()))}",
        f"label_l2_counts={dict(sorted(l2_counts.items()))}",
        "feature_extractor=16x16 RGB thumbnail + color stats + histogram",
        "classifier_type=top-k nearest neighbor",
        "",
        f"metrics.total={metrics['total']}",
        f"metrics.l1_accuracy={metrics['l1_accuracy']}",
        f"metrics.l2_accuracy={metrics['l2_accuracy']}",
    ]
    for split_name, split_metrics in sorted(metrics["per_split"].items()):
        lines.append(
            "metrics."
            f"{split_name}=count:{split_metrics['count']},"
            f"l1_accuracy:{split_metrics['l1_accuracy']},"
            f"l2_accuracy:{split_metrics['l2_accuracy']}"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    rows = build_classification_dataset(load_sample_records())
    model = BaselineImageClassifierV1.fit(rows)
    metrics = model.evaluate(rows)
    model_dir = ROOT / "artifacts" / "models" / "classifier_baseline_v1"
    metadata = {
        "model_name": "classifier_baseline_v1",
        "train_count": sum(1 for row in rows if row["split"] == "train"),
        "feature_extractor": "16x16 RGB thumbnail + color stats + histogram",
        "classifier_type": "top-k nearest neighbor",
        "k": model.k,
        "metrics": metrics,
    }
    model.save(model_dir, metadata=metadata)
    save_json(model_dir / "metrics.json", metrics)
    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "classifier_baseline_v1_train.log"
    log_path.write_text(build_train_log(rows, metrics), encoding="utf-8")
    print(model_dir)
    print(model_dir / "metrics.json")
    print(log_path)


if __name__ == "__main__":
    main()
