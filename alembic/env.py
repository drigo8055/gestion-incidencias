"""
Alembic environment configuration for the SGI project.

Key points:
  - DATABASE_URL is read from fastapi_app.core.config.settings at runtime,
    so it is never hard-coded in alembic.ini.
  - target_metadata points to Base.metadata so autogenerate can detect schema
    changes from the ORM models.
  - compare_type=True makes Alembic detect column type changes (e.g. VARCHAR
    length, ENUM values) during autogenerate.
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ---------------------------------------------------------------------------
# Standard Alembic config object
# ---------------------------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Inject DATABASE_URL from pydantic-settings so secrets never live in .ini
# ---------------------------------------------------------------------------
from fastapi_app.core.config import settings  # noqa: E402

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# ---------------------------------------------------------------------------
# Target metadata — points to our DeclarativeBase so autogenerate works.
# Models are imported inside db/base.py (uncommented as they are created).
# ---------------------------------------------------------------------------
from fastapi_app.db.base import Base  # noqa: E402

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Migration runners
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """
    Offline mode: emit SQL to stdout without a live DB connection.
    Useful for generating a migration script to review before applying.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Online mode: connect to the database and apply migrations directly.
    NullPool is used to avoid keeping a connection open after the run.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
