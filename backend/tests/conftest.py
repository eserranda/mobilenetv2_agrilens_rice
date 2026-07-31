"""
tests/conftest.py
==================
Shared pytest fixtures for API integration tests.
"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    """Fixture that yields an AsyncClient with the application lifespan executed."""
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac


@pytest.fixture(autouse=True)
def mock_image_guardrail():
    """Globally mock the OpenAI guardrail check during tests to always return True."""
    from unittest.mock import patch
    with patch("app.core.llm.engine.LLMEngine.validate_rice_plant_image", return_value={"is_rice_plant": True, "reason": "Mocked validation"}):
        yield
