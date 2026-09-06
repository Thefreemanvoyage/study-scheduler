"""CRUD endpoints for Subjects (all protected by auth)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("", response_model=list[schemas.SubjectOut])
def list_subjects(
    db: Session = Depends(get_db), _user=Depends(get_current_user)
):
    return db.query(models.Subject).order_by(models.Subject.id).all()


@router.post("", response_model=schemas.SubjectOut, status_code=201)
def create_subject(
    payload: schemas.SubjectCreate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    subject = models.Subject(**payload.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@router.get("/{subject_id}", response_model=schemas.SubjectOut)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    subject = db.get(models.Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.put("/{subject_id}", response_model=schemas.SubjectOut)
def update_subject(
    subject_id: int,
    payload: schemas.SubjectUpdate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    subject = db.get(models.Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(subject, field, value)
    db.commit()
    db.refresh(subject)
    return subject


@router.delete("/{subject_id}", status_code=204)
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    subject = db.get(models.Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    db.delete(subject)
    db.commit()
