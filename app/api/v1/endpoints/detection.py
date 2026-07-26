"""
app/api/v1/endpoints/detection.py
====================================
Disease Detection endpoint.

Responsibilities:
    - Accept image file upload via multipart/form-data
    - Validate uploaded file
    - Delegate inference to DiseasePredictor
    - Return structured JSON response

Rules per PRD Section 9:
    - Endpoint contains NO AI logic
    - Endpoint only handles HTTP concerns (validate, delegate, respond)
"""
import logging

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import JSONResponse

from app.core.vision.predictor import DiseasePredictor
from app.schemas.detection import DetectionResponse
from app.utils.exceptions import ImageValidationError, PredictionError
from app.utils.image_validator import validate_image

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/detect",
    response_model=DetectionResponse,
    summary="Rice Disease Detection",
    description=(
        "Upload an image of a rice leaf to detect the presence of disease. "
        "Returns the predicted disease label, confidence score, and inference time."
    ),
    tags=["Detection"],
)
async def detect_disease(
    request: Request,
    file: UploadFile = File(..., description="Rice leaf image (JPG, PNG, WebP)"),
) -> DetectionResponse:
    """Accept an uploaded rice leaf image and return a disease prediction.

    Args:
        request: FastAPI Request (used to access app.state predictor & settings).
        file: Uploaded image file via multipart/form-data.

    Returns:
        DetectionResponse with disease label, confidence, and inference time.

    Raises:
        422: If the uploaded file fails validation.
        500: If inference fails unexpectedly.
    """
    settings = request.app.state.settings
    predictor: DiseasePredictor = request.app.state.predictor

    # --- Read file bytes ---
    content = await file.read()
    filename = file.filename or "upload"

    logger.info("Detection request received | filename=%s | size=%d bytes", filename, len(content))

    # --- Validate image ---
    try:
        image = validate_image(
            content=content,
            filename=filename,
            allowed_extensions=settings.allowed_extensions_list,
            max_bytes=settings.max_upload_size_bytes,
        )
    except ImageValidationError as exc:
        logger.warning("Image validation failed: %s", exc.message)
        return JSONResponse(
            status_code=422,
            content={"detail": exc.message},
        )

    # --- Run inference ---
    try:
        result = predictor.predict(image)
    except PredictionError as exc:
        logger.error("Prediction failed: %s", exc.message)
        return JSONResponse(
            status_code=500,
            content={"detail": "Inference failed. Please try again."},
        )

    # --- Run Chain-of-Thought Diagnosis (Phase 2) ---
    thinking = None
    explanation = None
    recommendation = None
    severity = None

    if settings.openai_api_key:
        try:
            explainer = request.app.state.explainer
            diag = explainer.explain(disease=result.disease, confidence=result.confidence)
            thinking = diag.thinking
            explanation = diag.explanation
            recommendation = diag.recommendation
            severity = diag.severity
        except Exception as exc:
            logger.error("Failed to generate LLM explanation: %s", str(exc))
            # Graceful fallback: we still return the prediction even if LLM fails
            thinking = f"LLM error: {str(exc)}"
            explanation = "Diagnosis explanation is temporarily unavailable."
            recommendation = "Please consult an agricultural expert or try again later."
            severity = "unknown"
    else:
        logger.warning("OPENAI_API_KEY is not configured. LLM explanation is skipped.")

    return DetectionResponse(
        disease=result.disease,
        confidence=result.confidence,
        inference_time_ms=result.inference_time_ms,
        thinking=thinking,
        explanation=explanation,
        recommendation=recommendation,
        severity=severity,
        metadata=request.app.state.artifacts.metadata,
    )
