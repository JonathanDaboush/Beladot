import asyncio
from datetime import datetime, timedelta
from decimal import Decimal

# Simulate the clock times with a small delay
clock_in = datetime.now()
clock_out = clock_in + timedelta(seconds=0.001)  # 1 millisecond

delta = clock_out - clock_in
hours = Decimal(str(delta.total_seconds() / 3600))

print(f"Clock in: {clock_in}")
print(f"Clock out: {clock_out}")
print(f"Delta: {delta}")
print(f"Total seconds: {delta.total_seconds()}")
print(f"Hours: {hours}")
print(f"Rounded: {round(hours, 2)}")
