"""Vercel serverless entry point for exHacker FastAPI backend.

This file is deployed as a Vercel Serverless Function.
It imports and re-exports the FastAPI app from the backend package.
"""
import sys
import os

# Add the backend directory to Python path so imports resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Set default environment for Vercel
os.environ.setdefault("ENV", "production")

from app.main import app  # noqa: E402, F401

# Vercel ASGI handler — exports the app variable
handler = app
