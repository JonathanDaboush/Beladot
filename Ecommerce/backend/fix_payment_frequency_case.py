import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def fix_payment_frequency_enum():
    """Fix paymentfrequency enum to use lowercase values"""
    engine = create_async_engine('postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_test')
    
    async with engine.connect() as conn:
        # Drop and recreate the enum with lowercase values
        await conn.execute(text("DROP TYPE IF EXISTS paymentfrequency CASCADE"))
        await conn.commit()
        
        await conn.execute(text("CREATE TYPE paymentfrequency AS ENUM ('weekly', 'bi_weekly', 'semi_monthly', 'monthly')"))
        await conn.commit()
        
        print("✓ Fixed paymentfrequency enum to lowercase")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_payment_frequency_enum())
