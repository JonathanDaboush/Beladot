"""Add unpaid_break_minutes column to hours_worked table."""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Use test database
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_test"
async_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def add_column():
    """Add unpaid_break_minutes column."""
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text("""
                ALTER TABLE hours_worked 
                ADD COLUMN IF NOT EXISTS unpaid_break_minutes INTEGER DEFAULT 0 NOT NULL
            """))
            await session.commit()
            print("✓ Added unpaid_break_minutes column to hours_worked table in test database")
        except Exception as e:
            print(f"✗ Error: {e}")
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(add_column())
