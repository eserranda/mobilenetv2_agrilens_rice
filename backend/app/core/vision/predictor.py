"""
app/core/vision/predictor.py
=============================
Orchestrates the complete vision inference pipeline:
    1. Run preprocessing via VisionPreprocessor
    2. Move tensor to correct device
    3. Run forward pass through MobileNetV2
    4. Calculate Softmax confidence scores
    5. Return predicted disease label and confidence

This module is framework-agnostic. It has no knowledge of FastAPI,
HTTP, or LLM modules. The Predictor deliberately does NOT know that
any LLM module exists.
"""
import logging
import time
from dataclasses import dataclass
from typing import Dict

import torch
import torch.nn.functional as F
from PIL import Image

from app.core.vision.loader import ModelArtifacts
from app.core.vision.preprocessing import VisionPreprocessor
from app.utils.exceptions import PredictionError

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """Structured output from the DiseasePredictor."""

    disease: str
    confidence: float
    inference_time_ms: float
    all_probabilities: Dict[str, float]


class DiseasePredictor:
    """Runs the full inference pipeline on a PIL Image.

    The predictor is initialized once at application startup and reused
    across all requests to avoid repeated model loading overhead.

    Usage:
        predictor = DiseasePredictor(artifacts)
        result = predictor.predict(pil_image)
    """

    def __init__(self, artifacts: ModelArtifacts) -> None:
        self._model = artifacts.model
        self._labels = artifacts.labels
        self._device = artifacts.device
        self._preprocessor = VisionPreprocessor()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict(self, image: Image.Image) -> PredictionResult:
        """Run inference on a PIL Image and return a structured prediction.

        Args:
            image: A PIL Image of a rice leaf (any mode; will be normalized).

        Returns:
            PredictionResult containing the top-1 predicted disease label,
            its confidence score, inference time, and all class probabilities.

        Raises:
            PredictionError: If preprocessing or inference fails.
        """
        start_time = time.perf_counter()

        try:
            # Step 1: Preprocess
            tensor = self._preprocessor.transform(image)      # [1, 3, 224, 224]
            tensor = tensor.to(self._device)

            # Step 2: Inference
            with torch.no_grad():
                logits = self._model(tensor)                   # [1, num_classes]

            # Step 3: Softmax confidence scores
            probabilities = F.softmax(logits, dim=1).squeeze(0)  # [num_classes]

            # Step 4: Top-1 prediction
            top_idx: int = probabilities.argmax().item()
            confidence: float = probabilities[top_idx].item()
            disease: str = self._labels[top_idx]

            inference_time_ms = (time.perf_counter() - start_time) * 1000

            # Build full probability map for transparency
            all_probs = {
                self._labels[i]: float(probabilities[i])
                for i in range(len(self._labels))
            }

            logger.info(
                "Prediction: %s | confidence=%.4f | time=%.1f ms",
                disease,
                confidence,
                inference_time_ms,
            )

            return PredictionResult(
                disease=disease,
                confidence=round(confidence, 6),
                inference_time_ms=round(inference_time_ms, 2),
                all_probabilities=all_probs,
            )

        except PredictionError:
            raise
        except Exception as exc:
            raise PredictionError(
                f"Inference failed unexpectedly: {exc}"
            ) from exc
