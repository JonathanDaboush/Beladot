from decimal import Decimal
from datetime import date, datetime
from typing import Optional


class PaidSick:
    """Business logic for Paid Sick Leave entity."""
    
    def __init__(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        hours_requested: Decimal,
        sick_type: str = "illness",
        reason_notes: Optional[str] = None,
        balance_before: Optional[Decimal] = None
    ):
        self.employee_id = employee_id
        self.start_date = start_date
        self.end_date = end_date
        self.hours_requested = hours_requested
        self.sick_type = sick_type
        self.reason_notes = reason_notes
        self.balance_before = balance_before
    
    def calculate_days_absent(self) -> int:
        """Calculate number of calendar days absent."""
        delta = self.end_date - self.start_date
        return delta.days + 1
    
    def calculate_business_days(self) -> int:
        """Calculate number of business days absent."""
        business_days = 0
        current = self.start_date
        
        while current <= self.end_date:
            if current.weekday() < 5:  # Monday-Friday
                business_days += 1
            current = date.fromordinal(current.toordinal() + 1)
        
        return business_days
    
    def calculate_balance_after(self) -> Optional[Decimal]:
        """Calculate sick leave balance after this request."""
        if self.balance_before is None:
            return None
        return self.balance_before - self.hours_requested
    
    def is_sufficient_balance(self) -> bool:
        """Check if employee has sufficient sick leave balance."""
        if self.balance_before is None:
            return False
        return self.balance_before >= self.hours_requested
    
    def requires_doctors_note(self, threshold_days: int = 3) -> bool:
        """
        Check if sick leave requires doctor's note.
        
        Typically required for absences >= 3 consecutive days.
        """
        return self.calculate_days_absent() >= threshold_days
    
    def is_fmla_eligible(self, days_absent: int = 3) -> bool:
        """
        Check if absence might be FMLA eligible.
        
        FMLA (Family and Medical Leave Act) typically applies for:
        - Serious health conditions
        - Family care
        - 3+ consecutive days with medical treatment
        """
        if self.sick_type in ["injury", "family_care"]:
            return True
        
        if self.calculate_days_absent() >= days_absent:
            return True
        
        return False
    
    def validate_dates(self) -> tuple[bool, str]:
        """
        Validate sick leave dates.
        
        Returns (is_valid, error_message)
        """
        if self.end_date < self.start_date:
            return False, "End date must be on or after start date"
        
        # Sick leave can be reported retroactively (unlike PTO)
        # But should be within reasonable timeframe (e.g., 7 days)
        max_retroactive_days = 7
        if (date.today() - self.start_date).days > max_retroactive_days:
            return False, f"Sick leave must be reported within {max_retroactive_days} days"
        
        return True, ""
    
    def validate_hours(self, hours_per_day: Decimal = Decimal("8")) -> tuple[bool, str]:
        """Validate hours requested are reasonable."""
        business_days = self.calculate_business_days()
        expected_hours = Decimal(str(business_days)) * hours_per_day
        
        # Allow flexibility for partial days, weekends, etc
        min_hours = Decimal("0.5")  # Minimum 0.5 hour
        max_hours = (Decimal(str(business_days)) + Decimal("2")) * hours_per_day
        
        if self.hours_requested < min_hours or self.hours_requested > max_hours:
            return False, f"Hours requested ({self.hours_requested}) is invalid for {business_days} business days"
        
        return True, ""
    
    def is_workers_comp_claim(self) -> bool:
        """Check if sick leave is related to workplace injury (workers' comp)."""
        return self.sick_type == "injury"
    
    def requires_quarantine_documentation(self) -> bool:
        """Check if quarantine-related absence requires documentation."""
        return self.sick_type == "quarantine"
    
    def get_duration_display(self) -> str:
        """Get human-readable duration."""
        days = self.calculate_days_absent()
        business_days = self.calculate_business_days()
        
        if days == 1:
            return f"1 day ({self.hours_requested} hours)"
        else:
            return f"{days} days ({business_days} business days, {self.hours_requested} hours)"
    
    def calculate_intermittent_leave_usage(self, total_hours_used: Decimal, fmla_limit: Decimal = Decimal("480")) -> dict:
        """
        Calculate intermittent FMLA leave usage.
        
        FMLA allows up to 12 weeks (480 hours) of unpaid leave per year.
        """
        hours_remaining = fmla_limit - total_hours_used
        weeks_used = total_hours_used / Decimal("40")
        weeks_remaining = hours_remaining / Decimal("40")
        
        return {
            "total_hours_used": float(total_hours_used),
            "hours_remaining": float(hours_remaining),
            "weeks_used": float(weeks_used),
            "weeks_remaining": float(weeks_remaining),
            "percentage_used": float((total_hours_used / fmla_limit) * 100)
        }
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "employee_id": self.employee_id,
            "sick_type": self.sick_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "hours_requested": float(self.hours_requested),
            "days_absent": self.calculate_days_absent(),
            "business_days": self.calculate_business_days(),
            "reason_notes": self.reason_notes,
            "balance_before": float(self.balance_before) if self.balance_before else None,
            "balance_after": float(self.calculate_balance_after()) if self.calculate_balance_after() else None,
            "requires_doctors_note": self.requires_doctors_note()
        }
