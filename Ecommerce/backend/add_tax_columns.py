import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def add_columns():
    engine = create_async_engine('postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_test')
    async with engine.begin() as conn:
        await conn.execute(text('ALTER TABLE employee_financials ADD COLUMN IF NOT EXISTS federal_tax_rate NUMERIC(5,4) DEFAULT 0.15'))
        await conn.execute(text('ALTER TABLE employee_financials ADD COLUMN IF NOT EXISTS provincial_tax_rate NUMERIC(5,4) DEFAULT 0.10'))
        await conn.execute(text('ALTER TABLE employee_financials ADD COLUMN IF NOT EXISTS cpp_contribution_rate NUMERIC(5,4) DEFAULT 0.0595'))
        await conn.execute(text('ALTER TABLE employee_financials ADD COLUMN IF NOT EXISTS ei_contribution_rate NUMERIC(5,4) DEFAULT 0.0166'))
    await engine.dispose()
    print('Tax columns added successfully')

asyncio.run(add_columns())
