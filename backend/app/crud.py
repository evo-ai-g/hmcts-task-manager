from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas


def create_task(db: Session, payload: schemas.TaskCreate) -> models.Task:
    """Insert a new task and return the persisted row."""
    task = models.Task(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        due_date=payload.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)  # populates task.id, created_at, updated_at from the DB
    return task


def list_tasks(db: Session) -> list[models.Task]:
    """Return all tasks ordered by due date, then id (deterministic)."""
    stmt = select(models.Task).order_by(
        models.Task.due_date.asc(), models.Task.id.asc()
    )
    return list(db.scalars(stmt).all())


def get_task(db: Session, task_id: int) -> models.Task | None:
    """Return a task by id, or None if it doesn't exist."""
    return db.get(models.Task, task_id)


def update_task_status(
    db: Session, task: models.Task, new_status: models.TaskStatus
) -> models.Task:
    """Change a task's status and bump updated_at."""
    task.status = new_status
    task.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: models.Task) -> None:
    """Delete a task permanently."""
    db.delete(task)
    db.commit()
