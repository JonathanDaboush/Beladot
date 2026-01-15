from pydantic import BaseModel, Field
from typing import Optional

class FinanceIssueCreate(BaseModel):
    employee_id: int
    description: str
    cost: float
    date: str  # ISO format
    status: str

class FinanceIssueUpdate(BaseModel):
    description: Optional[str] = None
    cost: Optional[float] = None
    date: Optional[str] = None
    status: Optional[str] = None

class FinanceIssueResponse(BaseModel):
    incident_id: int
    employee_id: int
    description: str
    cost: float
    date: str
    status: str

class FinanceReimbursementUpdate(BaseModel):
    amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class FinanceReimbursementResponse(BaseModel):
    reimbursement_id: int
    employee_id: int
    amount: float
    status: str
    notes: Optional[str] = None
    date: str
