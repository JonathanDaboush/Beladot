import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def truncate():
    engine = create_async_engine('postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_test')
    async with engine.begin() as conn:
        # Get all table names first
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        tables = [row[0] for row in result]
        print(f"Found {len(tables)} tables: {', '.join(tables)}")
        
        if tables:
            tables_str = ', '.join(tables)
            await conn.execute(text(f"TRUNCATE TABLE {tables_str} RESTART IDENTITY CASCADE"))
            print('All tables truncated successfully')
        else:
            print('No tables to truncate')
    await engine.dispose()

asyncio.run(truncate())

