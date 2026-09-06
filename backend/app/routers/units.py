"""CRUD endpoints for Units."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/units", tags=["units"])


@router.get("", response_model=list[schemas.UnitOut])
def list_units(
    subject_id: int | None = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """List units, optionally filtered by ?subject_id=."""
    query = db.query(models.Unit)
    if subject_id is not None:
        query = query.filter(models.Unit.subject_id == subject_id)
    return query.order_by(models.Unit.id).all()


@router.post("", response_model=schemas.UnitOut, status_code=201)
def create_unit(
    payload: schemas.UnitCreate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    if not db.get(models.Subject, payload.subject_id):
        raise HTTPException(status_code=404, detail="Subject not found")
    unit = models.Unit(**payload.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


@router.get("/{unit_id}", response_model=schemas.UnitOut)
def get_unit(
    unit_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
):
    unit = db.get(models.Unit, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit


@router.put("/{unit_id}", response_model=schemas.UnitOut)
def update_unit(
    unit_id: int,
    payload: schemas.UnitUpdate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    unit = db.get(models.Unit, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(unit, field, value)
    db.commit()
    db.refresh(unit)
    return unit


@router.delete("/{unit_id}", status_code=204)
def delete_unit(
    unit_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
):
    unit = db.get(models.Unit, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    db.delete(unit)
    db.commit()
