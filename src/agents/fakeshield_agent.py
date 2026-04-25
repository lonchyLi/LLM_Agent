from __future__ import annotations

from typing import Any

from src.agents.cache import ToolResultCache


LABEL_KEYS = [
    "none",
    "copy_move",
    "splice",
    "inpainting_removal",
    "inpainting_replacement",
    "aigc_global",
]


def _empty_support() -> dict[str, float]:
    return {key: 0.0 for key in LABEL_KEYS}


class FakeShieldAgentAdapter:
    tool_name = "FakeShield"

    def __init__(self, cache: ToolResultCache) -> None:
        self.cache = cache

    def run(self, sample: dict[str, Any], router_output: dict[str, Any]) -> dict[str, Any]:
        sample_id = str(sample["sample_id"])
        round_id = int(router_output["round_id"])
        return self.cache.get_or_run(
            self.tool_name,
            sample_id,
            round_id,
            lambda: self._build_result(sample, router_output),
        )

    def _build_result(
        self, sample: dict[str, Any], router_output: dict[str, Any]
    ) -> dict[str, Any]:
        support = _empty_support()
        candidate_scores = {
            item["label"]: float(item["score"])
            for item in router_output.get("coarse_type_candidates", [])
        }
        support.update({key: candidate_scores.get(key, 0.0) for key in support})

        coarse_label = router_output["coarse_label"]
        if coarse_label == "authentic":
            support["none"] = max(support["none"], 0.82)
            support["aigc_global"] = min(support["aigc_global"], 0.08)
        elif coarse_label == "fully_generated":
            support["aigc_global"] = max(support["aigc_global"], 0.86)
            support["none"] = min(support["none"], 0.06)
        elif coarse_label == "manipulated":
            local_best = max(
                ("copy_move", "splice", "inpainting_removal", "inpainting_replacement"),
                key=lambda key: support[key],
            )
            support[local_best] = max(support[local_best], 0.72)

        top_label = max(support, key=support.get)
        top_score = round(float(support[top_label]), 6)
        return {
            "sample_id": str(sample["sample_id"]),
            "round_id": int(router_output["round_id"]),
            "tool_name": self.tool_name,
            "status": "success",
            "score": top_score,
            "label_support": {key: round(value, 6) for key, value in support.items()},
            "summary": (
                f"FakeShield baseline adapter favors `{top_label}` under coarse label "
                f"`{router_output['coarse_label']}`."
            ),
        }
