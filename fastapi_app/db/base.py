"""
SQLAlchemy declarative base.

All ORM models must subclass Base defined here. Alembic reads
Base.metadata to autogenerate migration scripts, so every model
module must be imported somewhere before autogenerate runs.

Model imports will be uncommented here progressively as each
model is implemented in task 2.2.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all SGI ORM models."""


# ---------------------------------------------------------------------------
# Model imports for Alembic autogenerate — uncomment as models are created
# (task 2.2):
# ---------------------------------------------------------------------------
# from fastapi_app.models import usuario    # noqa: F401
# from fastapi_app.models import categoria  # noqa: F401
# from fastapi_app.models import incidencia # noqa: F401
# from fastapi_app.models import comentario # noqa: F401
# from fastapi_app.models import historial  # noqa: F401
