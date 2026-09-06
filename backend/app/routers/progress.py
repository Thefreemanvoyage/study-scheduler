"""Progress tracking and adaptive workload endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, services
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("", response_model=list[schemas.SubjectProgress])
def all_progress(
    db: Session = Depends(get_db), _user=Depends(get_current_user)
):
    """Subject-wise completion % for the dashboard."""
    subjects = db.query(models.Subject).order_by(models.Subject.id).all()
    return [services.compute_subject_progress(db, s) for s in subjects]


@router.get("/{subject_id}", response_model=schemas.SubjectProgress)
def subject_progress(
    subject_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    subject = db.get(models.Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return services.compute_subject_progress(db, subject)


@router.get("/{subject_id}/logs", response_model=list[schemas.ProgressLogOut])
def subject_progress_logs(
    subject_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Historical daily completion % values for trend charts."""
    if not db.get(models.Subject, subject_id):
        raise HTTPException(status_code=404, detail="Subject not found")
    return (
        db.query(models.ProgressLog)
        .filter(models.ProgressLog.subject_id == subject_id)
        .order_by(models.ProgressLog.date)
        .all()
    )


@router.get("/{subject_id}/workload", response_model=schemas.WorkloadOut)
def subject_workload(
    subject_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Adaptive workload: recalculated daily hours and burden index."""
    subject = db.get(models.Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return services.compute_workload(db, subject)


@router.get("/workload/all", response_model=list[schemas.WorkloadOut])
def all_workload(
    db: Session = Depends(get_db), _user=Depends(get_current_user)
):
    subjects = db.query(models.Subject).order_by(models.Subject.id).all()
    return [services.compute_workload(db, s) for s in subjects]
