"""Vercel serverless entry point for exHacker FastAPI backend.

This file is deployed as a Vercel Serverless Function via @vercel/python.
It imports the FastAPI app and ensures the production environment is configured
for PostgreSQL (Supabase) instead of SQLite.
"""
import os
import sys

# Ensure the backend app is on the Python path
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# Force production environment variables for serverless
os.environ["ENV"] = "production"
os.environ["MOCK_AI"] = os.environ.get("MOCK_AI", "true")
os.environ["MOCK_RESEARCH"] = os.environ.get("MOCK_RESEARCH", "true")

# CORS — allow frontend
_origins = os.environ.get("CORS_ORIGINS", '["https://exhacker-frontend.vercel.app"]')
os.environ.setdefault("CORS_ORIGINS", _origins)

from app.main import app  # noqa: E402

handler = app
