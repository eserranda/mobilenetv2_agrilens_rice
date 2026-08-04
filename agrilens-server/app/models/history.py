"""
app/models/history.py
======================
SQLAlchemy model for storing detection history logs.
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base


class DetectionHistory(Base):
    """Model mapping the detection history table."""
    __tablename__ = "detection_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    image_path = Column(String(500), nullable=False)
    disease = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    inference_time_ms = Column(Float, nullable=False)
    thinking = Column(String(2000), nullable=True)
    explanation = Column(String(1000), nullable=True)
    recommendation = Column(String(1000), nullable=True)
    severity = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", backref="histories")
