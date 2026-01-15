from pydantic import BaseModel
from typing import Optional

class IncidentCreate(BaseModel):
    employee_id: int
    description: str
    cost: float
    date: Optional[str] = None

# Use IncidentCreate as the alternate for incident creation requests.