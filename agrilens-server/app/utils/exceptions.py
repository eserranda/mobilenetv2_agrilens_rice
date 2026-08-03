"""
app/utils/exceptions.py
=======================
Custom domain exceptions for the Rice Disease API.
These exceptions are framework-agnostic and should never
import FastAPI or any HTTP-related modules.
"""


class RiceDiseaseAPIError(Exception):
    """Base exception for all Rice Disease API errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ImageValidationError(RiceDiseaseAPIError):
    """Raised when an uploaded image fails validation checks.

    Examples:
        - Unsupported file extension
        - File size exceeds limit
        - File is not a valid image (corrupted or wrong format)
    """


class ModelLoadError(RiceDiseaseAPIError):
    """Raised when the AI model or its associated artifacts fail to load.

    Examples:
        - Model weights file (.pth) not found
        - labels.json not found or malformed
        - Incompatible model architecture
    """


class PredictionError(RiceDiseaseAPIError):
    """Raised when inference fails during the prediction pipeline.

    Examples:
        - Preprocessing returns an unexpected tensor shape
        - Model inference throws a runtime error
    """
