"""Vercel Python serverless entrypoint.

Vercel routes every /api/* request (see vercel.json rewrite) to this file and
serves the exported ASGI `app`. The real FastAPI app lives in backend/app; we
add it to sys.path and mount it under "/api" so its routes (/auth, /subjects,
...) are reachable at /api/auth, /api/subjects, ... — same origin as the
frontend, so no CORS is needed in production.
"""
import os
import sys

# Make the backend package importable (backend/app/...).
BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(BACKEND_DIR))

from fastapi import FastAPI  # noqa: E402
from app.main import app as backend_app  # noqa: E402

app = FastAPI()
app.mount("/api", backend_app)
