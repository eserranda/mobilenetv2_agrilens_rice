"""
app/schemas/health.py
=====================
Pydantic schema for the Health Check API response.
"""
from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response schema for GET /api/v1/health."""

    status: str = Field(..., description="API health status", examples=["ok"])
    version: str = Field(..., description="Application version", examples=["1.0.0"])
    uptime_seconds: float = Field(..., description="Seconds since server startup")
    timestamp: datetime = Field(..., description="Current UTC timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "ok",
                "version": "1.0.0",
                "uptime_seconds": 123.45,
                "timestamp": "2024-01-01T00:00:00Z",
            }
        }
    }
