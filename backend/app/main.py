"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import auth, subjects, units, tasks, progress, reminders, admin

# Create tables on startup. For production migrations use Alembic; for this
# project create_all keeps setup simple. Wrapped so an unreachable database at
# cold start doesn't crash the whole serverless function (the frontend and
# health check still work; DB-backed routes will surface a clear error).
import logging

try:
    Base.metadata.create_all(bind=engine)
except Exception as exc:  # pragma: no cover
    logging.getLogger("uvicorn.error").warning(
        "Could not create tables at startup (check DATABASE_URL): %s", exc
    )

app = FastAPI(
    title="Study Scheduler API",
    version="1.0.0",
    description="Backend for the Study Scheduler app (subjects, units, tasks, "
    "progress tracking, adaptive workload and reminders).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(subjects.router)
app.include_router(units.router)
app.include_router(tasks.router)
app.include_router(progress.router)
app.include_router(reminders.router)
app.include_router(admin.router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "service": "study-scheduler-api"}
