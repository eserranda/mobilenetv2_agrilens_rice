"""
app/api/router.py
==================
API main router.
Combines all endpoint routers under a single prefix.
"""
from fastapi import APIRouter

from app.api.endpoints import detection, health, history, setting, auth, users

router = APIRouter()

router.include_router(health.router)
router.include_router(detection.router)
router.include_router(history.router)
router.include_router(setting.router)
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
