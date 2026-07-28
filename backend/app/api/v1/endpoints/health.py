"""
app/api/v1/endpoints/health.py
================================
Health Check endpoint.

Responsibilities:
    - Receive GET /api/v1/health request
    - Return application status, version, and uptime

Rules per PRD Section 9:
    - Endpoint contains NO AI logic
    - Endpoint only handles HTTP concerns
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Request

from app.schemas.health import HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns the current status, version, and uptime of the API.",
    tags=["Health"],
)
async def health_check(request: Request) -> HealthResponse:
    """Return the current health status of the API.

    The uptime is tracked via the `startup_time` stored in `app.state`
    which is set during the FastAPI lifespan event in `main.py`.

    Args:
        request: FastAPI Request (used to access app.state).

    Returns:
        HealthResponse with status, version, uptime, and timestamp.
    """
    startup_time: datetime = request.app.state.startup_time
    uptime = (datetime.now(timezone.utc) - startup_time).total_seconds()

    logger.debug("Health check requested | uptime=%.2fs", uptime)

    return HealthResponse(
        status="ok",
        version=request.app.state.settings.app_version,
        uptime_seconds=round(uptime, 3),
        timestamp=datetime.now(timezone.utc),
    )
