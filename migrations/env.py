# migrations/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# --------------------------------------------------
# Ensure backend is importable
# --------------------------------------------------
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your declarative Base
from backend.db.base import Base  # canonical declarative Base

# Ensure all ORM models are imported so Base.metadata is populated
import importlib, pkgutil
try:
    import backend.persistance as models_pkg
    for _finder, _name, _ispkg in pkgutil.iter_modules(models_pkg.__path__):
        try:
            importlib.import_module(f"backend.persistance.{_name}")
        except Exception:
            # Skip modules that fail to import; continue loading others
            continue
except Exception:
    # Package missing or failed entirely; proceed with whatever is loaded
    pass

# Alembic Config object
config = context.config

# Setup Python logging from config, if available
if config.config_file_name:
    fileConfig(config.config_file_name)

# Metadata for 'autogenerate'
target_metadata = Base.metadata

def _sync_url_from_env_or_config() -> str:
    """Return a synchronous driver URL derived from env or alembic.ini.

    Converts async URLs like sqlite+aiosqlite and postgresql+asyncpg to their
    sync equivalents for use in Alembic's synchronous migration context.
    """
    # Prefer explicit env var, else fallback to alembic.ini
    url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    if not url:
        raise RuntimeError("DATABASE_URL or sqlalchemy.url must be set for Alembic")
    # Normalize to sync drivers
    if "+aiosqlite" in url:
        url = url.replace("+aiosqlite", "")
    if "+asyncpg" in url:
        url = url.replace("+asyncpg", "+psycopg2")
    return url

# --------------------------------------------------
# Offline migration mode
# --------------------------------------------------
def run_migrations_offline():
    url = _sync_url_from_env_or_config()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

# --------------------------------------------------
# Online migration mode
# --------------------------------------------------
def run_migrations_online():
    url = _sync_url_from_env_or_config()
    connectable = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()

# --------------------------------------------------
# Run
# --------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
