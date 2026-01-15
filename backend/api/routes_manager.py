
from fastapi import APIRouter, Depends, HTTPException, Request
from backend.services.managerServices import ManagerService
from backend.schemas_employee import EmployeeEditRequest
from backend.schemas_incident import IncidentCreateRequest
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from backend.persistance.base import AsyncSessionLocal

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

router = APIRouter(prefix="/api/v1/manager", tags=["manager"])

def require_role(role: str):
    async def dependency(request: Request):
        identity = getattr(request.state, "identity", {})
        if identity.get("role") != role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return identity
    return dependency

# Dependency for DB session (replace with your actual DB dependency)



@router.post("/incident", response_model=Any)
async def create_incident_report(
    payload: IncidentCreateRequest,
    identity=Depends(require_role("manager")),
    db: AsyncSession = Depends(get_db)
):
    service = ManagerService(db)
    return await service.create_incident_report(
        manager_id=identity["manager_id"],
        employee_id=payload.employee_id,
        description=payload.description,
        cost=payload.cost,
        date=payload.date
    )

@router.put("/employee/{employee_id}", response_model=Any)
async def edit_employee_info(
    employee_id: int,
    payload: EmployeeEditRequest,
    identity=Depends(require_role("manager")),
    db: AsyncSession = Depends(get_db)
):
    service = ManagerService(db)
    return await service.edit_employee_info(
        manager_id=identity["manager_id"],
        employee_id=employee_id,
        **payload.dict()
    )
