"""
Shared pytest fixtures for the SGI test suite.

Fixtures provided:
  - db_session   : SQLite in-memory SQLAlchemy session (unit / property tests)
  - client       : Starlette TestClient with the in-memory DB injected
  - make_usuario : factory for creating Usuario ORM instances in the test DB
  - make_categoria : factory for creating Categoria ORM instances in the test DB

The fixtures use SQLite (via aiosqlite-compatible sync driver) so no running
PostgreSQL instance is required during local development or CI.
"""

import os
import uuid
from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

# ── Override DATABASE_URL before any app module loads the real settings ───────
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")

from fastapi_app.db.base import Base  # noqa: E402 — must come after env override
from fastapi_app.db.session import get_db  # noqa: E402
from fastapi_app.main import app  # noqa: E402

# ── SQLite in-memory engine ────────────────────────────────────────────────────
_TEST_DATABASE_URL = "sqlite:///:memory:"

_engine = create_engine(
    _TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Enable FK enforcement in SQLite (disabled by default).
@event.listens_for(_engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


_TestingSessionLocal = sessionmaker(
    bind=_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Yields a fresh SQLAlchemy session backed by an in-memory SQLite database.
    All tables are created before the test and dropped after it, ensuring
    full isolation between test functions.
    """
    Base.metadata.create_all(bind=_engine)
    session: Session = _TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Yields a Starlette TestClient with the FastAPI app configured to use the
    in-memory SQLite session instead of the real PostgreSQL session.
    """

    def _override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass  # session lifecycle managed by the db_session fixture

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ── Model factories ────────────────────────────────────────────────────────────
# These are defined as inner-fixture factories so models can be imported lazily
# (models don't exist yet in task 1; they will be added in task 2).


@pytest.fixture(scope="function")
def make_usuario(db_session: Session):
    """
    Factory fixture that creates and persists a Usuario in the test DB.

    Usage::

        def test_something(make_usuario):
            user = make_usuario(nombre="Ana", email="ana@example.com", rol="USUARIO")
    """

    def _factory(**kwargs: Any):
        # Import lazily so this fixture file doesn't break before models exist.
        from fastapi_app.models.usuario import Usuario  # noqa: PLC0415
        from fastapi_app.models.enums import RolEnum  # noqa: PLC0415

        defaults: dict[str, Any] = {
            "id": uuid.uuid4(),
            "nombre": "Test User",
            "email": f"user-{uuid.uuid4().hex[:8]}@example.com",
            "password_hash": "$2b$12$placeholder_hash_for_tests_only",
            "rol": RolEnum.USUARIO,
            "is_active": True,
            "failed_login_attempts": 0,
        }
        defaults.update(kwargs)
        usuario = Usuario(**defaults)
        db_session.add(usuario)
        db_session.commit()
        db_session.refresh(usuario)
        return usuario

    return _factory


@pytest.fixture(scope="function")
def make_categoria(db_session: Session):
    """
    Factory fixture that creates and persists a Categoria in the test DB.

    Usage::

        def test_something(make_categoria):
            cat = make_categoria(nombre="Hardware")
    """

    def _factory(**kwargs: Any):
        from fastapi_app.models.categoria import Categoria  # noqa: PLC0415

        defaults: dict[str, Any] = {
            "id": uuid.uuid4(),
            "nombre": f"Categoria-{uuid.uuid4().hex[:6]}",
            "is_active": True,
        }
        defaults.update(kwargs)
        categoria = Categoria(**defaults)
        db_session.add(categoria)
        db_session.commit()
        db_session.refresh(categoria)
        return categoria

    return _factory
