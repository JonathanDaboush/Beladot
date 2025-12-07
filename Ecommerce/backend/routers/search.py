"""
Search Routes
Handles product search and filtering
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from Services.SearchService import SearchService
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.get("/products", dependencies=[Depends(rate_limiter_moderate)])
async def search_products(
    query: str,
    category: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Search products with filters"""
    search_service = SearchService(db)
    
    results = await search_service.search_products(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price
    )
    
    return {"results": results}
