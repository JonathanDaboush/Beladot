"""
Payment Methods Routes
Handles stored payment methods for users
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from schemas import MessageResponse
from Models.StoredPaymentMethod import StoredPaymentMethod
from Repositories.StoredPaymentMethodRepository import StoredPaymentMethodRepository
from Utilities.auth import get_current_active_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/payment-methods", tags=["Payment Methods"])


@router.get("", dependencies=[Depends(rate_limiter_moderate)])
async def list_payment_methods(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all stored payment methods for current user"""
    payment_method_repo = StoredPaymentMethodRepository(db)
    
    methods = await payment_method_repo.get_by_user(current_user.id)
    
    # Sanitize response (don't expose gateway_token)
    sanitized = []
    for method in methods:
        sanitized.append({
            'id': method.id,
            'card_brand': method.card_brand,
            'card_last_four': method.card_last_four,
            'expiry_month': method.expiry_month,
            'expiry_year': method.expiry_year,
            'is_default': method.is_default,
            'is_active': method.is_active
        })
    
    return {"payment_methods": sanitized}


@router.post("", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def add_payment_method(
    gateway_token: str,
    card_brand: str,
    card_last_four: str,
    expiry_month: int,
    expiry_year: int,
    billing_zip: Optional[str] = None,
    set_as_default: bool = False,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a stored payment method.
    Gateway token should be obtained from payment gateway (e.g., Stripe) on frontend.
    """
    payment_method_repo = StoredPaymentMethodRepository(db)
    
    # Create payment method
    method = StoredPaymentMethod(
        user_id=current_user.id,
        gateway_token=gateway_token,
        card_brand=card_brand,
        card_last_four=card_last_four,
        expiry_month=expiry_month,
        expiry_year=expiry_year,
        billing_zip=billing_zip,
        is_default=set_as_default
    )
    
    # If this is the first payment method, make it default
    existing_methods = await payment_method_repo.get_by_user(current_user.id)
    if not existing_methods:
        method.is_default = True
    
    method = await payment_method_repo.create(method)
    
    # If set as default, unset others
    if set_as_default:
        await payment_method_repo.set_default(method.id, current_user.id)
    
    return {"message": "Payment method added successfully"}


@router.patch("/{payment_method_id}/default", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def set_default_payment_method(
    payment_method_id: int,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Set a payment method as default"""
    payment_method_repo = StoredPaymentMethodRepository(db)
    
    # Verify user owns this payment method
    method = await payment_method_repo.get_by_id(payment_method_id)
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    if method.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own payment methods"
        )
    
    await payment_method_repo.set_default(payment_method_id, current_user.id)
    
    return {"message": "Default payment method updated"}


@router.delete("/{payment_method_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def delete_payment_method(
    payment_method_id: int,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete (deactivate) a payment method"""
    payment_method_repo = StoredPaymentMethodRepository(db)
    
    # Verify user owns this payment method
    method = await payment_method_repo.get_by_id(payment_method_id)
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    if method.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own payment methods"
        )
    
    await payment_method_repo.delete(payment_method_id)
    
    return {"message": "Payment method deleted successfully"}
