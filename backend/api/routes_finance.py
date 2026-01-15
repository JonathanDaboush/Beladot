
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List

from backend.schemas import (
    FinanceIssueCreate,
    FinanceIssueUpdate,
    FinanceIssueResponse,
    FinanceReimbursementUpdate,
    FinanceReimbursementResponse,
)

router = APIRouter(prefix="/api/finance", tags=["finance"])

# -------------------------------------------------
# Dependency: Role enforcement (request-scoped)
# -------------------------------------------------
def require_role(role: str):
    async def dependency(request: Request):
        identity = getattr(request.state, "identity", {})
        if identity.get("role") != role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return identity
    return dependency

# -------------------------------------------------
# Dummy finance service (IMPORT-SAFE)
# -------------------------------------------------
class DummyFinanceService:
    async def get_issues_catalog(self, employee_id: int):
        return []

    async def create_issue(self, employee_id: int, **kwargs):
        return {**kwargs, "id": 1}

    async def update_issue(self, issue_id: int, **kwargs):
        return {**kwargs, "id": issue_id}

    async def delete_issue(self, issue_id: int):
        return {"id": issue_id, "deleted": True}

async def get_finance_services():
    return DummyFinanceService()

# -------------------------------------------------
# Routes
# -------------------------------------------------

@router.get("/issues", response_model=List[FinanceIssueResponse])
async def get_issues(
    finance_services=Depends(get_finance_services),
    identity=Depends(require_role("employee")),
):
    return await finance_services.get_issues_catalog(
        employee_id=identity["employee_id"]
    )

@router.post("/issues", response_model=FinanceIssueResponse)
async def create_issue(
    issue: FinanceIssueCreate,
    finance_services=Depends(get_finance_services),
    identity=Depends(require_role("employee")),
):
    return await finance_services.create_issue(
        employee_id=identity["employee_id"],
        **issue.dict(),
    )

@router.put("/issues/{issue_id}", response_model=FinanceIssueResponse)
async def update_issue(
    issue_id: int,
    update: FinanceIssueUpdate,
    finance_services=Depends(get_finance_services),
    identity=Depends(require_role("employee")),
):
    return await finance_services.update_issue(
        issue_id,
        **update.dict(),
    )

@router.delete("/issues/{issue_id}")
async def delete_issue(
    issue_id: int,
    finance_services=Depends(get_finance_services),
    identity=Depends(require_role("employee")),
):
    return await finance_services.delete_issue(issue_id)

@router.put(
    "/reimbursements/{reimbursement_id}",
    response_model=FinanceReimbursementResponse,
)
async def update_reimbursement(
    reimbursement_id: int,
    update: FinanceReimbursementUpdate,
    finance_services=Depends(get_finance_services),
    identity=Depends(require_role("employee")),
):
    return {**update.dict(), "id": reimbursement_id}

