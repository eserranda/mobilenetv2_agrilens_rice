"""
app/api/endpoints/users.py
===========================
Endpoints for admin-level user management.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.user import User
from app.core.security import get_admin_user
from app.api.endpoints.auth import UserResponse

router = APIRouter()


@router.get(
    "",
    response_model=List[UserResponse],
    summary="Daftar Semua Pengguna (Khusus Admin)",
)
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Retrieve all users in the system. Requires Admin authorization."""
    query = select(User).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()
    return users


@router.delete(
    "/{id}",
    status_code=204,
    summary="Hapus Pengguna (Khusus Admin)",
)
async def delete_user(
    id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Delete a user from the system by ID. Admin only."""
    if id == admin_user.id:
        raise HTTPException(
            status_code=400,
            detail="Anda tidak dapat menghapus akun Anda sendiri.",
        )

    query = select(User).where(User.id == id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"Pengguna dengan ID '{id}' tidak ditemukan.",
        )

    # Disassociate user from their detection history instead of deleting the history records
    from app.models.history import DetectionHistory
    from sqlalchemy import update
    update_stmt = update(DetectionHistory).where(DetectionHistory.user_id == id).values(user_id=None)
    await db.execute(update_stmt)

    await db.delete(user)
    await db.commit()
    return None
