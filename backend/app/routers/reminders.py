"""Reminder scheduling endpoints.

Reminders are stored against tasks. The `/next` endpoint returns upcoming
reminder times so the frontend can fire push/email/browser notifications.
Actual push/email delivery is a deployment concern (e.g. a cron worker or
a service like Twilio/SendGrid); here we expose the schedule.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("", response_model=list[schemas.ReminderOut])
def list_reminders(
    db: Session = Depends(get_db), _user=Depends(get_current_user)
):
    return db.query(models.Reminder).order_by(models.Reminder.reminder_time).all()


@router.post("", response_model=schemas.ReminderOut, status_code=201)
def create_reminder(
    payload: schemas.ReminderCreate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    if not db.get(models.Task, payload.task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    reminder = models.Reminder(**payload.model_dump())
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.get("/next", response_model=list[schemas.NextReminder])
def next_reminders(
    limit: int = 10,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Return the next scheduled reminders (soonest first)."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    rows = (
        db.query(models.Reminder)
        .filter(
            models.Reminder.status == "scheduled",
            models.Reminder.reminder_time >= now,
        )
        .order_by(models.Reminder.reminder_time)
        .limit(limit)
        .all()
    )
    result = []
    for r in rows:
        unit = r.task.unit
        result.append(
            schemas.NextReminder(
                reminder_id=r.id,
                task_id=r.task_id,
                reminder_time=r.reminder_time,
                unit_name=unit.name,
                subject_name=unit.subject.name,
            )
        )
    return result


@router.post("/{reminder_id}/dismiss", response_model=schemas.ReminderOut)
def dismiss_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    reminder = db.get(models.Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    reminder.status = "dismissed"
    db.commit()
    db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}", status_code=204)
def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    reminder = db.get(models.Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(reminder)
    db.commit()
