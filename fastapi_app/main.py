"""
SGI - Sistema de Gestion de Incidencias
FastAPI application entry point.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Sistema de Gestion de Incidencias (SGI)",
    version="0.1.0",
    description="API REST para registrar, gestionar y resolver incidencias.",
)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}
