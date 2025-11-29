from decimal import Decimal
from datetime import datetime, date, time
from typing import Optional


class HoursWorked:
    """Business logic for Hours Worked entity."""
    
    def __init__(
        self,
        employee_id: int,
        work_date: date,
        regular_hours: Decimal = Decimal("0"),
        overtime_hours: Decimal = Decimal("0"),
        double_time_hours: Decimal = Decimal("0"),
        holiday_hours: Decimal = Decimal("0"),
        clock_in: Optional[datetime] = None,
        clock_out: Optional[datetime] = None,
        notes: Optional[str] = None
    ):
        self.employee_id = employee_id
        self.work_date = work_date
        self.regular_hours = regular_hours
        self.overtime_hours = overtime_hours
        self.double_time_hours = double_time_hours
        self.holiday_hours = holiday_hours
        self.clock_in = clock_in
        self.clock_out = clock_out
        self.notes = notes
    
    def calculate_total_hours(self) -> Decimal:
        """Calculate total hours worked."""
        return (
            self.regular_hours + 
            self.overtime_hours + 
            self.double_time_hours + 
            self.holiday_hours
        )
    
    def calculate_hours_from_clock_times(self) -> Decimal:
        """
        Calculate hours from clock in/out times.
        Returns total hours worked (including breaks subtraction if needed).
        """
        if not self.clock_in or not self.clock_out:
            return Decimal("0")
        
        delta = self.clock_out - self.clock_in
        hours = Decimal(str(delta.total_seconds() / 3600))
        
        # Subtract lunch break if shift > 6 hours
        if hours > Decimal("6"):
            hours -= Decimal("0.5")  # 30-minute unpaid lunch
        
        return round(hours, 2)
    
    def split_regular_and_overtime(self, max_regular_hours: Decimal = Decimal("8")) -> dict:
        """
        Split total hours into regular and overtime.
        
        Standard: First 8 hours = regular, beyond that = overtime.
        Returns dict with regular_hours and overtime_hours.
        """
        total = self.calculate_hours_from_clock_times()
        
        if total <= max_regular_hours:
            return {
                "regular_hours": total,
                "overtime_hours": Decimal("0")
            }
        else:
            return {
                "regular_hours": max_regular_hours,
                "overtime_hours": total - max_regular_hours
            }
    
    def is_weekend(self) -> bool:
        """Check if work date falls on weekend."""
        return self.work_date.weekday() >= 5  # 5=Saturday, 6=Sunday
    
    def is_holiday(self, holidays: list) -> bool:
        """
        Check if work date is a statutory holiday.
        
        Args:
            holidays: List of date objects representing statutory holidays
        """
        return self.work_date in holidays
    
    def calculate_weighted_hours(self, overtime_multiplier: Decimal = Decimal("1.5")) -> Decimal:
        """
        Calculate hours weighted by pay multiplier.
        Used for total compensation calculation.
        
        Example: 8 regular + 2 overtime @1.5x = 8 + (2 * 1.5) = 11 weighted hours
        """
        weighted = self.regular_hours
        weighted += self.overtime_hours * overtime_multiplier
        weighted += self.double_time_hours * Decimal("2.0")
        weighted += self.holiday_hours * Decimal("2.0")  # Holiday pay typically 2x
        
        return weighted
    
    def validate_hours(self, max_daily_hours: Decimal = Decimal("16")) -> tuple[bool, str]:
        """
        Validate hours worked are reasonable.
        
        Returns (is_valid, error_message)
        """
        total = self.calculate_total_hours()
        
        if total <= Decimal("0"):
            return False, "Total hours must be greater than 0"
        
        if total > max_daily_hours:
            return False, f"Total hours ({total}) exceeds maximum daily hours ({max_daily_hours})"
        
        if self.clock_in and self.clock_out:
            if self.clock_out <= self.clock_in:
                return False, "Clock out time must be after clock in time"
        
        return True, ""
    
    def get_shift_duration_display(self) -> str:
        """Get human-readable shift duration."""
        if not self.clock_in or not self.clock_out:
            return "N/A"
        
        delta = self.clock_out - self.clock_in
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        
        return f"{hours}h {minutes}m"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "employee_id": self.employee_id,
            "work_date": self.work_date.isoformat() if self.work_date else None,
            "clock_in": self.clock_in.isoformat() if self.clock_in else None,
            "clock_out": self.clock_out.isoformat() if self.clock_out else None,
            "regular_hours": float(self.regular_hours),
            "overtime_hours": float(self.overtime_hours),
            "double_time_hours": float(self.double_time_hours),
            "holiday_hours": float(self.holiday_hours),
            "total_hours": float(self.calculate_total_hours()),
            "notes": self.notes
        }
