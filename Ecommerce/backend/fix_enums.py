"""Fix PaymentFrequency enum values to match Python model."""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def fix_enum():
    test_db_url = "postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_test"
    engine = create_async_engine(test_db_url)
    
    async with engine.connect() as conn:
        # Drop and recreate the enum with correct values
        print("Updating PaymentFrequency enum...")
        
        # First, remove the enum from the column
        await conn.execute(text("""
            ALTER TABLE employee_financials 
            ALTER COLUMN payment_frequency TYPE VARCHAR(50)
        """))
        print("✓ Converted payment_frequency to VARCHAR")
        
        # Drop the old enum
        await conn.execute(text("DROP TYPE IF EXISTS paymentfrequency CASCADE"))
        print("✓ Dropped old enum")
        
        # Create new enum with lowercase values
        await conn.execute(text("""
            CREATE TYPE paymentfrequency AS ENUM (
                'weekly', 'bi_weekly', 'semi_monthly', 'monthly'
            )
        """))
        print("✓ Created new enum with lowercase values")
        
        # Convert column back to enum
        await conn.execute(text("""
            ALTER TABLE employee_financials 
            ALTER COLUMN payment_frequency TYPE paymentfrequency 
            USING payment_frequency::paymentfrequency
        """))
        print("✓ Converted column back to enum")
        
        # Do the same for paymentmethod
        await conn.execute(text("""
            ALTER TABLE employee_financials 
            ALTER COLUMN payment_method TYPE VARCHAR(50)
        """))
        
        await conn.execute(text("DROP TYPE IF EXISTS paymentmethod CASCADE"))
        
        await conn.execute(text("""
            CREATE TYPE paymentmethod AS ENUM (
                'direct_deposit', 'check', 'cash'
            )
        """))
        
        await conn.execute(text("""
            ALTER TABLE employee_financials 
            ALTER COLUMN payment_method TYPE paymentmethod 
            USING payment_method::paymentmethod
        """))
        print("✓ Fixed PaymentMethod enum")
        
        await conn.commit()
    
    await engine.dispose()
    print("✓ Enum values fixed successfully")


if __name__ == "__main__":
    asyncio.run(fix_enum())
