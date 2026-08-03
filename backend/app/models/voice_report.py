from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base_class import Base

if TYPE_CHECKING:
    from backend.app.models.user import User


class VoiceReport(Base):
    __tablename__ = "voice_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    file_id: Mapped[str] = mapped_column(String(512), nullable=False)  # شناسه فایل در بله
    file_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)  # آدرس ذخیره محلی یا سرویس ابری
    duration: Mapped[Optional[int]] = mapped_column(nullable=True)  # مدت زمان به ثانیه
    
    transcription: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # متن استخراج شده از وویس
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True, nullable=False)  # pending, processing, completed, failed
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # ارتباط با مدل کاربر
    user: Mapped["User"] = relationship("User", back_populates="reports")

    def __repr__(self) -> str:
        return f"<VoiceReport id={self.id} user_id={self.user_id} status={self.status}>"