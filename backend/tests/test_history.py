"""
tests/test_history.py
======================
Integration tests for database persistence and Detection History API endpoints.
"""
import io
import pytest
from httpx import AsyncClient
from PIL import Image

from app.models.history import DetectionHistory
from app.db.session import async_session_maker


def _create_test_image_bytes(width: int = 224, height: int = 224) -> bytes:
    """Create a synthetic RGB image as PNG bytes for testing."""
    img = Image.new("RGB", (width, height), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_detect_saves_to_database_and_returns_predictions(client: AsyncClient):
    """POST /detect should classify the image and save a record to the database."""
    image_bytes = _create_test_image_bytes()

    # 1. Trigger detection endpoint
    response = await client.post(
        "/api/v1/detect",
        files={"file": ("test_leaf_db.png", image_bytes, "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "disease" in data
    assert "confidence" in data

    # 2. Check that database has at least one entry corresponding to this detection
    async with async_session_maker() as session:
        from sqlalchemy import select
        stmt = select(DetectionHistory).order_by(DetectionHistory.created_at.desc())
        result = await session.execute(stmt)
        entry = result.scalars().first()

        assert entry is not None
        assert entry.filename == "test_leaf_db.png"
        assert entry.disease == data["disease"]
        assert entry.confidence == data["confidence"]
        assert entry.image_path.startswith("/static/uploads/")


@pytest.mark.asyncio
async def test_get_history_list(client: AsyncClient):
    """GET /history should return paginated list of detection logs."""
    response = await client.get("/api/v1/history?page=1&size=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_get_history_detail_and_not_found(client: AsyncClient):
    """GET /history/{id} should return details of a record, and 404 for invalid ID."""
    # 1. Check 404 for non-existent UUID
    response = await client.get("/api/v1/history/non-existent-uuid")
    assert response.status_code == 404
    assert response.json()["detail"] == "History record with ID 'non-existent-uuid' not found."

    # 2. Fetch list to get a valid ID (from the post call in the first test)
    list_response = await client.get("/api/v1/history?page=1&size=1")
    assert list_response.status_code == 200
    list_data = list_response.json()

    if list_data["items"]:
        valid_id = list_data["items"][0]["id"]

        # Query details for valid ID
        detail_response = await client.get(f"/api/v1/history/{valid_id}")
        assert detail_response.status_code == 200
        detail_data = detail_response.json()
        assert detail_data["id"] == valid_id
        assert "filename" in detail_data
        assert "disease" in detail_data
        assert "image_path" in detail_data


@pytest.mark.asyncio
async def test_delete_history_record(client: AsyncClient):
    """DELETE /history/{id} should delete the record from database and associated image from disk."""
    # 1. Fetch list to get a valid ID to delete
    list_response = await client.get("/api/v1/history?page=1&size=1")
    assert list_response.status_code == 200
    list_data = list_response.json()

    assert list_data["items"], "Should have at least one history entry to delete"
    valid_id = list_data["items"][0]["id"]

    # 2. Call DELETE endpoint
    delete_response = await client.delete(f"/api/v1/history/{valid_id}")
    assert delete_response.status_code == 204

    # 3. Verify it is deleted (GET returns 404)
    get_response = await client.get(f"/api/v1/history/{valid_id}")
    assert get_response.status_code == 404
