"""
app/api/endpoints/setting.py
=============================
App Settings endpoints.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.models.setting import AppSetting

logger = logging.getLogger(__name__)
router = APIRouter()


class SettingUpdate(BaseModel):
    value: str


class SettingResponse(BaseModel):
    key: str
    value: str


@router.get(
    "/settings/{key}",
    response_model=SettingResponse,
    summary="Get App Setting",
    tags=["Settings"],
)
async def get_setting(key: str, db: AsyncSession = Depends(get_db)):
    """Retrieve the value of an application setting by key."""
    q = select(AppSetting).where(AppSetting.key == key)
    res = await db.execute(q)
    setting = res.scalar_one_or_none()

    # If the key is 'openai_guardrail' and not set, return 'true' as default
    if not setting:
        if key == "openai_guardrail":
            return {"key": key, "value": "true"}
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found.")

    return setting


@router.put(
    "/settings/{key}",
    response_model=SettingResponse,
    summary="Update App Setting",
    tags=["Settings"],
)
async def update_setting(key: str, body: SettingUpdate, db: AsyncSession = Depends(get_db)):
    """Create or update an application setting by key."""
    logger.info("Setting update requested | key=%s | value=%s", key, body.value)

    q = select(AppSetting).where(AppSetting.key == key)
    res = await db.execute(q)
    setting = res.scalar_one_or_none()

    if not setting:
        setting = AppSetting(key=key, value=body.value)
        db.add(setting)
    else:
        setting.value = body.value

    await db.commit()
    await db.refresh(setting)
    return setting
