import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def check_all_enums():
    engine = create_async_engine('postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_test')
    async with engine.connect() as conn:
        # Check all enum types
        enums = ['paymentmethod', 'paymentstatus', 'paymentfrequency']
        for enum_name in enums:
            try:
                result = await conn.execute(text(f"SELECT unnest(enum_range(NULL::{enum_name}))"))
                values = [row[0] for row in result]
                print(f"{enum_name}: {values}")
            except Exception as e:
                print(f"{enum_name}: ERROR - {e}")
    await engine.dispose()

asyncio.run(check_all_enums())
