"""
app/utils/image_validator.py
=============================
Provides utility functions to validate uploaded image files
before they enter the preprocessing pipeline.

Responsibilities:
    - Validate file extension against the allowed list
    - Validate file size against the max upload limit
    - Validate that the bytes represent a real, non-corrupted image
"""
from io import BytesIO
from typing import List

from PIL import Image, UnidentifiedImageError

from app.utils.exceptions import ImageValidationError


def validate_extension(filename: str, allowed_extensions: List[str]) -> None:
    """Raise ImageValidationError if the filename extension is not allowed.

    Args:
        filename: The original filename from the upload (e.g. "leaf.jpg").
        allowed_extensions: A list of permitted lowercase extensions
                            (e.g. ["jpg", "jpeg", "png", "webp"]).

    Raises:
        ImageValidationError: If the file extension is not in the allowed list.
    """
    if not filename or "." not in filename:
        raise ImageValidationError(
            "Invalid filename. File must have a valid extension."
        )

    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed_extensions:
        allowed_str = ", ".join(allowed_extensions)
        raise ImageValidationError(
            f"File extension '.{ext}' is not allowed. "
            f"Supported extensions: {allowed_str}."
        )


def validate_size(content: bytes, max_bytes: int) -> None:
    """Raise ImageValidationError if the file size exceeds the limit.

    Args:
        content: Raw file bytes.
        max_bytes: Maximum allowed byte size.

    Raises:
        ImageValidationError: If the file size exceeds max_bytes.
    """
    size = len(content)
    if size > max_bytes:
        max_mb = max_bytes / (1024 * 1024)
        actual_mb = size / (1024 * 1024)
        raise ImageValidationError(
            f"File size {actual_mb:.2f} MB exceeds the maximum allowed "
            f"size of {max_mb:.0f} MB."
        )


def validate_image_content(content: bytes) -> Image.Image:
    """Attempt to open the bytes as a PIL Image to verify integrity.

    Args:
        content: Raw file bytes representing the image.

    Returns:
        A PIL Image object in RGB mode.

    Raises:
        ImageValidationError: If bytes cannot be decoded as a valid image.
    """
    try:
        image = Image.open(BytesIO(content)).convert("RGB")
        image.verify()  # Check for file corruption
    except (UnidentifiedImageError, Exception):
        # Re-open after verify() since verify() exhausts the stream
        try:
            image = Image.open(BytesIO(content)).convert("RGB")
        except Exception as exc:
            raise ImageValidationError(
                "Uploaded file is not a valid or supported image. "
                "Please upload a clear photo of a rice leaf."
            ) from exc

    return image


def validate_image(
    content: bytes,
    filename: str,
    allowed_extensions: List[str],
    max_bytes: int,
) -> Image.Image:
    """Run all image validations and return the loaded PIL Image.

    This is the main entry point for image validation. It chains
    all sub-validators in the correct order.

    Args:
        content: Raw file bytes from the upload.
        filename: Original filename (used for extension check).
        allowed_extensions: List of permitted lowercase file extensions.
        max_bytes: Maximum allowed file size in bytes.

    Returns:
        A valid PIL Image in RGB mode.

    Raises:
        ImageValidationError: On any validation failure.
    """
    validate_extension(filename, allowed_extensions)
    validate_size(content, max_bytes)
    image = validate_image_content(content)
    return image
