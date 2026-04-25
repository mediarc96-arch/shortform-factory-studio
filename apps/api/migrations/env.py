from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from sfs_console.config import Settings


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def run_migrations_offline() -> None:
    url = _database_url()
    context.configure(url=url, literal_binds=True, dialect_opts={"paramstyle": "named"})

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(_database_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


def _sqlalchemy_url(url: str | None) -> str:
    if not url:
        raise RuntimeError("SFS_DATABASE_URL or SFS_DB_* env vars are required for migrations")
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def _database_url() -> str:
    configured_url = config.attributes.get("database_url")
    if isinstance(configured_url, str) and configured_url:
        return configured_url
    return _sqlalchemy_url(Settings.from_env().database_url)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
