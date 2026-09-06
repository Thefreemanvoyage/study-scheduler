"""Admin endpoint to seed a hosted database once.

On serverless hosts (Vercel) you can't easily run `python -m app.seed`, so this
token-guarded endpoint seeds the demo data + user, but only when the database
is empty. Set SEED_TOKEN in the host env, then POST /api/admin/seed?token=...
Once seeded you can delete this router.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models
from ..config import settings
from ..database import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/seed")
def seed_database(token: str = Query(...), db: Session = Depends(get_db)):
    # Disabled unless a SEED_TOKEN is configured and matches.
    if not settings.seed_token or token != settings.seed_token:
        raise HTTPException(status_code=403, detail="Invalid or missing seed token")

    # Idempotent: don't reseed a populated database.
    if db.query(models.Subject).first():
        return {"status": "already_seeded"}

    from ..seed import run  # imported lazily to avoid circular imports

    run()
    return {"status": "seeded", "login": "student / password123"}
