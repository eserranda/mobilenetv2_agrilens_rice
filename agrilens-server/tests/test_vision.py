"""
tests/test_vision.py
=====================
Unit tests for the Vision Module components:
    - VisionPreprocessor
    - ModelLoader
    - DiseasePredictor
"""
import io
from pathlib import Path

import pytest
import torch
from PIL import Image

from app.core.vision.preprocessing import VisionPreprocessor
from app.utils.exceptions import ImageValidationError
from app.utils.image_validator import (
    validate_extension,
    validate_image,
    validate_size,
)


# ------------------------------------------------------------------ Helpers
def _make_rgb_image(width: int = 300, height: int = 300) -> Image.Image:
    """Create a simple solid-color RGB PIL Image for testing."""
    return Image.new("RGB", (width, height), color=(100, 180, 80))


# ------------------------------------------------------------------ VisionPreprocessor Tests
class TestVisionPreprocessor:
    def test_output_tensor_shape(self):
        """Preprocessor should output a [1, 3, 224, 224] tensor."""
        preprocessor = VisionPreprocessor()
        image = _make_rgb_image()
        tensor = preprocessor.transform(image)

        assert isinstance(tensor, torch.Tensor)
        assert tensor.shape == (1, 3, 224, 224)

    def test_output_tensor_dtype_is_float32(self):
        """Preprocessor tensor should be float32."""
        preprocessor = VisionPreprocessor()
        tensor = preprocessor.transform(_make_rgb_image())
        assert tensor.dtype == torch.float32

    def test_handles_non_rgb_image(self):
        """Preprocessor should handle RGBA images by converting to RGB."""
        rgba_image = Image.new("RGBA", (200, 200), color=(100, 180, 80, 255))
        preprocessor = VisionPreprocessor()
        tensor = preprocessor.transform(rgba_image)
        assert tensor.shape == (1, 3, 224, 224)

    def test_normalization_changes_values(self):
        """After normalization, values should not all be in [0, 1]."""
        preprocessor = VisionPreprocessor()
        tensor = preprocessor.transform(_make_rgb_image())
        # ImageNet normalization shifts values outside [0, 1]
        assert tensor.min().item() < 0.0 or tensor.max().item() > 1.0


# ------------------------------------------------------------------ ImageValidator Tests
class TestImageValidator:
    def test_valid_extension_passes(self):
        validate_extension("leaf.jpg", ["jpg", "jpeg", "png"])

    def test_invalid_extension_raises(self):
        with pytest.raises(ImageValidationError):
            validate_extension("leaf.gif", ["jpg", "jpeg", "png"])

    def test_no_extension_raises(self):
        with pytest.raises(ImageValidationError):
            validate_extension("leafnodot", ["jpg"])

    def test_size_within_limit_passes(self):
        validate_size(b"x" * 100, max_bytes=1000)

    def test_size_over_limit_raises(self):
        with pytest.raises(ImageValidationError):
            validate_size(b"x" * 1001, max_bytes=1000)

    def test_valid_image_returns_pil_image(self):
        image = _make_rgb_image()
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        result = validate_image(
            content=buf.getvalue(),
            filename="leaf.png",
            allowed_extensions=["png"],
            max_bytes=10 * 1024 * 1024,
        )
        assert isinstance(result, Image.Image)

    def test_non_image_bytes_raises(self):
        with pytest.raises(ImageValidationError):
            validate_image(
                content=b"not an image at all",
                filename="leaf.jpg",
                allowed_extensions=["jpg"],
                max_bytes=10 * 1024 * 1024,
            )
