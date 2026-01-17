# Async SQLAlchemy setup for FastAPI/Quart

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

_engine = None
_session_factory = None

def get_async_engine():
    """
    Create and return an async SQLAlchemy Engine from the DATABASE_URL.
    Defers environment access until runtime to avoid import-time failures.
    """
    global _engine
    if _engine is None:
        import os
        url = os.environ.get("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL environment variable not set")
        # Ensure async driver for SQLite in test environments
        if url.startswith("sqlite") and "+aiosqlite" not in url:
            url = url.replace("sqlite://", "sqlite+aiosqlite://")
        _engine = create_async_engine(url, echo=True, future=True)
    return _engine

def get_async_sessionmaker():
    """
    Return an async sessionmaker bound to the runtime-created async Engine.
    """
    global _session_factory
    if _session_factory is None:
        # Defer engine creation; avoid generic type evaluation at import time
        _session_factory = async_sessionmaker(get_async_engine(), expire_on_commit=False)
    return _session_factory

__all__ = [
    "AsyncSessionLocal",
    "engine",
    "get_async_engine",
    "get_async_sessionmaker",
]

class _LazyAsyncSessionLocal:
    """Callable proxy that creates the async session factory on first use and reuses it thereafter."""
    def __call__(self, *args, **kwargs):
        return get_async_sessionmaker()(*args, **kwargs)

# Public symbol expected by app/tests; lazily initialized, single factory
AsyncSessionLocal = _LazyAsyncSessionLocal()

class _LazyEngineProxy:
    """Attribute proxy for the async Engine to preserve lazy initialization.

    Allows code importing `engine` to access attributes/methods like
    `engine.begin()`, `engine.dispose()`, etc., while deferring actual
    engine creation until first attribute access.
    """
    def __getattr__(self, name):
        return getattr(get_async_engine(), name)

# Public symbol expected by tests (`engine`);
# provides lazy access to the actual async Engine instance
engine = _LazyEngineProxy()



