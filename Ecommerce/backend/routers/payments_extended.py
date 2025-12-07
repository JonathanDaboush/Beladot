"""
Payments Extended Router
Adds refund processing and webhook handling
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from schemas import MessageResponse
from Services.PaymentService import PaymentService
from Utilities.auth import get_current_admin_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/payments", tags=["Payments Extended"])


@router.post("/refund/{payment_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def refund_payment(
    payment_id: int,
    amount_cents: Optional[int] = None,
    reason: Optional[str] = None,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Process payment refund (full or partial)
    Admin only - requires approval
    """
    from Repositories.PaymentRepository import PaymentRepository
    
    payment_repo = PaymentRepository(db)
    payment_service = PaymentService(payment_repo)
    
    result = await payment_service.refund_payment(
        payment_id=payment_id,
        amount_cents=amount_cents,
        reason=reason
    )
    
    return {
        "message": "Refund processed successfully",
        "refund_id": result.get("refund_id"),
        "amount_refunded": result.get("amount_refunded")
    }


@router.post("/webhook", dependencies=[Depends(rate_limiter_moderate)])
async def payment_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle payment gateway webhooks
    Public endpoint - validates signature internally
    """
    from Repositories.PaymentRepository import PaymentRepository
    
    # Get raw body
    body = await request.body()
    
    # Get headers
    headers = dict(request.headers)
    
    payment_repo = PaymentRepository(db)
    payment_service = PaymentService(payment_repo)
    
    # Parse event
    event_type = headers.get("x-webhook-event-type")
    
    # Handle webhook
    result = await payment_service.handle_webhook(
        event_type=event_type,
        event_data={"body": body.decode(), "headers": headers}
    )
    
    return {"status": "processed", "event": event_type}
