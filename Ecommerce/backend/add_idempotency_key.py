import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def add_col():
    engine = create_async_engine('postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_test')
    async with engine.connect() as conn:
        await conn.execute(text('ALTER TABLE orders ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(255)'))
        await conn.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_idempotency_key ON orders(idempotency_key) WHERE idempotency_key IS NOT NULL'))
        await conn.commit()
        print('✓ Added idempotency_key column')
    await engine.dispose()

asyncio.run(add_col())
