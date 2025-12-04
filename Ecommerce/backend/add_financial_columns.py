import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def add_payment_frequency_column():
    """Add payment_frequency column to employee_financials table"""
    engine = create_async_engine('postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_test')
    
    async with engine.connect() as conn:
        # Add payment_frequency column
        await conn.execute(text("""
            ALTER TABLE employee_financials 
            ADD COLUMN IF NOT EXISTS payment_frequency paymentfrequency NOT NULL DEFAULT 'bi_weekly'
        """))
        await conn.commit()
        
        # Add payment_method column
        await conn.execute(text("""
            ALTER TABLE employee_financials 
            ADD COLUMN IF NOT EXISTS payment_method paymentmethod NOT NULL DEFAULT 'direct_deposit'
        """))
        await conn.commit()
        
        print("✓ Added payment_frequency and payment_method columns")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_payment_frequency_column())
