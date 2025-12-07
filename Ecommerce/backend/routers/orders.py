"""
Order Routes
Handles order creation and management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict

from database import get_db
from schemas import OrderResponse, CreateOrderRequest, MessageResponse
from Services.OrderService import OrderService
from Utilities.auth import get_current_active_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, dependencies=[Depends(rate_limiter_moderate)])
async def create_order(
    order_data: CreateOrderRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new order from cart"""
    order_service = OrderService(db)
    
    order = await order_service.create_order(
        user_id=current_user.id,
        shipping_address_id=order_data.shipping_address_id,
        payment_method=order_data.payment_method
    )
    
    return order


@router.get("", dependencies=[Depends(rate_limiter_moderate)])
async def get_user_orders(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all orders for current user with order history"""
    order_service = OrderService(db)
    orders = await order_service.get_user_orders(current_user.id)
    
    return {"orders": orders}


@router.get("/history", dependencies=[Depends(rate_limiter_moderate)])
async def get_order_history(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's order history with products, prices, and dates"""
    order_service = OrderService(db)
    orders = await order_service.get_user_orders(current_user.id)
    
    # Format for history view
    history = []
    for order in orders:
        history.append({
            "order_id": order.id,
            "order_number": order.order_number,
            "status": order.status.value,
            "total_cents": order.total_cents,
            "created_at": order.created_at,
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price_cents": item.unit_price_cents,
                    "total_price_cents": item.total_price_cents
                }
                for item in order.items
            ]
        })
    
    return {"order_history": history}


@router.post("/{order_id}/cancel", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def cancel_order(
    order_id: int,
    reason: str = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel order before delivery"""
    order_service = OrderService(db)
    
    try:
        await order_service.cancel_order(order_id, current_user.id, reason)
        return {"message": "Order cancelled successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{order_id}/refund", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def request_refund(
    order_id: int,
    items: List[Dict],
    reason: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Request refund for delivered order"""
    order_service = OrderService(db)
    
    try:
        await order_service.request_refund(
            order_id=order_id,
            user_id=current_user.id,
            items=items,
            reason=reason
        )
        return {"message": "Refund request submitted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{order_id}/tracking", dependencies=[Depends(rate_limiter_moderate)])
async def track_order_delivery(
    order_id: int,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Track delivery status for an order.
    
    Shows:
    - Current delivery status
    - Tracking number
    - Carrier information
    - Estimated delivery date
    - Current location (if available)
    - Delivery history
    """
    from sqlalchemy import select
    from Models.Order import Order
    from Models.Shipment import Shipment
    
    # Verify order belongs to user
    result = await db.execute(
        select(Order).where(Order.id == order_id).where(Order.user_id == current_user.id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Get shipment information
    result = await db.execute(
        select(Shipment).where(Shipment.order_id == order_id).order_by(Shipment.created_at.desc())
    )
    shipments = result.scalars().all()
    
    if not shipments:
        return {
            "order_id": order_id,
            "order_number": order.order_number,
            "order_status": order.status.value,
            "has_shipment": False,
            "message": "No shipment created yet. Order is being processed."
        }
    
    # Format shipment tracking info
    tracking_info = []
    for shipment in shipments:
        tracking_info.append({
            "shipment_id": shipment.id,
            "tracking_number": shipment.tracking_number,
            "carrier": shipment.carrier,
            "status": shipment.status.value,
            "estimated_delivery": shipment.estimated_delivery,
            "shipped_at": shipment.shipped_at,
            "delivered_at": shipment.delivered_at,
            "notes": shipment.notes,
            "current_location": shipment.notes.split('\n')[-1] if shipment.notes else "In transit"
        })
    
    return {
        "order_id": order_id,
        "order_number": order.order_number,
        "order_status": order.status.value,
        "has_shipment": True,
        "shipments": tracking_info,
        "primary_tracking": tracking_info[0] if tracking_info else None
    }


# ===== CART MANAGEMENT ENDPOINTS =====

@router.post("/cart/items", dependencies=[Depends(rate_limiter_moderate)])
async def add_cart_item(
    product_id: int,
    quantity: int = 1,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add item to cart.
    
    Customer adds products to their cart for checkout.
    Creates cart if doesn't exist.
    """
    from Repositories.CartRepository import CartRepository
    from Repositories.ProductRepository import ProductRepository
    from Services.CartService import CartService
    from Services.PricingService import PricingService
    
    product_repo = ProductRepository(db)
    cart_repo = CartRepository(db)
    pricing_service = PricingService(product_repo)
    cart_service = CartService(cart_repo, pricing_service)
    
    try:
        # Get or create cart
        cart = await cart_service.get_cart(user_id=current_user.id)
        
        if not cart:
            # Create new cart
            from Models.Cart import Cart
            cart = Cart(user_id=current_user.id)
            cart = await cart_repo.create(cart)
        
        # Add item
        cart_item = await cart_service.add_item(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity
        )
        
        return {
            "message": "Item added to cart",
            "cart_item_id": cart_item.id,
            "product_id": product_id,
            "quantity": cart_item.quantity,
            "cart_id": cart.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/cart/items/{cart_item_id}", dependencies=[Depends(rate_limiter_moderate)])
async def remove_cart_item(
    cart_item_id: int,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove item from cart.
    
    Customer removes products from their cart.
    """
    from Repositories.CartRepository import CartRepository
    from Repositories.ProductRepository import ProductRepository
    from Services.CartService import CartService
    from Services.PricingService import PricingService
    from sqlalchemy import select
    from Models.CartItem import CartItem
    from Models.Cart import Cart
    
    # Verify cart item belongs to user
    result = await db.execute(
        select(CartItem, Cart)
        .join(Cart, Cart.id == CartItem.cart_id)
        .where(CartItem.id == cart_item_id)
        .where(Cart.user_id == current_user.id)
    )
    
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found or doesn't belong to you"
        )
    
    cart_item, cart = row
    
    product_repo = ProductRepository(db)
    cart_repo = CartRepository(db)
    pricing_service = PricingService(product_repo)
    cart_service = CartService(cart_repo, pricing_service)
    
    try:
        await cart_service.remove_item(
            cart_id=cart.id,
            product_id=cart_item.product_id
        )
        
        return {
            "message": "Item removed from cart",
            "cart_item_id": cart_item_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/cart/items/{cart_item_id}", dependencies=[Depends(rate_limiter_moderate)])
async def update_cart_item(
    cart_item_id: int,
    quantity: int,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update cart item quantity.
    
    Customer modifies product quantity in their cart.
    """
    from Repositories.CartRepository import CartRepository
    from Repositories.ProductRepository import ProductRepository
    from Services.CartService import CartService
    from Services.PricingService import PricingService
    from sqlalchemy import select
    from Models.CartItem import CartItem
    from Models.Cart import Cart
    
    if quantity < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be at least 1"
        )
    
    # Verify cart item belongs to user
    result = await db.execute(
        select(CartItem, Cart)
        .join(Cart, Cart.id == CartItem.cart_id)
        .where(CartItem.id == cart_item_id)
        .where(Cart.user_id == current_user.id)
    )
    
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found or doesn't belong to you"
        )
    
    cart_item, cart = row
    
    product_repo = ProductRepository(db)
    cart_repo = CartRepository(db)
    pricing_service = PricingService(product_repo)
    cart_service = CartService(cart_repo, pricing_service)
    
    try:
        updated_item = await cart_service.update_item_quantity(
            cart_item_id=cart_item_id,
            quantity=quantity
        )
        
        return {
            "message": "Cart item updated",
            "cart_item_id": cart_item_id,
            "new_quantity": updated_item.quantity,
            "product_id": updated_item.product_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/cart", dependencies=[Depends(rate_limiter_moderate)])
async def clear_cart(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Clear entire cart.
    
    Customer removes all items from their cart.
    """
    from Repositories.CartRepository import CartRepository
    from Repositories.ProductRepository import ProductRepository
    from Services.CartService import CartService
    from Services.PricingService import PricingService
    
    product_repo = ProductRepository(db)
    cart_repo = CartRepository(db)
    pricing_service = PricingService(product_repo)
    cart_service = CartService(cart_repo, pricing_service)
    
    try:
        cart = await cart_service.get_cart(user_id=current_user.id)
        
        if not cart:
            return {"message": "Cart is already empty"}
        
        await cart_service.clear_cart(cart.id)
        
        return {
            "message": "Cart cleared successfully",
            "cart_id": cart.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ===== ORDER MANAGEMENT (ADMIN/MANAGER/CS) =====

@router.get("/all", dependencies=[Depends(rate_limiter_moderate)])
async def get_all_orders(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all orders.
    
    - Customers see only their own orders
    - Customer Service, Managers, and Admin see all orders
    """
    from Models.User import UserRole
    
    order_service = OrderService(db)
    
    # Check if user has permission to see all orders
    if current_user.role in [UserRole.CUSTOMER_SERVICE, UserRole.MANAGER, UserRole.ADMIN, UserRole.FINANCE]:
        # Get all orders for CS, Manager, Finance, Admin
        orders = await order_service.get_all_orders()
    else:
        # Customers can only see their own orders
        orders = await order_service.get_user_orders(current_user.id)
    
    return {"orders": orders, "count": len(orders)}


# ===== CHECKOUT =====

@router.post("/checkout", dependencies=[Depends(rate_limiter_moderate)])
async def create_order_from_cart(
    shipping_address_id: int,
    payment_method_id: int = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create order from cart (checkout).
    
    Converts user's cart into an order with:
    - Inventory reservation
    - Payment processing
    - Order confirmation
    """
    from Services.CheckoutService import CheckoutService
    from Services.PaymentService import PaymentService
    from Services.InventoryService import InventoryService
    from Services.NotificationService import NotificationService
    
    checkout_service = CheckoutService(db)
    payment_service = PaymentService(db)
    inventory_service = InventoryService(db)
    notification_service = NotificationService(db)
    
    try:
        # Create order from cart
        order = await checkout_service.create_order_from_cart(
            user_id=current_user.id,
            shipping_address_id=shipping_address_id,
            payment_method_id=payment_method_id
        )
        
        # Send order confirmation email
        await notification_service.send_order_confirmation(
            email=current_user.email,
            order_id=order.id,
            order_details={
                "order_number": order.order_number,
                "total": order.total_cents / 100,
                "items": [
                    {
                        "name": item.product.name if hasattr(item, 'product') else f"Product {item.product_id}",
                        "quantity": item.quantity,
                        "price": item.unit_price_cents / 100
                    }
                    for item in order.items
                ]
            }
        )
        
        return {
            "message": "Order created successfully",
            "order_id": order.id,
            "order_number": order.order_number,
            "total_cents": order.total_cents,
            "status": order.status.value
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{order_id}/cancel-checkout", dependencies=[Depends(rate_limiter_moderate)])
async def cancel_order_checkout(
    order_id: int,
    reason: str = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel order (CheckoutService version).
    
    Available for:
    - Customers (own orders)
    - Customer Service (any order)
    - Managers (any order)
    """
    from Services.CheckoutService import CheckoutService
    from Models.User import UserRole
    from sqlalchemy import select
    from Models.Order import Order
    
    # Verify order exists and check permissions
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check permissions
    if current_user.role not in [UserRole.CUSTOMER_SERVICE, UserRole.MANAGER, UserRole.ADMIN]:
        # Customer can only cancel their own orders
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this order"
            )
    
    checkout_service = CheckoutService(db)
    
    try:
        cancelled_order = await checkout_service.cancel_order(order_id, reason)
        
        return {
            "message": "Order cancelled successfully",
            "order_id": cancelled_order.id,
            "order_number": cancelled_order.order_number,
            "status": cancelled_order.status.value
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

