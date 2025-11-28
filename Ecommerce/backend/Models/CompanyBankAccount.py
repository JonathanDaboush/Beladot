from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class CompanyBankAccount(Base):
    __tablename__ = 'company_bank_accounts'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_number = Column(String(255), nullable=False)
    routing_number = Column(String(255), nullable=False)
    bank_name = Column(String(255), nullable=False)
    account_holder_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
