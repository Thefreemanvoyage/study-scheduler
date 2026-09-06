"""Database engine, session factory and declarative base."""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

# Render/Heroku expose the URL with the legacy `postgres://` scheme, but
# SQLAlchemy 2.x requires `postgresql://`. Normalise it here.
db_url = settings.database_url
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# SQLite (used for zero-config local dev) needs check_same_thread disabled so
# the connection can be shared across FastAPI's threadpool. PostgreSQL ignores
# connect_args here.
connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_engine(db_url, pool_pre_ping=True, connect_args=connect_args)

# SQLite doesn't enforce foreign keys / ON DELETE CASCADE unless asked to.
if db_url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _enable_sqlite_fk(dbapi_conn, _record):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a request-scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
