import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as SAEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TaskStatus(str, enum.Enum):
    """The three allowed task statuses."""

    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Task(Base):
    """A caseworker task."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus), nullable=False, default=TaskStatus.TODO, index=True
    )
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )
