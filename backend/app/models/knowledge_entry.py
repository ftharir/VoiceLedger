import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base_class import Base

if TYPE_CHECKING:
    from backend.app.models.domain import Domain
    from backend.app.models.user import User


class KnowledgeEntryType(str, enum.Enum):
    VOICE = "voice"
    TEXT = "text"


class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entries"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    domain_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("domains.id"),
        nullable=False,
        index=True,
    )

    entry_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    source_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="knowledge_entries",
    )

    domain: Mapped["Domain"] = relationship(
        "Domain",
        back_populates="knowledge_entries",
    )

    def __repr__(self) -> str:
        return (
            f"<KnowledgeEntry id={self.id} "
            f"type={self.entry_type} "
            f"domain_id={self.domain_id}>"
        )