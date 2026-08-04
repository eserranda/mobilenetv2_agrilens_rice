"""
app/api/endpoints/history.py
================================
History endpoints with Role-Based Access Control.
"""
import logging
import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.history import DetectionHistory
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.history import HistoryDetailResponse, HistoryListResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/history",
    response_model=HistoryListResponse,
    summary="Get Detection History",
    description="Retrieve a paginated list of past rice leaf disease detections. Users only see their own logs; admins see all.",
    tags=["History"],
)
async def get_history(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(default=10, ge=1, le=100, description="Number of items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HistoryListResponse:
    """Return a paginated list of past detections, filtered by user ownership/role."""
    logger.info("History list requested | page=%d | size=%d | user=%s", page, size, current_user.username)

    # 1. Base queries depending on role
    if current_user.role == "admin":
        total_query = select(func.count()).select_from(DetectionHistory)
        items_query = (
            select(DetectionHistory)
            .order_by(DetectionHistory.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
    else:
        total_query = select(func.count()).select_from(DetectionHistory).where(
            DetectionHistory.user_id == current_user.id
        )
        items_query = (
            select(DetectionHistory)
            .where(DetectionHistory.user_id == current_user.id)
            .order_by(DetectionHistory.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )

    # 2. Execute count query
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0

    # 3. Execute items query
    items_result = await db.execute(items_query)
    items = items_result.scalars().all()

    return HistoryListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
    )


@router.get(
    "/history/{id}",
    response_model=HistoryDetailResponse,
    summary="Get History Detail",
    description="Retrieve full details (including LLM pathologist reasoning) of a past diagnosis.",
    tags=["History"],
)
async def get_history_detail(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HistoryDetailResponse:
    """Return details of a specific history entry if owner or admin."""
    logger.info("History detail requested | id=%s | user=%s", id, current_user.username)

    query = select(DetectionHistory).where(DetectionHistory.id == id)
    result = await db.execute(query)
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=404,
            detail=f"History record with ID '{id}' not found.",
        )

    # Access control: Must be owner or admin
    if current_user.role != "admin" and entry.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Akses ditolak. Anda tidak memiliki akses ke riwayat diagnosa ini.",
        )

    return entry


@router.delete(
    "/history/{id}",
    status_code=204,
    summary="Delete History Record",
    description="Delete a past rice leaf disease detection record by ID and remove its associated image file from disk.",
    tags=["History"],
)
async def delete_history(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a history entry and its associated file if owner or admin."""
    logger.info("Delete history entry requested | id=%s | user=%s", id, current_user.username)

    # 1. Fetch the entry first to find the image path
    query = select(DetectionHistory).where(DetectionHistory.id == id)
    result = await db.execute(query)
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=404,
            detail=f"History record with ID '{id}' not found.",
        )

    # Access control: Must be owner or admin to delete
    if current_user.role != "admin" and entry.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Akses ditolak. Anda tidak memiliki izin untuk menghapus riwayat diagnosa ini.",
        )

    # 2. Attempt to delete the associated image file from disk
    image_url_path = entry.image_path
    if image_url_path.startswith("/static/uploads/"):
        filename = image_url_path.replace("/static/uploads/", "")
        file_path = os.path.join("uploads", filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info("Deleted associated image file: %s", file_path)
            except Exception as exc:
                logger.error("Failed to delete image file '%s' from disk: %s", file_path, str(exc))

    # 3. Delete from the database
    await db.delete(entry)
    await db.commit()

    return None
