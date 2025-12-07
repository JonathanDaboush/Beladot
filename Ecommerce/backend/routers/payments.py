"""
Payment Routes
Handles payment processing and transactions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from database import get_db
from schemas import MessageResponse, PaymentCreateRequest, PaymentResponse
from Services.PaymentService import PaymentService
from Utilities.auth import get_current_active_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.post("", response_model=PaymentResponse, dependencies=[Depends(rate_limiter_moderate)])
async def process_payment(
    payment_data: PaymentCreateRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Process payment for an order"""
    payment_service = PaymentService(db)
    
    payment = await payment_service.process_payment(
        order_id=payment_data.order_id,
        payment_method=payment_data.payment_method,
        amount=payment_data.amount,
        user_id=current_user.id
    )
    
    return payment


@router.get("/{payment_id}", response_model=PaymentResponse, dependencies=[Depends(rate_limiter_moderate)])
async def get_payment(
    payment_id: int,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payment details"""
    payment_service = PaymentService(db)
    
    payment = await payment_service.get_payment(payment_id)
    
    if not payment or payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment


@router.post("/intent", dependencies=[Depends(rate_limiter_moderate)])
async def create_payment_intent(
    order_id: int,
    amount_cents: int,
    currency: str = "USD",
    payment_method_id: int = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a payment intent for an order.
    
    This initiates a payment that can be captured later.
    Used for authorization-and-capture payment flows.
    """
    from sqlalchemy import select
    from Models.Order import Order
    
    payment_service = PaymentService(db)
    
    # Verify order ownership
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create payment for this order"
        )
    
    try:
        result = await payment_service.create_payment_intent(
            order_id=order_id,
            amount_cents=amount_cents,
            currency=currency,
            payment_method_id=payment_method_id
        )
        
        return {
            "intent_id": result.get("intent_id"),
            "client_secret": result.get("client_secret"),
            "status": result.get("status"),
            "amount": result.get("amount"),
            "currency": result.get("currency")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{payment_id}/capture", dependencies=[Depends(rate_limiter_moderate)])
async def capture_payment(
    payment_id: int,
    amount_cents: int = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Capture a previously authorized payment.
    
    Used for two-step payment flows where authorization happens first
    and capture happens when the order is ready to ship or fulfill.
    """
    from sqlalchemy import select
    from Models.Payment import Payment
    
    payment_service = PaymentService(db)
    
    # Verify payment ownership
    result = await db.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Verify order ownership
    result = await db.execute(
        select(Order).where(Order.id == payment.order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order or order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to capture this payment"
        )
    
    try:
        result = await payment_service.capture_payment(
            payment_id=payment_id,
            amount_cents=amount_cents
        )
        
        return {
            "payment_id": payment_id,
            "status": result.get("status"),
            "amount_captured": result.get("amount_captured"),
            "currency": result.get("currency")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/stored-method/charge", dependencies=[Depends(rate_limiter_moderate)])
async def charge_stored_payment_method(
    order_id: int,
    amount_cents: int,
    currency: str = "USD",
    payment_method_id: int = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Charge a stored payment method for an order.
    
    Uses a previously saved payment method to process payment.
    Single-step payment flow (authorize and capture in one step).
    """
    from sqlalchemy import select
    from Models.Order import Order
    
    payment_service = PaymentService(db)
    
    # Verify order ownership
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to charge payment for this order"
        )
    
    try:
        result = await payment_service.charge_stored_payment_method(
            user_id=current_user.id,
            amount_cents=amount_cents,
            currency=currency,
            order_id=order_id,
            payment_method_id=payment_method_id
        )
        
        return {
            "payment_id": result.get("payment_id"),
            "status": result.get("status"),
            "amount": result.get("amount"),
            "currency": result.get("currency"),
            "payment_method": result.get("payment_method")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

