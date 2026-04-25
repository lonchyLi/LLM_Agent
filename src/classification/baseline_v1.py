from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from src.data.unified_dataset import DATASET_ROOT


L1_LABELS = ["authentic", "manipulated", "fully_generated", "unknown"]
L2_LABELS = [
    "none",
    "copy_move",
    "splice",
    "inpainting_removal",
    "inpainting_replacement",
    "aigc_global",
    "uncertain",
]


def _normalize(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm == 0.0:
        return vector
    return vector / norm


def _softmax(scores: np.ndarray) -> np.ndarray:
    shifted = scores - np.max(scores)
    exp = np.exp(shifted)
    denom = np.sum(exp)
    if denom == 0:
        return np.ones_like(scores) / len(scores)
    return exp / denom


class BaselineImageClassifierV1:
    """A small non-parametric image baseline for week-3 closed-set classification."""

    def __init__(
        self,
        train_features: np.ndarray,
        sample_ids: list[str],
        label_l1: list[str],
        label_l2: list[str],
        image_paths: list[str],
        k: int = 3,
    ) -> None:
        self.train_features = train_features.astype(np.float32)
        self.sample_ids = sample_ids
        self.label_l1 = label_l1
        self.label_l2 = label_l2
        self.image_paths = image_paths
        self.k = min(k, len(sample_ids)) if sample_ids else 1

    @staticmethod
    def extract_feature(image_path: str | Path) -> np.ndarray:
        path = Path(image_path)
        if not path.is_absolute():
            path = DATASET_ROOT / path

        with Image.open(path) as img:
            rgb = img.convert("RGB")
            low_res = rgb.resize((16, 16))
            arr = np.asarray(low_res, dtype=np.float32) / 255.0

        flattened = arr.reshape(-1)
        mean = arr.mean(axis=(0, 1))
        std = arr.std(axis=(0, 1))
        hist_parts = []
        for channel in range(3):
            hist, _ = np.histogram(arr[:, :, channel], bins=8, range=(0.0, 1.0))
            hist_parts.append(hist.astype(np.float32) / arr[:, :, channel].size)
        feature = np.concatenate([flattened, mean, std, *hist_parts]).astype(np.float32)
        return _normalize(feature)

    @classmethod
    def fit(
        cls,
        rows: list[dict[str, Any]],
        k: int = 3,
    ) -> "BaselineImageClassifierV1":
        train_rows = [row for row in rows if row["split"] == "train"]
        features = np.stack([cls.extract_feature(row["image_path"]) for row in train_rows])
        return cls(
            train_features=features,
            sample_ids=[str(row["sample_id"]) for row in train_rows],
            label_l1=[row["label_l1"] for row in train_rows],
            label_l2=[row["label_l2"] for row in train_rows],
            image_paths=[row["image_path"] for row in train_rows],
            k=k,
        )

    def save(self, model_dir: str | Path, metadata: dict[str, Any] | None = None) -> None:
        target_dir = Path(model_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            target_dir / "weights.npz",
            train_features=self.train_features,
            sample_ids=np.array(self.sample_ids, dtype=object),
            label_l1=np.array(self.label_l1, dtype=object),
            label_l2=np.array(self.label_l2, dtype=object),
            image_paths=np.array(self.image_paths, dtype=object),
            k=np.array([self.k], dtype=np.int32),
        )
        if metadata is not None:
            (target_dir / "metadata.json").write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    @classmethod
    def load(cls, model_dir: str | Path) -> "BaselineImageClassifierV1":
        payload = np.load(Path(model_dir) / "weights.npz", allow_pickle=True)
        return cls(
            train_features=payload["train_features"],
            sample_ids=[str(item) for item in payload["sample_ids"].tolist()],
            label_l1=[str(item) for item in payload["label_l1"].tolist()],
            label_l2=[str(item) for item in payload["label_l2"].tolist()],
            image_paths=[str(item) for item in payload["image_paths"].tolist()],
            k=int(payload["k"][0]),
        )

    def _predict_distribution(self, feature: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        similarities = self.train_features @ feature
        top_indices = np.argsort(similarities)[::-1][: self.k]
        top_scores = similarities[top_indices]
        weights = _softmax(top_scores)
        return top_indices, weights

    def _weighted_scores(
        self,
        labels: list[str],
        top_indices: np.ndarray,
        weights: np.ndarray,
        label_space: list[str],
    ) -> dict[str, float]:
        scores = {label: 0.0 for label in label_space}
        for idx, weight in zip(top_indices, weights):
            label = labels[int(idx)]
            if label in scores:
                scores[label] += float(weight)
        return scores

    def predict(self, image_path: str | Path, sample_id: str | None = None) -> dict[str, Any]:
        feature = self.extract_feature(image_path)
        top_indices, weights = self._predict_distribution(feature)
        l1_scores = self._weighted_scores(self.label_l1, top_indices, weights, L1_LABELS)
        l2_scores = self._weighted_scores(self.label_l2, top_indices, weights, L2_LABELS)
        predicted_l1 = max(l1_scores, key=l1_scores.get)
        predicted_l2 = max(l2_scores, key=l2_scores.get)
        neighbors = []
        for idx, weight in zip(top_indices, weights):
            neighbors.append(
                {
                    "sample_id": self.sample_ids[int(idx)],
                    "label_l1": self.label_l1[int(idx)],
                    "label_l2": self.label_l2[int(idx)],
                    "score": round(float(weight), 6),
                }
            )
        return {
            "sample_id": sample_id,
            "predicted_l1": predicted_l1,
            "predicted_l2": predicted_l2,
            "confidence_l1": round(float(l1_scores[predicted_l1]), 6),
            "confidence_l2": round(float(l2_scores[predicted_l2]), 6),
            "label_scores_l1": {key: round(value, 6) for key, value in l1_scores.items()},
            "label_scores_l2": {key: round(value, 6) for key, value in l2_scores.items()},
            "neighbors": neighbors,
        }

    def evaluate(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        metrics: dict[str, Any] = {
            "total": len(rows),
            "l1_accuracy": 0.0,
            "l2_accuracy": 0.0,
            "per_split": {},
        }
        if not rows:
            return metrics

        total_l1_correct = 0
        total_l2_correct = 0
        per_split_predictions: dict[str, list[dict[str, Any]]] = {}

        for row in rows:
            prediction = self.predict(row["image_path"], sample_id=str(row["sample_id"]))
            prediction["split"] = row["split"]
            prediction["true_l1"] = row["label_l1"]
            prediction["true_l2"] = row["label_l2"]
            per_split_predictions.setdefault(row["split"], []).append(prediction)
            total_l1_correct += int(prediction["predicted_l1"] == row["label_l1"])
            total_l2_correct += int(prediction["predicted_l2"] == row["label_l2"])

        metrics["l1_accuracy"] = round(total_l1_correct / len(rows), 6)
        metrics["l2_accuracy"] = round(total_l2_correct / len(rows), 6)

        for split_name, predictions in sorted(per_split_predictions.items()):
            l1_correct = sum(int(p["predicted_l1"] == p["true_l1"]) for p in predictions)
            l2_correct = sum(int(p["predicted_l2"] == p["true_l2"]) for p in predictions)
            metrics["per_split"][split_name] = {
                "count": len(predictions),
                "l1_accuracy": round(l1_correct / len(predictions), 6),
                "l2_accuracy": round(l2_correct / len(predictions), 6),
            }

        return metrics
