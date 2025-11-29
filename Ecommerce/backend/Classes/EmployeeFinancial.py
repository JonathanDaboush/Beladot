from decimal import Decimal
from typing import Optional


class EmployeeFinancial:
    """Business logic for Employee Financial entity."""
    
    def __init__(
        self,
        employee_id: int,
        pay_rate: Decimal,
        is_salary: bool = False,
        overtime_eligible: bool = True,
        payment_frequency: str = "bi_weekly",
        payment_method: str = "direct_deposit",
        bank_name: Optional[str] = None,
        bank_account_number: Optional[str] = None,
        tax_exemptions: int = 0
    ):
        self.employee_id = employee_id
        self.pay_rate = pay_rate
        self.is_salary = is_salary
        self.overtime_eligible = overtime_eligible
        self.payment_frequency = payment_frequency
        self.payment_method = payment_method
        self.bank_name = bank_name
        self.bank_account_number = bank_account_number
        self.tax_exemptions = tax_exemptions
    
    def calculate_gross_pay(
        self, 
        regular_hours: Decimal = Decimal("0"),
        overtime_hours: Decimal = Decimal("0"),
        overtime_multiplier: Decimal = Decimal("1.5")
    ) -> Decimal:
        """
        Calculate gross pay for a pay period.
        
        For hourly: (regular_hours * rate) + (overtime_hours * rate * multiplier)
        For salary: annual_salary / pay_periods_per_year
        """
        if self.is_salary:
            # Convert annual salary to pay period amount
            pay_periods_per_year = self._get_pay_periods_per_year()
            return self.pay_rate / Decimal(str(pay_periods_per_year))
        else:
            regular_pay = regular_hours * self.pay_rate
            overtime_pay = overtime_hours * self.pay_rate * overtime_multiplier
            return regular_pay + overtime_pay
    
    def _get_pay_periods_per_year(self) -> int:
        """Get number of pay periods per year based on frequency."""
        frequency_map = {
            "weekly": 52,
            "bi_weekly": 26,
            "semi_monthly": 24,
            "monthly": 12
        }
        return frequency_map.get(self.payment_frequency, 26)
    
    def calculate_federal_tax(self, gross_pay: Decimal) -> Decimal:
        """
        Calculate federal income tax (simplified Canadian tax).
        
        This is a simplified calculation. Production systems should use
        official CRA tax tables or a proper payroll service.
        """
        # Basic Canadian federal tax brackets (2025)
        taxable_income = gross_pay
        
        if taxable_income <= Decimal("0"):
            return Decimal("0")
        
        # Simplified: ~15% effective rate for demonstration
        # Real implementation needs proper CRA tables
        return round(taxable_income * Decimal("0.15"), 2)
    
    def calculate_cpp_deduction(self, gross_pay: Decimal, ytd_cpp: Decimal = Decimal("0")) -> Decimal:
        """
        Calculate Canada Pension Plan (CPP) contribution.
        
        2025 Rate: 5.95% on earnings between $3,500 and $68,500
        Max annual contribution: ~$3,867.50
        """
        cpp_rate = Decimal("0.0595")
        max_annual_cpp = Decimal("3867.50")
        
        if ytd_cpp >= max_annual_cpp:
            return Decimal("0")
        
        cpp_contribution = gross_pay * cpp_rate
        
        # Don't exceed annual max
        remaining_allowed = max_annual_cpp - ytd_cpp
        return min(cpp_contribution, remaining_allowed)
    
    def calculate_ei_deduction(self, gross_pay: Decimal, ytd_ei: Decimal = Decimal("0")) -> Decimal:
        """
        Calculate Employment Insurance (EI) premium.
        
        2025 Rate: 1.66% on insurable earnings
        Max annual insurable: $63,200
        Max annual premium: ~$1,049
        """
        ei_rate = Decimal("0.0166")
        max_annual_ei = Decimal("1049.00")
        
        if ytd_ei >= max_annual_ei:
            return Decimal("0")
        
        ei_premium = gross_pay * ei_rate
        
        remaining_allowed = max_annual_ei - ytd_ei
        return min(ei_premium, remaining_allowed)
    
    def calculate_net_pay(
        self,
        gross_pay: Decimal,
        ytd_cpp: Decimal = Decimal("0"),
        ytd_ei: Decimal = Decimal("0"),
        other_deductions: Decimal = Decimal("0")
    ) -> dict:
        """
        Calculate net pay after all deductions.
        
        Returns breakdown of gross, deductions, and net.
        """
        federal_tax = self.calculate_federal_tax(gross_pay)
        cpp = self.calculate_cpp_deduction(gross_pay, ytd_cpp)
        ei = self.calculate_ei_deduction(gross_pay, ytd_ei)
        
        total_deductions = federal_tax + cpp + ei + other_deductions
        net_pay = gross_pay - total_deductions
        
        return {
            "gross_pay": float(gross_pay),
            "federal_tax": float(federal_tax),
            "cpp_contribution": float(cpp),
            "ei_premium": float(ei),
            "other_deductions": float(other_deductions),
            "total_deductions": float(total_deductions),
            "net_pay": float(net_pay)
        }
    
    def mask_account_number(self) -> str:
        """Mask bank account number for display (show last 4 digits)."""
        if not self.bank_account_number or len(self.bank_account_number) < 4:
            return "****"
        return "****" + self.bank_account_number[-4:]
    
    def to_dict(self, include_sensitive: bool = False):
        """Convert to dictionary. Sensitive data only if explicitly requested."""
        base_data = {
            "employee_id": self.employee_id,
            "pay_rate": float(self.pay_rate),
            "is_salary": self.is_salary,
            "overtime_eligible": self.overtime_eligible,
            "payment_frequency": self.payment_frequency,
            "payment_method": self.payment_method,
            "bank_name": self.bank_name,
            "tax_exemptions": self.tax_exemptions
        }
        
        if include_sensitive:
            base_data["bank_account_number"] = self.bank_account_number
        else:
            base_data["bank_account_number_masked"] = self.mask_account_number()
        
        return base_data
