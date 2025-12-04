import asyncio
from database import async_engine
from sqlalchemy import inspect, text

async def check_tables():
    async with async_engine.connect() as conn:
        result = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        print("Existing tables:")
        for table in sorted(result):
            print(f"  - {table}")
        
        # Check for missing employee tables
        missing = []
        required = ['employees', 'employee_financial', 'hours_worked', 'paid_time_off', 'paid_sick', 'employee_schedule', 'shift_swaps', 'time_off_requests']
        for table in required:
            if table not in result:
                missing.append(table)
        
        if missing:
            print(f"\nMissing tables: {', '.join(missing)}")
        else:
            print("\nAll required tables exist!")

asyncio.run(check_tables())
