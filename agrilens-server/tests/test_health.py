"""
tests/test_health.py
=====================
Tests for the GET /api/v1/health endpoint.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_status_ok(client: AsyncClient):
    """Health endpoint should return status 200 with 'ok' status."""
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_health_response_schema(client: AsyncClient):
    """Health endpoint response should contain all required fields."""
    response = await client.get("/api/v1/health")

    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "uptime_seconds" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_uptime_is_positive(client: AsyncClient):
    """Uptime should be a non-negative float."""
    response = await client.get("/api/v1/health")

    data = response.json()
    assert isinstance(data["uptime_seconds"], float)
    assert data["uptime_seconds"] >= 0
