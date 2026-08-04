"""
app/api/endpoints/auth.py
==========================
Endpoints for user registration and login.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter()


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nama pengguna unik")
    password: str = Field(..., min_length=4, max_length=100, description="Kata sandi")


class UserLogin(BaseModel):
    username: str = Field(..., description="Nama pengguna")
    password: str = Field(..., description="Kata sandi")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Daftar Pengguna Baru",
)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check if username already exists
    query = select(User).where(User.username == payload.username)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nama pengguna sudah terdaftar.",
        )
        
    # Check if user table is empty to assign admin role to first user
    count_query = select(User)
    count_result = await db.execute(count_query)
    is_first_user = len(count_result.scalars().all()) == 0
    
    # Determine role: admin if first user or starts with "admin"
    role = "user"
    if is_first_user or payload.username.lower().startswith("admin"):
        role = "admin"
        
    # Create new user
    new_user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role=role,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Masuk Pengguna",
)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.username == payload.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nama pengguna atau kata sandi salah.",
        )
        
    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        username=user.username,
        role=user.role,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Ambil Profil Pengguna Saat Ini",
)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
