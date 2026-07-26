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
