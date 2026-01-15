from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class EmployeeComponent(Base):
    __tablename__ = 'employee_component'
    id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    content = Column(String(1024), nullable=False)
    # New: department_id foreign key
    department_id = Column(Integer, ForeignKey('department.id'), nullable=False)
    department = relationship('Department', back_populates='employee_components')

# In department.py, add:
# employee_components = relationship('EmployeeComponent', back_populates='department')
