"""
Cart Extended Router
Adds missing cart functionality: coupons, item count, get without create
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from schemas import MessageResponse
from Services.CartService import CartService
from Services.PricingService import PricingService
from Utilities.auth import get_current_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/cart", tags=["Cart Extended"])


@router.post("/coupon", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def apply_coupon(
    coupon_code: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Apply coupon code to cart"""
    from Repositories.CartRepository import CartRepository
    from Repositories.ProductRepository import ProductRepository
    
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    pricing_service = PricingService(product_repo)
    cart_service = CartService(cart_repo, pricing_service)
    
    cart = await cart_service.get_cart(user_id=current_user.id)
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    
    await cart_service.apply_coupon(cart.id, coupon_code)
    
    return {"message": f"Coupon '{coupon_code}' applied successfully"}


@router.get("/count", dependencies=[Depends(rate_limiter_moderate)])
async def get_cart_item_count(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get total item count in cart (for badge display)"""
    from Repositories.CartRepository import CartRepository
    from Repositories.ProductRepository import ProductRepository
    
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    pricing_service = PricingService(product_repo)
    cart_service = CartService(cart_repo, pricing_service)
    
    cart = await cart_service.get_cart(user_id=current_user.id)
    
    if not cart:
        return {"item_count": 0}
    
    count = await cart_service.get_item_count(cart.id)
    
    return {"item_count": count}


@router.put("/item/{cart_item_id}/quantity", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_item_by_id(
    cart_item_id: int,
    quantity: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update cart item quantity by cart_item_id (not product_id)"""
    from Repositories.CartRepository import CartRepository
    from Repositories.ProductRepository import ProductRepository
    
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    pricing_service = PricingService(product_repo)
    cart_service = CartService(cart_repo, pricing_service)
    
    await cart_service.update_item_quantity(cart_item_id, quantity)
    
    return {"message": "Cart item quantity updated"}
