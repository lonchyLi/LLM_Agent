from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from src.common.json_io import load_json, save_json


class ToolResultCache:
    def __init__(self, cache_root: str | Path) -> None:
        self.cache_root = Path(cache_root)

    def cache_path(self, tool_name: str, sample_id: str, round_id: int) -> Path:
        return self.cache_root / tool_name / f"{sample_id}_round{round_id}.json"

    def get(self, tool_name: str, sample_id: str, round_id: int) -> dict[str, Any] | None:
        path = self.cache_path(tool_name, sample_id, round_id)
        if path.exists():
            return load_json(path)
        return None

    def put(
        self,
        tool_name: str,
        sample_id: str,
        round_id: int,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        path = self.cache_path(tool_name, sample_id, round_id)
        save_json(path, payload)
        return payload

    def get_or_run(
        self,
        tool_name: str,
        sample_id: str,
        round_id: int,
        builder: Callable[[], dict[str, Any]],
    ) -> dict[str, Any]:
        cached = self.get(tool_name, sample_id, round_id)
        if cached is not None:
            return cached
        return self.put(tool_name, sample_id, round_id, builder())
