import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, DateTime, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base_class import Base

if TYPE_CHECKING:
    from backend.app.models.knowledge_entry import KnowledgeEntry
    from backend.app.models.voice_report import VoiceReport


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    DOMAIN_ADMIN = "domain_admin"
    OPERATOR = "operator"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    bale_user_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
        nullable=False,
    )

    username: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    first_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    last_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        default=UserRole.OPERATOR.value,
        server_default=UserRole.OPERATOR.value,
        nullable=False,
    )

    is_approved: Mapped[bool] = mapped_column(
        default=False,
        server_default=text("false"),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
        server_default=text("true"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    voice_reports: Mapped[List["VoiceReport"]] = relationship(
        "VoiceReport",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    knowledge_entries: Mapped[List["KnowledgeEntry"]] = relationship(
        "KnowledgeEntry",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<User id={self.id} "
            f"bale_id={self.bale_user_id} "
            f"role={self.role} "
            f"approved={self.is_approved}>"
        )