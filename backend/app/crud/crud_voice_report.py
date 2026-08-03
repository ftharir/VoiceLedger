from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.voice_report import VoiceReport
from backend.app.schemas.voice_report import VoiceReportCreate, VoiceReportUpdate


class CRUDVoiceReport:
    async def create(self, db: AsyncSession, obj_in: VoiceReportCreate) -> VoiceReport:
        db_obj = VoiceReport(
            user_id=obj_in.user_id,
            file_id=obj_in.file_id,
            duration=obj_in.duration,
            status="pending",
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_id(self, db: AsyncSession, report_id: int) -> Optional[VoiceReport]:
        result = await db.execute(select(VoiceReport).where(VoiceReport.id == report_id))
        return result.scalars().first()

    async def get_multi_by_user(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[VoiceReport]:
        result = await db.execute(
            select(VoiceReport)
            .where(VoiceReport.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(VoiceReport.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, db_obj: VoiceReport, obj_in: VoiceReportUpdate
    ) -> VoiceReport:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


crud_voice_report = CRUDVoiceReport()