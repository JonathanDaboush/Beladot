"""
Setup script to create/update production database schema.
This script will sync your production database with the test database schema.
Run this to ensure all tables, columns, and enums are properly configured.
"""
import asyncio
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import database Base
from database import Base

# Import all models to register them with Base.metadata
import Models  # This imports all models from Models/__init__.py

# Get database credentials from environment
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC")

if not DATABASE_URL or not DATABASE_URL_SYNC:
    print("[ERROR] DATABASE_URL or DATABASE_URL_SYNC not found in .env file")
    sys.exit(1)

# Extract connection details from URL
# Format: postgresql://user:password@host:port/dbname
import re
match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL_SYNC)
if not match:
    print("[ERROR] Invalid DATABASE_URL_SYNC format")
    sys.exit(1)

DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME = match.groups()

ADMIN_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"


def check_database_exists():
    """Check if the production database exists."""
    print(f"Checking if database '{DB_NAME}' exists...")
    
    try:
        engine = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
        
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": DB_NAME}
            )
            exists = result.fetchone() is not None
        
        engine.dispose()
        return exists
        
    except Exception as e:
        print(f"[ERROR] Error checking database: {e}")
        return False


def create_database():
    """Create the production database if it doesn't exist."""
    print(f"Connecting to PostgreSQL server at {DB_HOST}:{DB_PORT}...")
    
    try:
        engine = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
        
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": DB_NAME}
            )
            exists = result.fetchone() is not None
            
            if exists:
                print(f"[OK] Database '{DB_NAME}' already exists.")
            else:
                print(f"Creating database '{DB_NAME}'...")
                conn.execute(text(f'CREATE DATABASE "{DB_NAME}"'))
                print(f"[OK] Database '{DB_NAME}' created successfully!")
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error with database: {e}")
        print("\nPlease check:")
        print(f"  1. PostgreSQL is running on {DB_HOST}:{DB_PORT}")
        print(f"  2. User '{DB_USER}' exists with password")
        print(f"  3. User has permission to create databases")
        return False


async def create_enums():
    """Create all required enum types."""
    print("\nCreating/updating enum types...")
    
    enums_to_create = {
        'userrole': ['admin', 'customer', 'support'],
        'orderstatus': ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'],
        'shipmentstatus': ['pending', 'picked', 'packed', 'shipped', 'in_transit', 'out_for_delivery', 'delivered', 'failed'],
        'paymentstatus': ['pending', 'authorized', 'captured', 'failed', 'refunded', 'partially_refunded', 'cancelled'],
        'returnstatus': ['pending', 'approved', 'rejected', 'received', 'refunded', 'cancelled'],
        'refundstatus': ['pending', 'processing', 'completed', 'failed', 'cancelled'],
        'ptostatus': ['pending', 'approved', 'denied', 'cancelled'],
        'sickstatus': ['pending', 'approved', 'denied', 'cancelled'],
        'jobstatus': ['open', 'filled', 'closed', 'cancelled'],
        'paymentmethod': ['credit_card', 'debit_card', 'paypal', 'bank_transfer', 'cash', 'other'],
        'paymentfrequency': ['weekly', 'biweekly', 'semimonthly', 'monthly']
    }
    
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        
        async with engine.begin() as conn:
            for enum_name, enum_values in enums_to_create.items():
                # Check if enum exists
                result = await conn.execute(
                    text("SELECT 1 FROM pg_type WHERE typname = :typename"),
                    {"typename": enum_name}
                )
                exists = result.fetchone() is not None
                
                if not exists:
                    values_str = "', '".join(enum_values)
                    await conn.execute(text(f"CREATE TYPE {enum_name} AS ENUM ('{values_str}')"))
                    print(f"  ✓ Created enum: {enum_name}")
                else:
                    print(f"  ✓ Enum exists: {enum_name}")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error creating enums: {e}")
        import traceback
        traceback.print_exc()
        return False


async def create_or_update_tables():
    """Create all tables and add missing columns."""
    print("\nCreating/updating tables...")
    
    try:
        engine = create_async_engine(DATABASE_URL, echo=True)
        
        async with engine.begin() as conn:
            # Create all tables (won't affect existing tables)
            print("  Creating any missing tables...")
            print(f"  Found {len(Base.metadata.tables)} tables in metadata")
            
            # Use run_sync to execute create_all with the connection
            def create_all_tables(connection):
                Base.metadata.create_all(bind=connection)
            
            await conn.run_sync(create_all_tables)
            
            # Add missing columns to existing tables
            print("\n  Checking for missing columns...")
            
            # Employee table columns (using correct pluralized table names)
            await add_column_if_not_exists(conn, 'employees', 'balance_hours', 'NUMERIC(10, 2) DEFAULT 0')
            await add_column_if_not_exists(conn, 'employees', 'balance_amount', 'INTEGER DEFAULT 0')
            
            # Employee Schedule table
            await add_column_if_not_exists(conn, 'employee_schedules', 'break_minutes', 'INTEGER DEFAULT 0')
            
            # Order table
            await add_column_if_not_exists(conn, 'orders', 'idempotency_key', 'VARCHAR(255)')
            
            # Payment table
            await add_column_if_not_exists(conn, 'payments', 'tax_amount_cents', 'INTEGER DEFAULT 0')
            
            # Get table count
            result = await conn.execute(
                text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'")
            )
            table_count = result.scalar()
            print(f"\n[OK] Database has {table_count} tables!")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error creating/updating tables: {e}")
        import traceback
        traceback.print_exc()
        return False


async def add_column_if_not_exists(conn, table_name, column_name, column_definition):
    """Add a column to a table if it doesn't exist."""
    try:
        # Check if column exists
        result = await conn.execute(
            text("""
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = :table_name AND column_name = :column_name
            """),
            {"table_name": table_name, "column_name": column_name}
        )
        exists = result.fetchone() is not None
        
        if not exists:
            # Check if table exists first
            result = await conn.execute(
                text("SELECT 1 FROM information_schema.tables WHERE table_name = :table_name"),
                {"table_name": table_name}
            )
            table_exists = result.fetchone() is not None
            
            if table_exists:
                await conn.execute(
                    text(f'ALTER TABLE "{table_name}" ADD COLUMN {column_name} {column_definition}')
                )
                print(f"  ✓ Added column: {table_name}.{column_name}")
            else:
                print(f"  ⚠ Table {table_name} doesn't exist yet, will be created")
        else:
            print(f"  ✓ Column exists: {table_name}.{column_name}")
    except Exception as e:
        print(f"  ⚠ Could not add {table_name}.{column_name}: {e}")


async def verify_schema():
    """Verify the schema is correct."""
    print("\nVerifying schema...")
    
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        
        async with engine.begin() as conn:
            # Check for employee tables (using correct pluralized names)
            tables_to_check = [
                'employees', 'employee_financials', 'employee_schedules', 
                'hours_worked', 'paid_time_off', 'paid_sick', 'jobs',
                'users', 'products', 'orders', 'payments', 'shipments'
            ]
            
            missing_tables = []
            for table in tables_to_check:
                result = await conn.execute(
                    text("SELECT 1 FROM information_schema.tables WHERE table_name = :table_name"),
                    {"table_name": table}
                )
                if not result.fetchone():
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"  ⚠ Missing tables: {', '.join(missing_tables)}")
                return False
            else:
                print("  ✓ All critical tables exist")
            
            # Check for critical columns
            columns_to_check = [
                ('employees', 'balance_hours'),
                ('employees', 'balance_amount'),
                ('employee_schedules', 'break_minutes'),
            ]
            
            missing_columns = []
            for table, column in columns_to_check:
                result = await conn.execute(
                    text("""
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = :table_name AND column_name = :column_name
                    """),
                    {"table_name": table, "column_name": column}
                )
                if not result.fetchone():
                    missing_columns.append(f"{table}.{column}")
            
            if missing_columns:
                print(f"  ⚠ Missing columns: {', '.join(missing_columns)}")
                return False
            else:
                print("  ✓ All critical columns exist")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error verifying schema: {e}")
        return False


async def main():
    """Main setup function."""
    print("=" * 70)
    print("PostgreSQL Production Database Setup")
    print("=" * 70)
    print(f"Target Database: {DB_NAME}")
    print(f"Host: {DB_HOST}:{DB_PORT}")
    print(f"User: {DB_USER}")
    print("=" * 70)
    
    # Confirm action
    print("\n⚠️  WARNING: This will modify your production database!")
    print("   - Create missing tables")
    print("   - Add missing columns to existing tables")
    print("   - Create missing enum types")
    print("   - Existing data will NOT be deleted")
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Operation cancelled.")
        sys.exit(0)
    
    # Step 1: Check/Create database
    if not create_database():
        sys.exit(1)
    
    # Step 2: Create enum types
    if not await create_enums():
        sys.exit(1)
    
    # Step 3: Create/Update tables
    if not await create_or_update_tables():
        sys.exit(1)
    
    # Step 4: Verify schema
    if not await verify_schema():
        print("\n⚠️  Schema verification found issues, but setup may have been partially successful.")
    
    print("\n" + "=" * 70)
    print("[OK] Production database setup completed!")
    print("=" * 70)
    print(f"\nDatabase ready at: {DATABASE_URL_SYNC}")
    print("\nYou can now run your application with:")
    print("  python app.py")
    print("\nOr test with:")
    print("  pytest Tests/")
    

if __name__ == "__main__":
    asyncio.run(main())
