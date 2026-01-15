from pydantic import BaseModel, Field
from typing import Optional

class AssistanceRefundStatusEmail(BaseModel):
    customer_email: str
    customer_name: Optional[str] = None
    order_id: Optional[int] = None
    refund_amount: Optional[float] = None
    status: str
    description: Optional[str] = None

class AssistanceRefundStatusResponse(BaseModel):
    result: bool

class AssistanceComplaint(BaseModel):
    customer_id: int
    complaint: str

class AssistanceComplaintResponse(BaseModel):
    result: bool
