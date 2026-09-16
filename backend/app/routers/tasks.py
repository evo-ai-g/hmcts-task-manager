from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_or_404(db: Session, task_id: int):
    """Fetch a task or raise 404. Shared by all by-id endpoints."""
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return task


@router.post("", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    return crud.create_task(db, payload)


@router.get("", response_model=list[schemas.TaskRead])
def list_tasks(db: Session = Depends(get_db)):
    """Retrieve all tasks ordered by due date."""
    return crud.list_tasks(db)


@router.get("/{task_id}", response_model=schemas.TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Retrieve a single task by ID."""
    return _get_or_404(db, task_id)


@router.patch("/{task_id}/status", response_model=schemas.TaskRead)
def update_task_status(
    task_id: int, payload: schemas.TaskStatusUpdate, db: Session = Depends(get_db)
):
    """Update the status of a task."""
    task = _get_or_404(db, task_id)
    return crud.update_task_status(db, task, payload.status)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task."""
    task = _get_or_404(db, task_id)
    crud.delete_task(db, task)
    return None
