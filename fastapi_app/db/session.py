"""
SQLAlchemy engine and session factory.

Provides:
  - engine       : shared Engine instance (psycopg2 / PostgreSQL)
  - SessionLocal : session factory bound to the engine
  - get_db       : FastAPI dependency that yields a Session per request

Usage in a FastAPI route:
    from fastapi import Depends
    from sqlalchemy.orm import Session
    from fastapi_app.db.session import get_db

    @router.get("/example")
    def example(db: Session = Depends(get_db)):
        ...
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from fastapi_app.core.config import settings

# ---------------------------------------------------------------------------
# Engine
# Pool settings are appropriate for a long-running web process:
#   pool_pre_ping  — verifies connection liveness before use
#   pool_size      — number of persistent connections kept open
#   max_overflow   — extra connections allowed above pool_size under load
# ---------------------------------------------------------------------------
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# ---------------------------------------------------------------------------
# Session factory
# autocommit=False  — transactions are explicit (commit/rollback in service)
# autoflush=False   — prevents accidental flushes mid-request
# expire_on_commit  — keeps objects usable after commit without re-querying
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    """
    Yield a SQLAlchemy Session for the duration of a single request.
    The session is always closed in the finally block, even on error.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
