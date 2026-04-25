#!/usr/bin/env python
from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "artifacts" / "mplconfig"))

import matplotlib.pyplot as plt
from PIL import Image

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.unified_dataset import load_sample_records, resolve_sample_paths, summarize_sample


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sample_id")
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output path. Defaults to artifacts/previews/<sample_id>.png",
    )
    args = parser.parse_args()

    sample = next(
        row for row in load_sample_records() if str(row["sample_id"]) == args.sample_id
    )
    paths = resolve_sample_paths(sample)
    image_fields = [field for field in paths if paths[field].exists()]
    cols = 3
    rows = math.ceil(len(image_fields) / cols) if image_fields else 1
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3.6 * rows))
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]

    for ax in axes:
        ax.axis("off")

    for idx, field in enumerate(image_fields):
        ax = axes[idx]
        with Image.open(paths[field]) as img:
            ax.imshow(img)
        ax.set_title(field)
        ax.axis("off")

    fig.suptitle(summarize_sample(sample), fontsize=10)
    fig.tight_layout()

    output_path = (
        Path(args.output)
        if args.output
        else ROOT / "artifacts" / "previews" / f"{args.sample_id}.png"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(output_path)


if __name__ == "__main__":
    main()
