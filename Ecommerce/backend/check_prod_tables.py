"""Quick script to check production database tables."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    engine = create_async_engine(os.getenv('DATABASE_URL'), echo=False)
    
    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
        )
        tables = [row[0] for row in result]
        
        print(f"\n✓ Found {len(tables)} tables in production database (ecommerce_db):\n")
        for table in tables:
            print(f"  - {table}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
