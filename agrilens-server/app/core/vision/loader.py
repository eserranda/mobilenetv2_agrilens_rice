"""
app/core/vision/loader.py
==========================
Responsible for loading all model artifacts required for inference:
    - MobileNetV2 model architecture + trained weights (.pth)
    - Label mapping (labels.json)
    - Model metadata (metadata.json)
    - Device selection (CUDA / CPU)

This module is framework-agnostic. It has no knowledge of FastAPI,
HTTP, or LLM modules.
"""
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import torch
import torch.nn as nn
from torchvision import models

from app.utils.exceptions import ModelLoadError

logger = logging.getLogger(__name__)


@dataclass
class ModelArtifacts:
    """Container for all loaded model artifacts."""

    model: nn.Module
    labels: Dict[int, str]          # {0: "Brown Spot", 1: "Healthy", ...}
    metadata: Dict                  # Raw metadata dict from metadata.json
    device: torch.device
    num_classes: int = field(init=False)

    def __post_init__(self) -> None:
        self.num_classes = len(self.labels)


class ModelLoader:
    """Loads MobileNetV2 model weights, labels, and metadata from disk.

    Usage:
        loader = ModelLoader(model_path, labels_path, metadata_path)
        artifacts = loader.load()
    """

    def __init__(
        self,
        model_path: Path,
        labels_path: Path,
        metadata_path: Path,
    ) -> None:
        self._model_path = Path(model_path)
        self._labels_path = Path(labels_path)
        self._metadata_path = Path(metadata_path)
        self._device = self._select_device()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self) -> ModelArtifacts:
        """Load all artifacts and return a ready-to-use ModelArtifacts object.

        Returns:
            ModelArtifacts with loaded model, labels, metadata, and device.

        Raises:
            ModelLoadError: If any artifact is missing or incompatible.
        """
        labels = self._load_labels()
        metadata = self._load_metadata()
        model = self._load_model(num_classes=len(labels))

        logger.info(
            "Model loaded successfully | device=%s | classes=%d",
            self._device,
            len(labels),
        )
        return ModelArtifacts(
            model=model,
            labels=labels,
            metadata=metadata,
            device=self._device,
        )

    # ------------------------------------------------------------------
    # Private Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _select_device() -> torch.device:
        """Select CUDA if available, otherwise fall back to CPU."""
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info("Using device: %s", device)
        return device

    def _load_labels(self) -> Dict[int, str]:
        """Load and parse labels.json into a {int -> str} mapping.

        The JSON file is expected to be a list of label strings ordered
        by class index, e.g.:
            ["Brown Spot", "Healthy", "Hispa", "Leaf Blast"]

        Returns:
            A dict mapping integer class index to label string.

        Raises:
            ModelLoadError: If the file is missing or malformed.
        """
        if not self._labels_path.exists():
            raise ModelLoadError(
                f"Labels file not found: {self._labels_path}. "
                "Please ensure labels.json is present in the models/ directory."
            )
        try:
            with open(self._labels_path, "r", encoding="utf-8") as f:
                raw: List[str] = json.load(f)
            return {idx: label for idx, label in enumerate(raw)}
        except (json.JSONDecodeError, TypeError) as exc:
            raise ModelLoadError(
                f"Failed to parse labels.json: {exc}"
            ) from exc

    def _load_metadata(self) -> Dict:
        """Load metadata.json as a raw dictionary.

        Returns:
            A dict with model metadata fields.

        Raises:
            ModelLoadError: If the file is missing or malformed.
        """
        if not self._metadata_path.exists():
            raise ModelLoadError(
                f"Metadata file not found: {self._metadata_path}. "
                "Please ensure metadata.json is present in the models/ directory."
            )
        try:
            with open(self._metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, TypeError) as exc:
            raise ModelLoadError(
                f"Failed to parse metadata.json: {exc}"
            ) from exc

    def _load_model(self, num_classes: int) -> nn.Module:
        """Build MobileNetV2 architecture with a custom classifier head,
        then load the trained weights from the .pth file.

        Args:
            num_classes: Number of output classes matching the label count.

        Returns:
            A PyTorch model in eval() mode on the selected device.

        Raises:
            ModelLoadError: If the weights file is missing or incompatible.
        """
        if not self._model_path.exists():
            raise ModelLoadError(
                f"Model weights not found: {self._model_path}. "
                "Please run scripts/generate_sample_model.py or copy your "
                "trained .pth file into the models/ directory."
            )

        try:
            # Build MobileNetV2 with the same head used during training
            model = models.mobilenet_v2(weights=None)
            in_features = model.classifier[1].in_features
            model.classifier[1] = nn.Linear(in_features, num_classes)

            # Load trained state dict
            state_dict = torch.load(
                self._model_path,
                map_location=self._device,
                weights_only=True,
            )
            model.load_state_dict(state_dict)
            model.to(self._device)
            model.eval()
            return model

        except RuntimeError as exc:
            raise ModelLoadError(
                f"Failed to load model weights from {self._model_path}: {exc}"
            ) from exc
