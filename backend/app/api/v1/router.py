"""
app/api/v1/router.py
=====================
API v1 main router.
Combines all v1 endpoint routers under a single prefix.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import detection, health, history

router = APIRouter()

router.include_router(health.router)
router.include_router(detection.router)
router.include_router(history.router)
