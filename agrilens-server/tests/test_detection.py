"""
tests/test_detection.py
========================
Tests for the POST /api/v1/detect endpoint.
"""
import io

import pytest
from httpx import AsyncClient
from PIL import Image


def _create_test_image_bytes(width: int = 224, height: int = 224) -> bytes:
    """Create a synthetic RGB image as PNG bytes for testing."""
    img = Image.new("RGB", (width, height), color=(34, 139, 34))  # Forest green
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_detect_returns_200_with_valid_image(client: AsyncClient):
    """Detection endpoint should return 200 for a valid PNG image."""
    image_bytes = _create_test_image_bytes()
    response = await client.post(
        "/api/v1/detect",
        files={"file": ("leaf.png", image_bytes, "image/png")},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_detect_response_schema(client: AsyncClient):
    """Detection response must contain disease, confidence, inference_time_ms."""
    image_bytes = _create_test_image_bytes()
    response = await client.post(
        "/api/v1/detect",
        files={"file": ("leaf.png", image_bytes, "image/png")},
    )

    data = response.json()
    assert "disease" in data
    assert "confidence" in data
    assert "inference_time_ms" in data
    assert isinstance(data["disease"], str)
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["inference_time_ms"] >= 0


@pytest.mark.asyncio
async def test_detect_rejects_invalid_extension(client: AsyncClient):
    """Detection endpoint should return 422 for disallowed file extension."""
    image_bytes = _create_test_image_bytes()
    response = await client.post(
        "/api/v1/detect",
        files={"file": ("leaf.gif", image_bytes, "image/gif")},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_detect_rejects_non_image_bytes(client: AsyncClient):
    """Detection endpoint should return 422 for non-image binary data."""
    fake_bytes = b"this is not an image"
    response = await client.post(
        "/api/v1/detect",
        files={"file": ("leaf.jpg", fake_bytes, "image/jpeg")},
    )

    assert response.status_code == 422
