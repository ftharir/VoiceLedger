from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.knowledge_entry import (
    KnowledgeEntry,
    KnowledgeEntryType,
)
from backend.app.models.voice_report import ReportStatus, VoiceReport


class CRUDKnowledgeEntry:
    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        domain_id: int,
        entry_type: str,
        content: str,
        source_id: Optional[int] = None,
    ) -> KnowledgeEntry:
        db_obj = KnowledgeEntry(
            user_id=user_id,
            domain_id=domain_id,
            entry_type=entry_type,
            content=content,
            source_id=source_id,
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj

    async def complete_voice_report_with_entry(
        self,
        db: AsyncSession,
        *,
        report: VoiceReport,
        transcription: str,
    ) -> KnowledgeEntry:
        """
        VoiceReport completion and KnowledgeEntry creation
        are committed together.
        """

        knowledge_entry = KnowledgeEntry(
            user_id=report.user_id,
            domain_id=report.domain_id,
            entry_type=KnowledgeEntryType.VOICE.value,
            content=transcription,
            source_id=report.id,
        )

        report.transcription = transcription
        report.status = ReportStatus.COMPLETED.value

        db.add(knowledge_entry)

        await db.commit()
        await db.refresh(report)
        await db.refresh(knowledge_entry)

        return knowledge_entry


crud_knowledge_entry = CRUDKnowledgeEntry()