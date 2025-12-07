"""
Cart Routes
Handles shopping cart operations with pricing and currency support
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from schemas import CartResponse, AddToCartRequest, MessageResponse
from Services.CartService import CartService
from Services.CurrencyConversionService import CurrencyConversionService
from Repositories.ProductRepository import ProductRepository
from Utilities.auth import get_current_active_user, get_current_customer_service
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.get("", response_model=CartResponse, dependencies=[Depends(rate_limiter_moderate)])
async def get_cart(
    currency: Optional[str] = Query("USD", description="Currency code for price display"),
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's shopping cart with optional currency conversion"""
    cart_service = CartService(db)
    cart = await cart_service.get_or_create_cart(current_user.id)
    
    # Convert prices if currency != USD
    if currency != "USD" and hasattr(cart, 'total_cents'):
        currency_service = CurrencyConversionService()
        cart.display_currency = currency
        cart.display_total = currency_service.convert("USD", currency, cart.total_cents / 100)
    
    return cart


@router.post("/items", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def add_to_cart(
    request: AddToCartRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Add item to shopping cart with inventory validation"""
    from Services.SimpleInventoryService import SimpleInventoryService
    
    cart_service = CartService(db)
    product_repo = ProductRepository(db)
    inventory_service = SimpleInventoryService(product_repo)
    
    # Check inventory availability before adding
    available = await inventory_service.check_availability(request.product_id, request.quantity)
    if not available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient inventory for this product"
        )
    
    await cart_service.add_item(
        user_id=current_user.id,
        product_id=request.product_id,
        quantity=request.quantity,
        variant_id=request.variant_id
    )
    
    return {"message": "Item added to cart successfully"}


@router.delete("/items/{product_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def remove_from_cart(
    product_id: int,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove item from cart (Users and Customer Service only)"""
    cart_service = CartService(db)
    cart = await cart_service.get_or_create_cart(current_user.id)
    
    success = await cart_service.remove_item(cart.id, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in cart"
        )
    
    return {"message": "Item removed from cart"}


@router.patch("/items/{product_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_cart_item_quantity(
    product_id: int,
    quantity: int = Query(..., gt=0, description="New quantity"),
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update cart item quantity (Users and Customer Service only)"""
    from Services.SimpleInventoryService import SimpleInventoryService
    
    cart_service = CartService(db)
    product_repo = ProductRepository(db)
    inventory_service = SimpleInventoryService(product_repo)
    cart = await cart_service.get_or_create_cart(current_user.id)
    
    # Check inventory availability
    available = await inventory_service.check_availability(product_id, quantity)
    if not available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient inventory for requested quantity"
        )
    
    await cart_service.update_item(cart.id, product_id, quantity)
    return {"message": "Cart item quantity updated"}


@router.delete("", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def clear_cart(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Clear all items from cart (Users and Customer Service only)"""
    cart_service = CartService(db)
    cart = await cart_service.get_or_create_cart(current_user.id)
    
    await cart_service.clear_cart(cart.id)
    return {"message": "Cart cleared successfully"}
