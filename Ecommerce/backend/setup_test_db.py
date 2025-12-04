"""
Setup script to create test database and tables in PostgreSQL.
Run this before running tests.
"""
import asyncio
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

# Import database Base
from database import Base

# Import all models to register them with Base.metadata
import Models  # This imports all models from Models/__init__.py

# Database connection parameters
DB_USER = "postgres"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ecommerce_test"

# URLs
ADMIN_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
TEST_DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
TEST_DB_URL_ASYNC = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def create_database():
    """Create the test database if it doesn't exist."""
    print(f"Connecting to PostgreSQL server at {DB_HOST}:{DB_PORT}...")
    
    try:
        # Connect to postgres database to create our test database
        engine = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
        
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": DB_NAME}
            )
            exists = result.fetchone() is not None
            
            if exists:
                print(f"Database '{DB_NAME}' already exists.")
                # Drop and recreate for clean state
                print(f"Dropping existing database '{DB_NAME}'...")
                conn.execute(text(f'DROP DATABASE "{DB_NAME}"'))
                print("Database dropped.")
            
            print(f"Creating database '{DB_NAME}'...")
            conn.execute(text(f'CREATE DATABASE "{DB_NAME}"'))
            print(f"[OK] Database '{DB_NAME}' created successfully!")
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error creating database: {e}")
        print("\nPlease check:")
        print(f"  1. PostgreSQL is running on {DB_HOST}:{DB_PORT}")
        print(f"  2. User '{DB_USER}' exists with password '{DB_PASSWORD}'")
        print(f"  3. User has permission to create databases")
        return False


async def create_tables():
    """Create all tables in the test database."""
    print(f"\nConnecting to test database '{DB_NAME}'...")
    
    try:
        engine = create_async_engine(TEST_DB_URL_ASYNC, echo=False)
        
        async with engine.begin() as conn:
            print("Dropping existing tables and types if any...")
            # Drop all tables and custom types
            await conn.execute(text("DROP SCHEMA public CASCADE"))
            await conn.execute(text("CREATE SCHEMA public"))
            await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            await conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
            
            print("Creating enum types...")
            # Create enum types before tables to avoid CHECK constraint errors
            await conn.execute(text("""
                CREATE TYPE userrole AS ENUM ('admin', 'customer', 'support')
            """))
            await conn.execute(text("""
                CREATE TYPE orderstatus AS ENUM ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded')
            """))
            await conn.execute(text("""
                CREATE TYPE shipmentstatus AS ENUM ('pending', 'picked', 'packed', 'shipped', 'in_transit', 'out_for_delivery', 'delivered', 'failed')
            """))
            await conn.execute(text("""
                CREATE TYPE paymentstatus AS ENUM ('pending', 'authorized', 'captured', 'failed', 'refunded', 'partially_refunded', 'cancelled')
            """))
            await conn.execute(text("""
                CREATE TYPE returnstatus AS ENUM ('pending', 'approved', 'rejected', 'received', 'refunded', 'cancelled')
            """))
            await conn.execute(text("""
                CREATE TYPE refundstatus AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled')
            """))
            
            print("Creating all tables...")
            await conn.run_sync(Base.metadata.create_all)
            
            # Get table count
            result = await conn.execute(
                text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            )
            table_count = result.scalar()
            print(f"[OK] Successfully created {table_count} tables!")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main setup function."""
    print("=" * 60)
    print("PostgreSQL Test Database Setup")
    print("=" * 60)
    
    # Step 1: Create database
    if not create_database():
        sys.exit(1)
    
    # Step 2: Create tables
    if not await create_tables():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("[OK] Setup completed successfully!")
    print("=" * 60)
    print(f"\nTest database ready at: {TEST_DB_URL}")
    print("\nYou can now run tests with:")
    print("  pytest Tests/")
    

if __name__ == "__main__":
    asyncio.run(main())
