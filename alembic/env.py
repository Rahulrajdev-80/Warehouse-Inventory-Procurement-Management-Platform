from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys


# Add project root to Python path
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(__file__))
)


# Import application configuration
from app.config import settings

# Import SQLAlchemy Base
from app.database import Base

# Import all models so Alembic can detect them
import app.models


# Alembic Config object
config = context.config


# SQLAlchemy metadata
target_metadata = Base.metadata


# ---------------------------------------------------------
# OFFLINE MIGRATIONS
# ---------------------------------------------------------

def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.
    """

    url = settings.SYNC_DATABASE_URL

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------
# ONLINE MIGRATIONS
# ---------------------------------------------------------

def run_migrations_online() -> None:
    """
    Run migrations in online mode.
    """

    configuration = config.get_section(
        config.config_ini_section
    )

    if configuration is None:
        configuration = {}

    configuration["sqlalchemy.url"] = settings.SYNC_DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------
# RUN MIGRATIONS
# ---------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()