from decimal import Decimal
from datetime import date, datetime
from typing import Optional


class PaidTimeOff:
    """Business logic for Paid Time Off (PTO) entity."""
    
    def __init__(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        hours_requested: Decimal,
        pto_type: str = "vacation",
        request_notes: Optional[str] = None,
        balance_before: Optional[Decimal] = None
    ):
        self.employee_id = employee_id
        self.start_date = start_date
        self.end_date = end_date
        self.hours_requested = hours_requested
        self.pto_type = pto_type
        self.request_notes = request_notes
        self.balance_before = balance_before
    
    def calculate_days_requested(self) -> int:
        """Calculate number of calendar days requested."""
        delta = self.end_date - self.start_date
        return delta.days + 1  # Include both start and end date
    
    def calculate_business_days(self) -> int:
        """Calculate number of business days (Monday-Friday) requested."""
        business_days = 0
        current = self.start_date
        
        while current <= self.end_date:
            if current.weekday() < 5:  # Monday=0, Friday=4
                business_days += 1
            current = date.fromordinal(current.toordinal() + 1)
        
        return business_days
    
    def calculate_balance_after(self) -> Optional[Decimal]:
        """Calculate balance after this PTO request."""
        if self.balance_before is None:
            return None
        return self.balance_before - self.hours_requested
    
    def is_sufficient_balance(self) -> bool:
        """Check if employee has sufficient PTO balance."""
        if self.balance_before is None:
            return False
        return self.balance_before >= self.hours_requested
    
    def validate_dates(self) -> tuple[bool, str]:
        """
        Validate PTO request dates.
        
        Returns (is_valid, error_message)
        """
        if self.end_date < self.start_date:
            return False, "End date must be on or after start date"
        
        # Check if dates are in the past
        if self.start_date < date.today():
            return False, "Cannot request PTO for past dates"
        
        # Check if request is too far in advance (1 year)
        max_advance_days = 365
        if (self.start_date - date.today()).days > max_advance_days:
            return False, f"Cannot request PTO more than {max_advance_days} days in advance"
        
        return True, ""
    
    def validate_hours(self, hours_per_day: Decimal = Decimal("8")) -> tuple[bool, str]:
        """
        Validate hours requested are reasonable.
        
        Args:
            hours_per_day: Standard work hours per day (default 8)
        """
        business_days = self.calculate_business_days()
        expected_hours = Decimal(str(business_days)) * hours_per_day
        
        # Allow significant flexibility for partial days, weekends, etc (±2 days)
        min_hours = max(Decimal("0"), (Decimal(str(business_days)) - Decimal("2")) * hours_per_day)
        max_hours = (Decimal(str(business_days)) + Decimal("2")) * hours_per_day
        
        if self.hours_requested < min_hours or self.hours_requested > max_hours:
            return False, f"Hours requested ({self.hours_requested}) doesn't match business days ({business_days} days = ~{expected_hours} hours)"
        
        return True, ""
    
    def requires_advanced_approval(self, days_notice: int = 14) -> bool:
        """
        Check if PTO request requires advanced approval.
        
        Typically, requests within 2 weeks need manager escalation.
        """
        days_until_start = (self.start_date - date.today()).days
        return days_until_start < days_notice
    
    def get_duration_display(self) -> str:
        """Get human-readable duration."""
        days = self.calculate_days_requested()
        business_days = self.calculate_business_days()
        
        if days == 1:
            return f"1 day ({self.hours_requested} hours)"
        else:
            return f"{days} days ({business_days} business days, {self.hours_requested} hours)"
    
    def conflicts_with_blackout_dates(self, blackout_periods: list) -> bool:
        """
        Check if PTO request conflicts with company blackout dates.
        
        Args:
            blackout_periods: List of (start_date, end_date) tuples
        """
        for blackout_start, blackout_end in blackout_periods:
            # Check for any overlap
            if not (self.end_date < blackout_start or self.start_date > blackout_end):
                return True
        return False
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "employee_id": self.employee_id,
            "pto_type": self.pto_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "hours_requested": float(self.hours_requested),
            "days_requested": self.calculate_days_requested(),
            "business_days": self.calculate_business_days(),
            "request_notes": self.request_notes,
            "balance_before": float(self.balance_before) if self.balance_before else None,
            "balance_after": float(self.calculate_balance_after()) if self.calculate_balance_after() else None
        }
