"""Register and login endpoints for the simple username/password auth."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.Token, status_code=201)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new account and return an access token."""
    exists = (
        db.query(models.User)
        .filter(models.User.username == payload.username)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Username already taken")

    user = models.User(
        username=payload.username,
        hashed_password=auth.hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    token = auth.create_access_token(user.username)
    return schemas.Token(access_token=token, username=user.username)


@router.post("/login", response_model=schemas.Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Validate credentials (OAuth2 password form) and return a token."""
    user = (
        db.query(models.User)
        .filter(models.User.username == form.username)
        .first()
    )
    if not user or not auth.verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = auth.create_access_token(user.username)
    return schemas.Token(access_token=token, username=user.username)
