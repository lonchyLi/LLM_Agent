#!/usr/bin/env python
from __future__ import annotations

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

from src.data.unified_dataset import DATASET_ROOT, load_sample_records


def main() -> None:
    records = load_sample_records()
    grouped: dict[str, list[dict]] = {}
    for row in records:
        grouped.setdefault(row["tamper_type_l2"], []).append(row)

    out_dir = ROOT / "artifacts" / "previews"
    out_dir.mkdir(parents=True, exist_ok=True)

    for tamper_type, rows in sorted(grouped.items()):
        cols = 2
        total = len(rows)
        grid_rows = math.ceil(total / cols)
        fig, axes = plt.subplots(grid_rows, cols, figsize=(5 * cols, 4 * grid_rows))
        axes = axes.flatten() if hasattr(axes, "flatten") else [axes]
        for ax in axes:
            ax.axis("off")

        for idx, sample in enumerate(sorted(rows, key=lambda x: x["sample_id"])):
            ax = axes[idx]
            image_path = DATASET_ROOT / sample["image_path"]
            with Image.open(image_path) as img:
                ax.imshow(img)
            ax.set_title(f"{sample['sample_id']} | {sample['source_dataset']}")
            ax.axis("off")

        fig.suptitle(f"{tamper_type} previews", fontsize=12)
        fig.tight_layout()
        output_path = out_dir / f"preview_{tamper_type}.png"
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(output_path)


if __name__ == "__main__":
    main()
