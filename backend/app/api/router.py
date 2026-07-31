"""
app/api/router.py
==================
API main router.
Combines all endpoint routers under a single prefix.
"""
from fastapi import APIRouter

from app.api.endpoints import detection, health, history, setting

router = APIRouter()

router.include_router(health.router)
router.include_router(detection.router)
router.include_router(history.router)
router.include_router(setting.router)
