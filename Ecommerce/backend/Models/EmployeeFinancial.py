from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class PaymentFrequency(enum.Enum):
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"
    SEMI_MONTHLY = "semi_monthly"
    MONTHLY = "monthly"


class PaymentMethod(enum.Enum):
    DIRECT_DEPOSIT = "direct_deposit"
    CHECK = "check"
    CASH = "cash"


class EmployeeFinancial(Base):
    """
    Employee financial information - bank, tax, and pay rate details.
    
    Separated from main Employee table for security and access control.
    Contains sensitive financial data with restricted access.
    """
    __tablename__ = "employee_financials"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, unique=True, index=True)
    
    # Compensation
    pay_rate = Column(Numeric(10, 2), nullable=False)  # Hourly rate or salary
    pay_rate_currency = Column(String(3), default="CAD", nullable=False)
    is_salary = Column(Boolean, default=False, nullable=False)  # True = salary, False = hourly
    overtime_eligible = Column(Boolean, default=True, nullable=False)
    overtime_rate_multiplier = Column(Numeric(4, 2), default=1.5)  # 1.5x for overtime
    
    # Payment Details
    payment_frequency = Column(Enum(PaymentFrequency, values_callable=lambda x: [e.value for e in x]), nullable=False, default=PaymentFrequency.BI_WEEKLY)
    payment_method = Column(Enum(PaymentMethod, values_callable=lambda x: [e.value for e in x]), nullable=False, default=PaymentMethod.DIRECT_DEPOSIT)
    
    # Banking Information (encrypted in production)
    bank_name = Column(String(100))
    bank_account_number = Column(String(100))  # Should be encrypted
    bank_routing_number = Column(String(50))   # Should be encrypted
    bank_branch = Column(String(100))
    
    # Tax Information
    tax_id_number = Column(String(50))  # SIN (Canada) / SSN (US) - Should be encrypted
    tax_exemptions = Column(Integer, default=0)
    additional_tax_withholding = Column(Numeric(10, 2), default=0.00)
    federal_tax_rate = Column(Numeric(5, 4), default=0.15)  # Federal tax rate (e.g., 0.15 = 15%)
    provincial_tax_rate = Column(Numeric(5, 4), default=0.10)  # Provincial/state tax rate
    cpp_contribution_rate = Column(Numeric(5, 4), default=0.0595)  # Canada Pension Plan rate
    ei_contribution_rate = Column(Numeric(5, 4), default=0.0166)  # Employment Insurance rate
    
    # Benefits Deductions (monthly amounts)
    health_insurance_deduction = Column(Numeric(10, 2), default=0.00)
    retirement_contribution = Column(Numeric(10, 2), default=0.00)
    other_deductions = Column(Numeric(10, 2), default=0.00)
    
    # Emergency Contact for Financial Issues
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relationship = Column(String(50))
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="financial_info")
    
    def __repr__(self):
        return f"<EmployeeFinancial employee_id={self.employee_id}>"
