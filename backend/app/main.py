"""Main entry point for Family Financial OS.

Starting the FastAPI server and loading the application.

Usage:
    python backend/app/main.py
"""

from __future__ import annotations
import sys
import os
from datetime import datetime

# ── Third-party ──────────────────────────────────
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ── Internal ─────────────────────────────────────
from app.api.api import router as api_router


# ── App ───────────────────────────────────────────

app = FastAPI(
    title="Family Financial OS",
    version="0.1.0",
    description="Sistema operativo financiero para hogares colombianos",
)

# ── CORS ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include API Router ───────────────────────────
app.include_router(api_router, prefix="/api/v1")


# ── Root ──────────────────────────────────────────

@app.get("/")
async def root() -> dict:
    return {
        "message": "Family Financial OS",
        "version": "0.1.0",
        "status": "ready",
        "api": "/api/v1",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


# ── Run ──────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
