"""
Checkout Routes
Handles checkout process with payment intent and capture flow
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from schemas import MessageResponse, OrderResponse
from Services.CheckoutService import CheckoutService
from Services.PaymentService import PaymentService
from Repositories.PaymentRepository import PaymentRepository
from Repositories.StoredPaymentMethodRepository import StoredPaymentMethodRepository
from Utilities.auth import get_current_active_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/checkout", tags=["Checkout"])


@router.post("/payment-intent", dependencies=[Depends(rate_limiter_moderate)])
async def create_payment_intent(
    amount_cents: int = Body(..., description="Amount in cents"),
    currency: str = Body("USD", description="Currency code"),
    payment_method_id: Optional[int] = Body(None, description="Stored payment method ID"),
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create payment intent (authorize payment before checkout).
    This reserves funds but doesn't charge yet.
    """
    payment_repo = PaymentRepository(db)
    payment_method_repo = StoredPaymentMethodRepository(db)
    payment_service = PaymentService(payment_repo, payment_method_repo)
    
    # Create a temporary order ID (0 for intent, will be replaced after order creation)
    intent = await payment_service.create_payment_intent(
        order_id=0,  # Temporary - will be updated after order creation
        amount_cents=amount_cents,
        currency=currency,
        payment_method_id=payment_method_id
    )
    
    return intent


@router.post("/process", response_model=OrderResponse, dependencies=[Depends(rate_limiter_moderate)])
async def process_checkout(
    cart_id: int = Body(..., description="Cart ID to checkout"),
    payment_intent_id: int = Body(..., description="Payment intent ID from /payment-intent"),
    shipping_address: dict = Body(..., description="Shipping address"),
    idempotency_key: Optional[str] = Body(None, description="Idempotency key for duplicate prevention"),
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Process checkout and capture payment.
    Steps:
    1. Create order from cart
    2. Update payment with order ID
    3. Capture payment (actually charge customer)
    4. Return order
    """
    checkout_service = CheckoutService(db)
    payment_repo = PaymentRepository(db)
    payment_method_repo = StoredPaymentMethodRepository(db)
    payment_service = PaymentService(payment_repo, payment_method_repo)
    
    # Create order from cart
    order = await checkout_service.create_order_from_cart(
        cart_id=cart_id,
        shipping_address=shipping_address,
        idempotency_key=idempotency_key
    )
    
    # Update payment with order ID
    payment = await payment_repo.get_by_id(payment_intent_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment intent not found"
        )
    
    payment.order_id = order.id
    await payment_repo.update(payment)
    
    # Capture payment (charge customer)
    try:
        capture_result = await payment_service.capture_payment(payment_intent_id)
    except ValueError as e:
        # If capture fails, cancel the order
        order.status = 'cancelled'
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment capture failed: {str(e)}"
        )
    
    # Update order status to confirmed
    from Models.Order import OrderStatus
    order.status = OrderStatus.CONFIRMED
    await db.commit()
    
    # Auto-create shipment for confirmed purchase
    from Services.FulfillmentService import FulfillmentService
    fulfillment_service = FulfillmentService(db)
    
    try:
        shipment = await fulfillment_service.create_shipment(
            order_id=order.id,
            carrier="AUTO",  # Auto-select based on destination
            actor_id=current_user.id
        )
        order.shipment_id = shipment.id
        await db.commit()
    except Exception as e:
        # Log but don't fail checkout if shipment creation fails
        print(f"Warning: Shipment auto-creation failed: {e}")
    
    return order


@router.post("/charge-stored-method", dependencies=[Depends(rate_limiter_moderate)])
async def charge_with_stored_method(
    cart_id: int = Body(..., description="Cart ID to checkout"),
    payment_method_id: Optional[int] = Body(None, description="Stored payment method ID (uses default if not provided)"),
    shipping_address: dict = Body(..., description="Shipping address"),
    idempotency_key: Optional[str] = Body(None, description="Idempotency key"),
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    One-step checkout with stored payment method.
    Creates order and charges payment method in one operation.
    """
    checkout_service = CheckoutService(db)
    payment_repo = PaymentRepository(db)
    payment_method_repo = StoredPaymentMethodRepository(db)
    payment_service = PaymentService(payment_repo, payment_method_repo)
    
    # Create order from cart
    order = await checkout_service.create_order_from_cart(
        cart_id=cart_id,
        shipping_address=shipping_address,
        idempotency_key=idempotency_key
    )
    
    # Charge stored payment method
    try:
        charge_result = await payment_service.charge_stored_payment_method(
            user_id=current_user.id,
            amount_cents=order.total_cents,
            currency="USD",
            order_id=order.id,
            payment_method_id=payment_method_id
        )
    except ValueError as e:
        # If charge fails, cancel the order
        order.status = 'cancelled'
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment failed: {str(e)}"
        )
    
    # Update order status to confirmed
    from Models.Order import OrderStatus
    order.status = OrderStatus.CONFIRMED
    await db.commit()
    
    return {
        "order": order,
        "payment": charge_result
    }

