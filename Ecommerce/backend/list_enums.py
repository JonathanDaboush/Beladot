import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def list_enums():
    engine = create_async_engine('postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_test')
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT typname FROM pg_type WHERE typcategory = 'E' ORDER BY typname"))
        enums = [row[0] for row in result]
        print("All enum types:", enums)
    await engine.dispose()

asyncio.run(list_enums())
