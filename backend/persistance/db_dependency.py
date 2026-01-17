from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from .async_base import get_async_sessionmaker

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_async_sessionmaker()
    async with session_factory() as session:
        yield session
