import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def check():
    engine = create_async_engine('postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_test')
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT unnest(enum_range(NULL::paymentfrequency))"))
        values = [row[0] for row in result]
        print("PaymentFrequency enum values in database:", values)
    await engine.dispose()

asyncio.run(check())
