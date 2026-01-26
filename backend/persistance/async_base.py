
# Asyncpg setup for FastAPI

_pool = None

async def get_asyncpg_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL.replace('postgresql+asyncpg', 'postgresql'))
    return _pool

async def get_db_connection():
    pool = await get_asyncpg_pool()
    async with pool.acquire() as connection:
        yield connection

# Async SQLAlchemy session setup for FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.config import settings

# Convert sync DB URL to async if needed
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql+psycopg2"):
    db_url = db_url.replace("postgresql+psycopg2", "postgresql+asyncpg")

async_engine = create_async_engine(db_url, echo=False, future=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Optionally, keep the asyncpg pool for direct connections if needed elsewhere
import asyncpg
_pool = None
async def get_asyncpg_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn=db_url.replace('postgresql+asyncpg', 'postgresql'))
    return _pool

async def get_db_connection():
    pool = await get_asyncpg_pool()
    async with pool.acquire() as connection:
        yield connection



