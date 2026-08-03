from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.crud import crud_voice_report
from backend.app.db.session import get_db
from backend.app.schemas import VoiceReportCreate, VoiceReportResponse

router = APIRouter()


@router.post("/", response_model=VoiceReportResponse, status_code=status.HTTP_201_CREATED)
async def create_voice_report(
    report_in: VoiceReportCreate,
    db: AsyncSession = Depends(get_db),
):
    """ثبت گزارش وویس جدید در پایگاه داده"""
    report = await crud_voice_report.create(db, obj_in=report_in)
    return report


@router.get("/user/{user_id}", response_model=List[VoiceReportResponse])
async def read_user_voice_reports(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """دریافت لیست گزارش‌های وویس مربوط به یک کاربر"""
    reports = await crud_voice_report.get_multi_by_user(
        db, user_id=user_id, skip=skip, limit=limit
    )
    return reports