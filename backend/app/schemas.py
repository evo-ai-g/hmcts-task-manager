from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

from app.models import TaskStatus


class CamelModel(BaseModel):
    """Base model that serialises to camelCase JSON (matches the starter repos)."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class TaskBase(CamelModel):
    """Fields shared by create and read responses."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.TODO)
    due_date: datetime

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be blank")
        return v.strip()


class TaskCreate(TaskBase):
    """Payload the client sends to create a task."""


class TaskStatusUpdate(CamelModel):
    """Payload for the PATCH status endpoint."""

    status: TaskStatus


class TaskRead(TaskBase):
    """Response shape for a task."""

    id: int
    created_at: datetime
    updated_at: datetime
