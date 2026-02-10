# PURPOSE: Alembic environment configuration for migrations.
# DEPENDENCIES: Alembic, SQLAlchemy, app.database, app.config
# MODIFICATION NOTES: MVP migration setup.

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.config import settings
from app.database import Base
from app import models


config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    # PURPOSE: Resolve the database URL for Alembic.
    # DEPENDENCIES: app.config.settings
    # MODIFICATION NOTES: MVP URL resolution.
    return settings.database_url


def run_migrations_offline() -> None:
    # PURPOSE: Run migrations in offline mode.
    # DEPENDENCIES: Alembic
    # MODIFICATION NOTES: Standard Alembic offline runner.
    url = get_url()
    is_sqlite = url.startswith("sqlite")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=is_sqlite,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # PURPOSE: Run migrations in online mode.
    # DEPENDENCIES: Alembic, SQLAlchemy
    # MODIFICATION NOTES: Standard Alembic online runner.
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()
    is_sqlite = configuration["sqlalchemy.url"].startswith("sqlite")
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=is_sqlite,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
