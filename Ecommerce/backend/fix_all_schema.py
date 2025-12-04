import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def fix_all():
    engine = create_async_engine('postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_test')
    async with engine.connect() as conn:
        # Fix payments table
        await conn.execute(text('ALTER TABLE payments ADD COLUMN IF NOT EXISTS method VARCHAR(50)'))
        
        # Fix sessions table
        await conn.execute(text('ALTER TABLE sessions ALTER COLUMN expires_at DROP NOT NULL'))
        
        await conn.commit()
        print('✓ Fixed database schema')
    await engine.dispose()

asyncio.run(fix_all())
