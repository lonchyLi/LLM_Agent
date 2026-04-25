from __future__ import annotations

from typing import Any

from src.data.unified_dataset import make_router_target


class HeuristicRouterV1:
    """Metadata-driven router prototype for the first two weeks."""

    def decide(self, sample: dict[str, Any]) -> dict[str, Any]:
        return make_router_target(sample)
