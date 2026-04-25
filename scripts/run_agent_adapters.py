#!/usr/bin/env python
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agents import FakeShieldAgentAdapter, ForgeryGPTAgentAdapter
from src.agents.cache import ToolResultCache
from src.common.json_io import save_jsonl
from src.data.unified_dataset import DATASET_ROOT, load_sample_records
from src.router.router_v1 import HeuristicRouterV1


def build_run_log(
    rows: list[dict],
    cache_stats: dict[str, dict[str, int]],
    sample_count: int,
    sample_id: str | None,
) -> str:
    tool_counts = Counter(row["tool_name"] for row in rows)
    top_labels = Counter(
        max(row["label_support"], key=row["label_support"].get) for row in rows
    )
    lines = [
        f"[{datetime.now().isoformat(timespec='seconds')}] agent adapter run",
        f"dataset_root={DATASET_ROOT}",
        f"sample_scope={sample_id or 'all'}",
        f"sample_count={sample_count}",
        f"result_count={len(rows)}",
        f"tool_counts={dict(sorted(tool_counts.items()))}",
        f"top_label_counts={dict(sorted(top_labels.items()))}",
        "cache_stats=" + str({key: cache_stats[key] for key in sorted(cache_stats)}),
        "",
        "sample_results:",
    ]
    for row in rows[:20]:
        top_label = max(row["label_support"], key=row["label_support"].get)
        lines.append(
            f"- sample_id={row['sample_id']}, tool={row['tool_name']}, "
            f"score={row['score']}, top_label={top_label}, status={row['status']}"
        )
    if len(rows) > 20:
        lines.append(f"- ... truncated {len(rows) - 20} additional rows")
    lines.append("")
    return "\n".join(lines)


def build_tool_logs(rows: list[dict], cache_stats: dict[str, dict[str, int]]) -> dict[str, str]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["tool_name"]].append(row)

    logs: dict[str, str] = {}
    for tool_name, tool_rows in sorted(grouped.items()):
        label_counts = Counter(
            max(row["label_support"], key=row["label_support"].get) for row in tool_rows
        )
        lines = [
            f"[{datetime.now().isoformat(timespec='seconds')}] {tool_name} adapter run",
            f"tool_name={tool_name}",
            f"result_count={len(tool_rows)}",
            f"cache_hits={cache_stats.get(tool_name, {}).get('cached', 0)}",
            f"new_results={cache_stats.get(tool_name, {}).get('new', 0)}",
            f"top_label_counts={dict(sorted(label_counts.items()))}",
            "",
            "rows:",
        ]
        for row in tool_rows[:20]:
            top_label = max(row["label_support"], key=row["label_support"].get)
            lines.append(
                f"- sample_id={row['sample_id']}, score={row['score']}, "
                f"top_label={top_label}, summary={row['summary']}"
            )
        if len(tool_rows) > 20:
            lines.append(f"- ... truncated {len(tool_rows) - 20} additional rows")
        lines.append("")
        logs[tool_name] = "\n".join(lines)
    return logs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-id", default=None)
    args = parser.parse_args()

    samples = load_sample_records()
    if args.sample_id:
        samples = [row for row in samples if str(row["sample_id"]) == args.sample_id]

    router = HeuristicRouterV1()
    cache = ToolResultCache(ROOT / "artifacts" / "cache" / "tool_results")
    adapters = {
        "FakeShield": FakeShieldAgentAdapter(cache),
        "ForgeryGPT": ForgeryGPTAgentAdapter(cache),
    }

    rows = []
    cache_stats: dict[str, dict[str, int]] = {
        tool_name: {"cached": 0, "new": 0} for tool_name in adapters
    }
    for sample in samples:
        router_output = router.decide(sample)
        for tool in router_output["tool_candidates"]:
            adapter = adapters.get(tool["tool"])
            if adapter is None:
                continue
            cache_path = cache.cache_path(
                adapter.tool_name, str(sample["sample_id"]), int(router_output["round_id"])
            )
            was_cached = cache_path.exists()
            rows.append(adapter.run(sample, router_output))
            cache_stats[adapter.tool_name]["cached" if was_cached else "new"] += 1

    out_path = ROOT / "artifacts" / "agents" / "agent_results.jsonl"
    save_jsonl(out_path, rows)
    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    run_log_path = log_dir / "agent_adapters_run.log"
    run_log_path.write_text(
        build_run_log(rows, cache_stats, len(samples), args.sample_id),
        encoding="utf-8",
    )
    tool_logs = build_tool_logs(rows, cache_stats)
    tool_log_paths = []
    for tool_name, payload in tool_logs.items():
        log_path = log_dir / f"{tool_name.lower()}_agent.log"
        log_path.write_text(payload, encoding="utf-8")
        tool_log_paths.append(log_path)
    print(out_path)
    print(run_log_path)
    for log_path in tool_log_paths:
        print(log_path)


if __name__ == "__main__":
    main()
