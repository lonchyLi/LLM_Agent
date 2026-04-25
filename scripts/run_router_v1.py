#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.json_io import save_json, save_jsonl
from src.data.unified_dataset import load_sample_records
from src.router.router_v1 import HeuristicRouterV1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-id", default=None)
    args = parser.parse_args()

    router = HeuristicRouterV1()
    samples = load_sample_records()
    if args.sample_id:
        sample = next(row for row in samples if str(row["sample_id"]) == args.sample_id)
        output = router.decide(sample)
        out_path = ROOT / "artifacts" / "router" / f"{args.sample_id}_router_v1.json"
        save_json(out_path, output)
        print(out_path)
        return

    outputs = [router.decide(sample) for sample in samples]
    out_path = ROOT / "artifacts" / "router" / "router_v1_outputs.jsonl"
    save_jsonl(out_path, outputs)
    print(out_path)


if __name__ == "__main__":
    main()
