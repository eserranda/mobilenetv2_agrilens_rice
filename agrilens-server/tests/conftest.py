"""
tests/conftest.py
==================
Shared pytest fixtures for API integration tests.
"""
import os

# Clean up SQLite test database file to enforce schema updates in tests
db_path = os.path.join("db_data", "rice_disease.db")
if os.path.exists(db_path):
    try:
        os.remove(db_path)
    except Exception:
        pass

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.core.security import get_current_user, get_admin_user
from app.models.user import User


async def mock_get_current_user():
    """Mock standard/admin user for test suite."""
    return User(id=999, username="test_admin", role="admin")


async def mock_get_admin_user():
    """Mock admin user for test suite."""
    return User(id=999, username="test_admin", role="admin")


@pytest.fixture
async def client():
    """Fixture that yields an AsyncClient with the application lifespan executed."""
    # Override authentication dependencies for testing
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_admin_user] = mock_get_admin_user

    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

    # Clean up overrides after test completes
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_image_guardrail():
    """Globally mock the OpenAI guardrail check during tests to always return True."""
    from unittest.mock import patch
    with patch("app.core.llm.engine.LLMEngine.validate_rice_plant_image", return_value={"is_rice_plant": True, "reason": "Mocked validation"}):
        yield
