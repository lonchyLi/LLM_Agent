#!/usr/bin/env python
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.json_io import save_json
from src.data.unified_dataset import audit_dataset


def build_markdown_report(audit: dict) -> str:
    lines = [
        f"# {audit['dataset_name']} Audit Report",
        "",
        f"- dataset_root: `{audit['dataset_root']}`",
        f"- dataset_name: `{audit['dataset_name']}`",
        f"- sample_count: `{audit['sample_count']}`",
        f"- question_count: `{audit['question_count']}`",
        "",
        "## Per L1",
        "",
    ]
    for key, value in sorted(audit["per_l1"].items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend([
        "",
        "## Per Type",
        "",
    ])
    for key, value in sorted(audit["per_type"].items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Per Task Mode", ""])
    for key, value in sorted(audit["per_mode"].items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Per Question Type", ""])
    for key, value in audit["per_question_type"].items():
        lines.append(f"- `question_type={key}`: `{value}`")
    lines.extend(["", "## Issues", ""])
    if audit["issues"]:
        for issue in audit["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- No validation or linkage issues found.")
    lines.extend(["", "## Sample Summaries", ""])
    for row in audit["sample_audits"]:
        details = row["image_details"]
        size_text = (
            f"{details.get('width')}x{details.get('height')} {details.get('mode')}"
            if details
            else "unknown"
        )
        lines.append(
            f"- `{row['sample_id']}` | `{row['tamper_type_l2']}` | `{row['task_mode']}` | "
            f"questions=`{row['question_count']}` | image=`{size_text}`"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    audit = audit_dataset()
    out_json = ROOT / "artifacts" / "audit" / "data_audit_report.json"
    out_md = ROOT / "artifacts" / "audit" / "data_audit_report.md"
    save_json(out_json, audit)
    out_md.write_text(build_markdown_report(audit), encoding="utf-8")
    print(out_json)
    print(out_md)


if __name__ == "__main__":
    main()
