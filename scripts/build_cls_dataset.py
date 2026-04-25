#!/usr/bin/env python
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.json_io import save_jsonl
from src.data.unified_dataset import build_classification_dataset, load_sample_records


def main() -> None:
    rows = build_classification_dataset(load_sample_records())
    out_path = ROOT / "artifacts" / "datasets" / "classification_dataset.jsonl"
    save_jsonl(out_path, rows)
    print(out_path)


if __name__ == "__main__":
    main()
