from datetime import date, datetime
from typing import Optional


class Employee:
    """Business logic for Employee entity."""
    
    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        employee_number: str,
        position: str,
        department: str,
        hire_date: date,
        phone: Optional[str] = None,
        employment_type: str = "full_time",
        work_location: Optional[str] = None,
        work_city: Optional[str] = None,
        work_state: Optional[str] = None,
        work_country: str = "CA",
        manager_id: Optional[int] = None
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.employee_number = employee_number
        self.position = position
        self.department = department
        self.employment_type = employment_type
        self.hire_date = hire_date
        self.work_location = work_location
        self.work_city = work_city
        self.work_state = work_state
        self.work_country = work_country
        self.manager_id = manager_id
    
    def get_full_name(self) -> str:
        """Return employee's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def get_years_of_service(self) -> int:
        """Calculate years of service."""
        today = date.today()
        years = today.year - self.hire_date.year
        if (today.month, today.day) < (self.hire_date.month, self.hire_date.day):
            years -= 1
        return years
    
    def is_eligible_for_benefits(self) -> bool:
        """Check if employee is eligible for benefits (90 days of employment)."""
        days_employed = (date.today() - self.hire_date).days
        return days_employed >= 90
    
    def calculate_pto_accrual_rate(self) -> float:
        """
        Calculate PTO accrual rate based on years of service.
        Returns hours per pay period (assuming bi-weekly).
        
        0-2 years: 80 hours/year (3.08 hours per pay period)
        3-5 years: 120 hours/year (4.62 hours per pay period)
        6+ years: 160 hours/year (6.15 hours per pay period)
        """
        years = self.get_years_of_service()
        
        if years < 3:
            annual_hours = 80
        elif years < 6:
            annual_hours = 120
        else:
            annual_hours = 160
        
        # 26 pay periods per year for bi-weekly
        return round(annual_hours / 26, 2)
    
    def calculate_sick_accrual_rate(self) -> float:
        """
        Calculate sick leave accrual rate.
        Standard: 40 hours/year (1.54 hours per pay period)
        """
        annual_hours = 40
        return round(annual_hours / 26, 2)
    
    def validate_email(self) -> bool:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, self.email))
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "employee_number": self.employee_number,
            "position": self.position,
            "department": self.department,
            "employment_type": self.employment_type,
            "hire_date": self.hire_date.isoformat() if self.hire_date else None,
            "work_location": self.work_location,
            "work_city": self.work_city,
            "work_state": self.work_state,
            "work_country": self.work_country,
            "manager_id": self.manager_id
        }
