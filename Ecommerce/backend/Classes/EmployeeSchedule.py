"""
Employee Schedule Business Logic

Handles shift calculations, overlap detection, and coverage management.
"""

from datetime import datetime, time, date, timedelta
from typing import List, Tuple, Dict


class EmployeeSchedule:
    """Business logic for employee schedules."""
    
    def __init__(
        self,
        employee_id: int,
        shift_date: date,
        shift_start: time,
        shift_end: time,
        shift_type: str = "full_day",
        unpaid_break_minutes: int = 30,
        paid_break_minutes: int = 15
    ):
        self.employee_id = employee_id
        self.shift_date = shift_date
        self.shift_start = shift_start
        self.shift_end = shift_end
        self.shift_type = shift_type
        self.unpaid_break_minutes = unpaid_break_minutes
        self.paid_break_minutes = paid_break_minutes
    
    def calculate_shift_duration(self) -> float:
        """
        Calculate total shift duration in hours.
        
        Returns hours including break time.
        """
        # Combine date and time for calculation
        start_dt = datetime.combine(self.shift_date, self.shift_start)
        end_dt = datetime.combine(self.shift_date, self.shift_end)
        
        # Handle overnight shifts
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)
        
        duration = end_dt - start_dt
        hours = duration.total_seconds() / 3600
        
        return round(hours, 2)
    
    def calculate_working_hours(self) -> float:
        """
        Calculate actual working hours (minus breaks).
        
        Returns net working hours.
        """
        total_hours = self.calculate_shift_duration()
        total_break_hours = (self.unpaid_break_minutes + self.paid_break_minutes) / 60
        
        working_hours = total_hours - (self.unpaid_break_minutes / 60)
        
        return round(working_hours, 2)
    
    def calculate_paid_hours(self) -> float:
        """
        Calculate paid hours (includes paid breaks).
        
        Returns hours to be paid.
        """
        total_hours = self.calculate_shift_duration()
        unpaid_break_hours = self.unpaid_break_minutes / 60
        
        paid_hours = total_hours - unpaid_break_hours
        
        return round(paid_hours, 2)
    
    def overlaps_with(
        self,
        other_start: time,
        other_end: time,
        other_date: date
    ) -> bool:
        """
        Check if this shift overlaps with another time range.
        
        Returns True if there's any overlap.
        """
        if self.shift_date != other_date:
            return False
        
        # Convert to datetime for comparison
        start1 = datetime.combine(self.shift_date, self.shift_start)
        end1 = datetime.combine(self.shift_date, self.shift_end)
        start2 = datetime.combine(other_date, other_start)
        end2 = datetime.combine(other_date, other_end)
        
        # Handle overnight shifts
        if end1 <= start1:
            end1 += timedelta(days=1)
        if end2 <= start2:
            end2 += timedelta(days=1)
        
        # Check overlap
        return start1 < end2 and start2 < end1
    
    def is_valid_shift_length(self) -> Tuple[bool, str]:
        """
        Validate shift length is reasonable.
        
        Returns (is_valid, error_message).
        """
        duration = self.calculate_shift_duration()
        
        if duration < 0.5:
            return False, "Shift must be at least 30 minutes"
        
        if duration > 16:
            return False, "Shift cannot exceed 16 hours"
        
        if duration > 6 and self.unpaid_break_minutes < 30:
            return False, "Shifts over 6 hours require 30-minute lunch break"
        
        return True, ""
    
    def requires_overtime_pay(self, weekly_hours: float) -> bool:
        """
        Check if this shift pushes into overtime.
        
        Args:
            weekly_hours: Total hours worked this week before this shift
        
        Returns True if overtime applies.
        """
        shift_hours = self.calculate_paid_hours()
        total_weekly = weekly_hours + shift_hours
        
        # Standard overtime threshold is 40 hours per week
        return total_weekly > 40
    
    def calculate_shift_cost(
        self,
        hourly_rate: float,
        overtime_multiplier: float = 1.5
    ) -> Dict:
        """
        Calculate cost of this shift.
        
        Returns breakdown of regular and overtime costs.
        """
        paid_hours = self.calculate_paid_hours()
        
        # For now, assume all hours are regular (would need weekly context for overtime)
        regular_hours = paid_hours
        overtime_hours = 0.0
        
        regular_cost = regular_hours * hourly_rate
        overtime_cost = overtime_hours * hourly_rate * overtime_multiplier
        
        return {
            "regular_hours": regular_hours,
            "overtime_hours": overtime_hours,
            "regular_cost": round(regular_cost, 2),
            "overtime_cost": round(overtime_cost, 2),
            "total_cost": round(regular_cost + overtime_cost, 2)
        }
    
    def is_late_night_shift(self) -> bool:
        """Check if shift includes late night hours (10 PM - 6 AM)."""
        # Check if shift starts or ends in late night window
        late_night_start = time(22, 0)  # 10 PM
        late_night_end = time(6, 0)     # 6 AM
        
        if self.shift_start >= late_night_start or self.shift_start < late_night_end:
            return True
        if self.shift_end >= late_night_start or self.shift_end < late_night_end:
            return True
        
        return False
    
    def get_shift_display(self) -> str:
        """Get human-readable shift time display."""
        start_str = self.shift_start.strftime("%I:%M %p")
        end_str = self.shift_end.strftime("%I:%M %p")
        hours = self.calculate_paid_hours()
        
        return f"{start_str} - {end_str} ({hours}h)"
