"""Business logic: progress calculation and adaptive workload."""
from datetime import date

from sqlalchemy.orm import Session

from . import models, schemas


def compute_subject_progress(db: Session, subject: models.Subject) -> schemas.SubjectProgress:
    """Aggregate a subject's units/tasks into a progress summary.

    Completion % is based on completed vs planned hours across all units,
    falling back to task counts when no hours are planned yet.
    """
    units = subject.units
    planned = sum(u.planned_hours for u in units)
    completed = sum(u.completed_hours for u in units)

    tasks = [t for u in units for t in u.tasks]
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == "completed")
    skipped_tasks = sum(1 for t in tasks if t.status == "skipped")

    if planned > 0:
        percent = round(min(completed / planned, 1.0) * 100, 1)
    elif total_tasks > 0:
        percent = round(completed_tasks / total_tasks * 100, 1)
    else:
        percent = 0.0

    return schemas.SubjectProgress(
        subject_id=subject.id,
        subject_name=subject.name,
        planned_hours=round(planned, 2),
        completed_hours=round(completed, 2),
        completion_percent=percent,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        skipped_tasks=skipped_tasks,
    )


def log_progress(db: Session, subject: models.Subject) -> models.ProgressLog:
    """Upsert today's ProgressLog row for a subject and return it."""
    progress = compute_subject_progress(db, subject)
    today = date.today()
    log = (
        db.query(models.ProgressLog)
        .filter(
            models.ProgressLog.subject_id == subject.id,
            models.ProgressLog.date == today,
        )
        .first()
    )
    if log is None:
        log = models.ProgressLog(
            subject_id=subject.id,
            date=today,
            completion_percent=progress.completion_percent,
        )
        db.add(log)
    else:
        log.completion_percent = progress.completion_percent
    db.commit()
    db.refresh(log)
    return log


def compute_workload(db: Session, subject: models.Subject) -> schemas.WorkloadOut:
    """Recalculate recommended daily study hours after skipped tasks.

    burden_index > 1.0 means the student must now study more per remaining
    day than originally planned, because time was lost to skipped tasks.
    """
    units = subject.units
    tasks = [t for u in units for t in u.tasks]

    planned_total = sum(u.planned_hours for u in units)
    completed_total = sum(u.completed_hours for u in units)
    remaining_hours = max(planned_total - completed_total, 0.0)

    skipped_hours = sum(
        t.planned_hours for t in tasks if t.status == "skipped"
    )

    today = date.today()
    future_dates = [t.date for t in tasks if t.date >= today]
    # Days left until the last scheduled task (at least 1 to avoid /0).
    if future_dates:
        remaining_days = max((max(future_dates) - today).days + 1, 1)
    else:
        remaining_days = 1

    # Original plan: spread ALL planned hours evenly across the schedule.
    all_dates = [t.date for t in tasks]
    if all_dates:
        span_days = max((max(all_dates) - min(all_dates)).days + 1, 1)
    else:
        span_days = 1
    original_daily = planned_total / span_days if span_days else 0.0

    recommended_daily = remaining_hours / remaining_days if remaining_days else 0.0
    burden_index = (
        round(recommended_daily / original_daily, 2)
        if original_daily > 0
        else 1.0
    )

    return schemas.WorkloadOut(
        subject_id=subject.id,
        subject_name=subject.name,
        remaining_hours=round(remaining_hours, 2),
        remaining_days=remaining_days,
        original_daily_hours=round(original_daily, 2),
        recommended_daily_hours=round(recommended_daily, 2),
        skipped_hours=round(skipped_hours, 2),
        burden_index=burden_index,
    )
