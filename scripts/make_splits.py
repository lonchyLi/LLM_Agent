#!/usr/bin/env python
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.json_io import save_json
from src.data.unified_dataset import deterministic_splits, load_sample_records


def main() -> None:
    samples = load_sample_records()
    splits = deterministic_splits(samples)
    split_dir = ROOT / "artifacts" / "splits"
    split_dir.mkdir(parents=True, exist_ok=True)
    for split_name, sample_ids in splits.items():
        payload = {
            "split": split_name,
            "sample_ids": sample_ids,
            "count": len(sample_ids),
        }
        save_json(split_dir / f"{split_name}.json", payload)
        print(split_dir / f"{split_name}.json")


if __name__ == "__main__":
    main()
