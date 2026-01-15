from backend.persistance.db_dependency import get_db
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from backend.schemas_employee import (
    EmployeeComponentCreate, EmployeeComponentResponse
)

router = APIRouter(prefix="/api/v1/employee", tags=["employee"])

def require_role(role: str):
    async def dependency(request: Request):
        identity = getattr(request.state, "identity", {})
        if identity.get("role") != role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return identity
    return dependency

async def dummy_employee_service():
    class DummyService:
        async def get_all_employee_components(self):
            return []
        async def create_employee_component(self, **kwargs):
            return kwargs
    return DummyService()

@router.get("/components", response_model=List[EmployeeComponentResponse])
async def get_all_employee_components(
    employeeService=Depends(dummy_employee_service),
    identity=Depends(require_role("employee")),
    db=Depends(get_db),
):
    return await employeeService.get_all_employee_components(employee_id=identity["employee_id"], db=db)

@router.post("/components", response_model=EmployeeComponentResponse)
async def create_employee_component(
    component: EmployeeComponentCreate,
    employeeService=Depends(dummy_employee_service),
    identity=Depends(require_role("employee")),
    db=Depends(get_db),
):
    return await employeeService.create_employee_component(employee_id=identity["employee_id"], db=db, **component.dict())
