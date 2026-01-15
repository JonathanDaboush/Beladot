from pydantic import BaseModel, Field
from typing import Optional

class EmployeeComponentCreate(BaseModel):
    img_url: str
    description: str
    department_id: int

class EmployeeComponentUpdate(BaseModel):
    img_url: Optional[str] = None
    description: Optional[str] = None

class EmployeeComponentResponse(BaseModel):
    id: int
    img_url: str
    description: str
    department_id: int

class EmployeeComponentDeleteResponse(BaseModel):
    result: bool
