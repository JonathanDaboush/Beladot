"""
Seller Extended Router
Adds seller registration and financial management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from database import get_db
from schemas import MessageResponse
from Services.SellerService import SellerService
from Utilities.auth import get_current_user, get_current_admin_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/seller", tags=["Seller Extended"])


@router.post("/register", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def register_as_seller(
    business_info: Dict,
    finance_info: Dict,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Register current user as seller
    Requires business information and banking details
    """
    from Repositories.SellerRepository import SellerRepository
    from Repositories.SellerFinanceRepository import SellerFinanceRepository
    
    seller_repo = SellerRepository(db)
    finance_repo = SellerFinanceRepository(db)
    seller_service = SellerService(seller_repo, finance_repo)
    
    seller = await seller_service.register_seller(
        user_id=current_user.id,
        business_info=business_info,
        finance_info=finance_info,
        actor_id=current_user.id,
        actor_type='user',
        actor_email=current_user.email
    )
    
    return {
        "message": "Seller registration successful",
        "seller_id": seller.id
    }


@router.get("/my-seller-info", dependencies=[Depends(rate_limiter_moderate)])
async def get_my_seller_info(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get seller information for current user"""
    from Repositories.SellerRepository import SellerRepository
    from Repositories.SellerFinanceRepository import SellerFinanceRepository
    
    seller_repo = SellerRepository(db)
    finance_repo = SellerFinanceRepository(db)
    seller_service = SellerService(seller_repo, finance_repo)
    
    seller = await seller_service.get_seller_by_user(
        user_id=current_user.id,
        actor_id=current_user.id,
        actor_type='user',
        actor_email=current_user.email
    )
    
    return {"seller": seller}


@router.get("/finance/{seller_id}", dependencies=[Depends(rate_limiter_moderate)])
async def get_seller_finance_details(
    seller_id: int,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get seller financial details (admin only)"""
    from Repositories.SellerRepository import SellerRepository
    from Repositories.SellerFinanceRepository import SellerFinanceRepository
    
    seller_repo = SellerRepository(db)
    finance_repo = SellerFinanceRepository(db)
    seller_service = SellerService(seller_repo, finance_repo)
    
    finance = await seller_service.get_seller_finance(
        seller_id=seller_id,
        actor_id=current_admin.id,
        actor_type='admin',
        actor_email=current_admin.email
    )
    
    return {"finance": finance}
