"""
app/models/setting.py
======================
SQLAlchemy model for storing application settings.
"""
from sqlalchemy import Column, String
from app.db.base import Base


class AppSetting(Base):
    """Model mapping the application settings table."""
    __tablename__ = "app_settings"

    key = Column(String(100), primary_key=True)
    value = Column(String(500), nullable=False)
