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
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_rating: Optional[float] = None,
    in_stock_only: Optional[bool] = False,
    sort_by: Optional[str] = "relevance",  # relevance, price_asc, price_desc, rating, newest
    limit: Optional[int] = 20,
    offset: Optional[int] = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Search products with advanced filters
    
    Args:
        query: Search query (product name, description, tags)
        category: Filter by category name
        min_price: Minimum price in cents
        max_price: Maximum price in cents
        min_rating: Minimum average rating (0-5)
        in_stock_only: Show only products with stock > 0
        sort_by: Sort order (relevance, price_asc, price_desc, rating, newest)
        limit: Number of results per page
        offset: Pagination offset
    """
    search_service = SearchService(db)
    
    results = await search_service.search_products(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        in_stock_only=in_stock_only,
        sort_by=sort_by,
        limit=limit,
        offset=offset
    )
    
    return {
        "results": results.get("items", []),
        "total": results.get("total", 0),
        "limit": limit,
        "offset": offset
    }
