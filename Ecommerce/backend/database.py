"""
Database Connection and Session Management Module

Provides async and sync database engines, session makers, and the base class
for SQLAlchemy ORM models. Handles connection pooling, session lifecycle,
and provides dependency injection for FastAPI routes.

Components:
    - async_engine: Async SQLAlchemy engine for FastAPI endpoints
    - sync_engine: Sync SQLAlchemy engine for migrations
    - AsyncSessionLocal: Async session factory
    - SessionLocal: Sync session factory (for Alembic)
    - Base: Declarative base class for all ORM models
    - get_db(): FastAPI dependency for database sessions

Connection Pooling:
    - Pool size: 10 connections
    - Max overflow: 20 additional connections
    - Pre-ping: True (validates connections before use)

Usage in Routes:
    @router.get("/endpoint")
    async def endpoint(db: AsyncSession = Depends(get_db)):
        # Database operations here
        pass
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from config import Settings

# Load application settings
settings = Settings()

# ============================================================================
# ASYNC ENGINE (Primary - for FastAPI routes)
# ============================================================================
async_engine = create_async_engine(
    settings.DATABASE_URL,  # postgresql+asyncpg://user:pass@host:port/db
    echo=settings.DEBUG,  # Log all SQL statements when DEBUG=True
    future=True,  # Use SQLAlchemy 2.0 style
    pool_pre_ping=True,  # Validate connections before using them
    pool_size=10,  # Number of connections to maintain in pool
    max_overflow=20  # Maximum additional connections beyond pool_size
)

# ============================================================================
# SYNC ENGINE (For Alembic migrations only)
# ============================================================================
sync_engine = create_engine(
    settings.DATABASE_URL_SYNC,  # postgresql://user:pass@host:port/db
    echo=settings.DEBUG,  # Log SQL when DEBUG=True
    pool_pre_ping=True  # Validate connections before use
)

# ============================================================================
# SESSION FACTORIES
# ============================================================================

# Async session maker for FastAPI routes
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit (allows access after commit)
    autocommit=False,  # Manual commit required (explicit transaction control)
    autoflush=False  # Manual flush required (explicit control over DB writes)
)

# Sync session maker for Alembic migrations
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

# ============================================================================
# BASE CLASS FOR ORM MODELS
# ============================================================================
Base = declarative_base()
"""
Base class for all SQLAlchemy ORM models.

All models in Models/ directory should inherit from this class:
    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        ...
"""


# ============================================================================
# DEPENDENCY INJECTION FOR FASTAPI
# ============================================================================
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides database sessions.
    
    Automatically manages session lifecycle:
    1. Creates a new session for each request
    2. Yields the session to the route handler
    3. Closes the session after the request completes
    4. Rolls back on exceptions
    
    Usage:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    
    Yields:
        AsyncSession: Database session for the request
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Initialize database tables
async def init_db():
    """
    Create all tables in the database.
    This should be called on application startup.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Close database connections
async def close_db():
    """
    Close all database connections.
    This should be called on application shutdown.
    """
    await async_engine.dispose()
