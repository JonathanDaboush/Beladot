from backend.persistance.db_dependency import get_db
from fastapi import APIRouter, Depends, HTTPException, Request
from backend.schemas_assistance import (
    AssistanceRefundStatusEmail, AssistanceRefundStatusResponse,
    AssistanceComplaint, AssistanceComplaintResponse
)
from backend.services import customerAssistanceServices

router = APIRouter(prefix="/api/v1/assistance", tags=["assistance"])

# Role enforcement
def require_role(role: str):
    async def dependency(request: Request):
        identity = getattr(request.state, "identity", {})
        if identity.get("role") != role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return identity
    return dependency

# Dummy service for tests / startup
async def dummy_assistance_service():
    class DummyService:
        async def send_customer_refund_status_email(self, **kwargs):
            return kwargs

        async def process_customer_complaint(self, **kwargs):
            return kwargs

    return DummyService()

@router.post("/refund-status", response_model=AssistanceRefundStatusResponse)
async def send_refund_status_email(
    payload: AssistanceRefundStatusEmail,
    # assistanceService dependency removed for import safety
    identity=Depends(require_role("user")),
        db=Depends(get_db),
):
    result = await customerAssistanceServices.send_customer_refund_status_email(user_id=identity["user_id"], db=db, **payload.dict())
    return {"result": result}

@router.post("/complaint", response_model=AssistanceComplaintResponse)
async def process_complaint(
    complaint: AssistanceComplaint,
    # assistanceService dependency removed for import safety
    identity=Depends(require_role("user")),
        db=Depends(get_db),
):
    result = await customerAssistanceServices.process_customer_complaint(user_id=identity["user_id"], db=db, **complaint.dict())
    return {"result": result}
