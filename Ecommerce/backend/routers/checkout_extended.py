"""
Checkout Extended Router
Adds order preview, cart validation, and order status transitions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import MessageResponse
from Services.CheckoutService import CheckoutService
from Services.CartService import CartService
from Services.InventoryService import InventoryService
from Services.PaymentService import PaymentService
from Services.PricingService import PricingService
from Services.NotificationService import NotificationService
from Utilities.auth import get_current_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/checkout", tags=["Checkout Extended"])


@router.post("/preview", dependencies=[Depends(rate_limiter_moderate)])
async def preview_order(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Preview order total before checkout (with shipping & tax)"""
    from Repositories.OrderRepository import OrderRepository
    from Repositories.CartRepository import CartRepository
    from Repositories.ProductRepository import ProductRepository
    from Repositories.PaymentRepository import PaymentRepository
    from Repositories.JobRepository import JobRepository
    
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    payment_repo = PaymentRepository(db)
    job_repo = JobRepository(db)
    
    pricing_service = PricingService(product_repo)
    cart_service = CartService(cart_repo, pricing_service)
    inventory_service = InventoryService(product_repo, None, None)
    payment_service = PaymentService(payment_repo)
    notification_service = NotificationService(job_repo)
    
    checkout_service = CheckoutService(
        order_repo, cart_service, inventory_service, 
        payment_service, pricing_service, notification_service
    )
    
    # Get cart
    cart = await cart_service.get_cart(user_id=current_user.id)
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart is empty"
        )
    
    # Calculate total
    total = await checkout_service.calculate_order_total(cart.id)
    
    return {
        "preview": total,
        "subtotal": total.get("subtotal"),
        "tax": total.get("tax"),
        "shipping": total.get("shipping"),
        "total": total.get("total")
    }


@router.post("/validate", dependencies=[Depends(rate_limiter_moderate)])
async def validate_cart_before_checkout(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Validate cart before checkout (stock availability, pricing)"""
    from Repositories.OrderRepository import OrderRepository
    from Repositories.CartRepository import CartRepository
    from Repositories.ProductRepository import ProductRepository
    from Repositories.PaymentRepository import PaymentRepository
    from Repositories.JobRepository import JobRepository
    
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    payment_repo = PaymentRepository(db)
    job_repo = JobRepository(db)
    
    pricing_service = PricingService(product_repo)
    cart_service = CartService(cart_repo, pricing_service)
    inventory_service = InventoryService(product_repo, None, None)
    payment_service = PaymentService(payment_repo)
    notification_service = NotificationService(job_repo)
    
    checkout_service = CheckoutService(
        order_repo, cart_service, inventory_service,
        payment_service, pricing_service, notification_service
    )
    
    cart = await cart_service.get_cart(user_id=current_user.id)
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart is empty"
        )
    
    validation = await checkout_service.validate_cart(cart)
    
    return {
        "valid": validation.get("valid", False),
        "errors": validation.get("errors", []),
        "warnings": validation.get("warnings", [])
    }


@router.get("/status-check/{order_id}", dependencies=[Depends(rate_limiter_moderate)])
async def check_status_transition(
    order_id: int,
    from_status: str,
    to_status: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check if order status transition is allowed"""
    from Repositories.OrderRepository import OrderRepository
    from Repositories.CartRepository import CartRepository
    from Repositories.ProductRepository import ProductRepository
    from Repositories.PaymentRepository import PaymentRepository
    from Repositories.JobRepository import JobRepository
    
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    payment_repo = PaymentRepository(db)
    job_repo = JobRepository(db)
    
    pricing_service = PricingService(product_repo)
    cart_service = CartService(cart_repo, pricing_service)
    inventory_service = InventoryService(product_repo, None, None)
    payment_service = PaymentService(payment_repo)
    notification_service = NotificationService(job_repo)
    
    checkout_service = CheckoutService(
        order_repo, cart_service, inventory_service,
        payment_service, pricing_service, notification_service
    )
    
    can_transition = checkout_service.can_transition_status(from_status, to_status)
    
    return {
        "can_transition": can_transition,
        "from_status": from_status,
        "to_status": to_status
    }
