from sqlalchemy import Column, Integer, String, Date, Enum, DateTime, Boolean, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
from database import Base


class EmploymentStatus(enum.Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"


class EmploymentType(enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    SEASONAL = "seasonal"


class Employee(Base):
    """
    Core employee identity, position, and location.
    
    Stores essential employee information including personal details,
    employment status, and organizational placement.
    """
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    
    # Employment Details
    employee_number = Column(String(50), unique=True, nullable=False, index=True)
    position = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    employment_type = Column(Enum(EmploymentType), nullable=False, default=EmploymentType.FULL_TIME)
    employment_status = Column(Enum(EmploymentStatus), nullable=False, default=EmploymentStatus.ACTIVE)
    
    # Dates
    hire_date = Column(Date, nullable=False, default=date.today)
    termination_date = Column(Date, nullable=True)
    
    # Location Information
    work_location = Column(String(200))  # Office/warehouse address
    work_city = Column(String(100))
    work_state = Column(String(50))
    work_country = Column(String(50), default="CA")
    work_postal_code = Column(String(20))
    
    # Manager/Reporting
    manager_id = Column(Integer, nullable=True)  # ID of manager employee
    
    # Leave Balances (hours)
    pto_balance = Column(Numeric(7, 2), default=0.0, nullable=False)
    sick_balance = Column(Numeric(7, 2), default=0.0, nullable=False)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    financial_info = relationship("EmployeeFinancial", back_populates="employee", uselist=False)
    hours_worked = relationship("HoursWorked", back_populates="employee")
    paid_time_off = relationship("PaidTimeOff", back_populates="employee")
    paid_sick = relationship("PaidSick", back_populates="employee")
    
    def __repr__(self):
        return f"<Employee {self.employee_number}: {self.first_name} {self.last_name}>"
