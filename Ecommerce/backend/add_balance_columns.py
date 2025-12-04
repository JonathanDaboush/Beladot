"""Add pto_balance and sick_balance columns to employees table."""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def add_balance_columns():
    # Use test database URL directly
    test_db_url = "postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_test"
    engine = create_async_engine(test_db_url)
    
    async with engine.connect() as conn:
        # Add pto_balance column
        try:
            await conn.execute(text("""
                ALTER TABLE employees 
                ADD COLUMN pto_balance NUMERIC(7, 2) DEFAULT 0.0 NOT NULL
            """))
            print("✓ Added pto_balance column")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ pto_balance column already exists")
            else:
                raise
        
        # Add sick_balance column
        try:
            await conn.execute(text("""
                ALTER TABLE employees 
                ADD COLUMN sick_balance NUMERIC(7, 2) DEFAULT 0.0 NOT NULL
            """))
            print("✓ Added sick_balance column")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ sick_balance column already exists")
            else:
                raise
        
        await conn.commit()
    await engine.dispose()
    print("✓ Balance columns added to TEST database successfully")


if __name__ == "__main__":
    asyncio.run(add_balance_columns())
