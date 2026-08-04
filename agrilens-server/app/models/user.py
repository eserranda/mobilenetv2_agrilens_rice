"""
app/models/user.py
===================
SQLAlchemy model for storing application users.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    """Model mapping the users table."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(20), default="user", nullable=False)  # "user" or "admin"
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
