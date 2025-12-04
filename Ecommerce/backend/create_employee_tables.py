"""
Create missing employee-related tables.
This script creates all missing database tables for the employee management system.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from database import Base
from sqlalchemy import text

# Import all models to ensure they're registered with Base
from Models.Employee import Employee
from Models.EmployeeFinancial import EmployeeFinancial
from Models.EmployeeSchedule import EmployeeSchedule
from Models.HoursWorked import HoursWorked
from Models.PaidTimeOff import PaidTimeOff
from Models.PaidSick import PaidSick
from Models.TimeOffRequest import TimeOffRequest
from Models.ShiftSwap import ShiftSwap

async def create_tables_for_db(db_url: str, db_name: str):
    """Create all missing tables for a specific database."""
    engine = create_async_engine(db_url, echo=False)
    
    print(f"Creating missing employee-related tables in {db_name}...")
    
    try:
        async with engine.begin() as conn:
            # Create tables
            await conn.run_sync(Base.metadata.create_all)
        
        print(f"[OK] All tables created successfully in {db_name}!")
        
        # Verify tables
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN (
                    'employees', 'employee_financials', 'employee_schedules',
                    'hours_worked', 'paid_time_off', 'paid_sick',
                    'time_off_requests', 'shift_swaps'
                )
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"Verified tables in {db_name}: {', '.join(tables)}")
    finally:
        await engine.dispose()

async def main():
    # Test database only
    test_url = "postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_test"
    await create_tables_for_db(test_url, "ecommerce_test")

if __name__ == "__main__":
    asyncio.run(main())
