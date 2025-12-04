import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def fix_payments():
    engine = create_async_engine('postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_test')
    async with engine.connect() as conn:
        # Drop the method column and recreate as VARCHAR
        try:
            await conn.execute(text("ALTER TABLE payments DROP COLUMN IF EXISTS method"))
            await conn.execute(text("ALTER TABLE payments ADD COLUMN method VARCHAR(50)"))
            print("✓ Fixed payments.method column")
        except Exception as e:
            print(f"Error: {e}")
        
        await conn.commit()
    await engine.dispose()

asyncio.run(fix_payments())
