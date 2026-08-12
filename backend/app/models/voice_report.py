import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base_class import Base

if TYPE_CHECKING:
    from backend.app.models.domain import Domain
    from backend.app.models.user import User


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    TRANSCRIBING = "transcribing"
    COMPLETED = "completed"
    FAILED = "failed"


class VoiceReport(Base):
    __tablename__ = "voice_reports"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    domain_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("domains.id"),
        nullable=False,
        index=True,
    )

    file_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    file_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    duration: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default=ReportStatus.PENDING.value,
        server_default=ReportStatus.PENDING.value,
        nullable=False,
    )

    transcription: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="voice_reports",
    )

    domain: Mapped["Domain"] = relationship(
        "Domain",
        back_populates="voice_reports",
    )