"""CRUD endpoints for Tasks, plus completion side-effects.

When a task's status/hours change we recompute the parent unit's
`completed_hours` and refresh the subject's progress log, so the dashboard
and workload endpoints always reflect reality.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, services
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _sync_unit_and_progress(db: Session, unit: models.Unit) -> None:
    """Recompute a unit's completed hours from its tasks and log progress."""
    unit.completed_hours = sum(
        t.completed_hours for t in unit.tasks if t.status == "completed"
    )
    db.commit()
    # Refresh today's progress log for the owning subject.
    services.log_progress(db, unit.subject)


@router.get("", response_model=list[schemas.TaskOut])
def list_tasks(
    unit_id: int | None = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """List tasks, optionally filtered by ?unit_id=."""
    query = db.query(models.Task)
    if unit_id is not None:
        query = query.filter(models.Task.unit_id == unit_id)
    return query.order_by(models.Task.date).all()


@router.post("", response_model=schemas.TaskOut, status_code=201)
def create_task(
    payload: schemas.TaskCreate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    unit = db.get(models.Unit, payload.unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    task = models.Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    _sync_unit_and_progress(db, unit)
    return task


@router.get("/{task_id}", response_model=schemas.TaskOut)
def get_task(
    task_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: int,
    payload: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    _sync_unit_and_progress(db, task.unit)
    return task


@router.post("/{task_id}/complete", response_model=schemas.TaskOut)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Mark a task completed; log the planned hours as completed if unset."""
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = "completed"
    if not task.completed_hours:
        task.completed_hours = task.planned_hours
    db.commit()
    db.refresh(task)
    _sync_unit_and_progress(db, task.unit)
    return task


@router.post("/{task_id}/skip", response_model=schemas.TaskOut)
def skip_task(
    task_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Mark a task skipped; workload endpoint will reflect the added burden."""
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = "skipped"
    task.completed_hours = 0.0
    db.commit()
    db.refresh(task)
    _sync_unit_and_progress(db, task.unit)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    unit = task.unit
    db.delete(task)
    db.commit()
    _sync_unit_and_progress(db, unit)
