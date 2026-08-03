"""
app/core/vision/preprocessing.py
==================================
Responsible for transforming a raw PIL Image into a normalized
tensor ready for MobileNetV2 inference.

Responsibilities:
    - Resize image to model input size (224x224)
    - Convert to RGB PIL Image
    - Apply ImageNet normalization
    - Convert to 4D batch tensor [1, C, H, W]

This module is framework-agnostic. It has no knowledge of FastAPI,
HTTP, or LLM modules.
"""
import logging

import torch
from PIL import Image
from torchvision import transforms

from app.utils.exceptions import PredictionError

logger = logging.getLogger(__name__)

# ImageNet normalization constants used during MobileNetV2 pretraining
_IMAGENET_MEAN = [0.485, 0.456, 0.406]
_IMAGENET_STD = [0.229, 0.224, 0.225]
_MODEL_INPUT_SIZE = 224


class VisionPreprocessor:
    """Transforms a PIL Image into a model-ready normalized batch tensor.

    The preprocessing pipeline mirrors the validation/inference transforms
    used during model training in Google Colab.

    Usage:
        preprocessor = VisionPreprocessor()
        tensor = preprocessor.transform(pil_image)  # shape: [1, 3, 224, 224]
    """

    def __init__(self, input_size: int = _MODEL_INPUT_SIZE) -> None:
        self._input_size = input_size
        self._transform = self._build_transform()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def transform(self, image: Image.Image) -> torch.Tensor:
        """Apply the full preprocessing pipeline to a PIL Image.

        Args:
            image: A PIL Image (any mode; will be converted to RGB internally).

        Returns:
            A 4D float tensor of shape [1, 3, H, W] on CPU.

        Raises:
            PredictionError: If preprocessing encounters an unexpected error.
        """
        try:
            if image.mode != "RGB":
                image = image.convert("RGB")

            tensor: torch.Tensor = self._transform(image)       # [3, H, W]
            batch_tensor = tensor.unsqueeze(0)                  # [1, 3, H, W]
            logger.debug("Preprocessed tensor shape: %s", batch_tensor.shape)
            return batch_tensor

        except Exception as exc:
            raise PredictionError(
                f"Image preprocessing failed: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Private Helpers
    # ------------------------------------------------------------------

    def _build_transform(self) -> transforms.Compose:
        """Build the torchvision transform pipeline.

        Pipeline:
            1. Resize to (input_size, input_size)
            2. CenterCrop (no-op for square images, kept for robustness)
            3. ToTensor  -> [0.0, 1.0] float32
            4. Normalize with ImageNet mean & std

        Returns:
            A composed torchvision transform.
        """
        return transforms.Compose([
            transforms.Resize((self._input_size, self._input_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=_IMAGENET_MEAN, std=_IMAGENET_STD),
        ])
