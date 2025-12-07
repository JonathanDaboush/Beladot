"""
Product Routes
Handles product listing and creation with currency support and stock visibility
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_db
from schemas import ProductResponse, ProductCreateRequest, PaginationParams
from Services.ProductService import ProductService
from Services.CurrencyConversionService import CurrencyConversionService
from Services.SimpleInventoryService import SimpleInventoryService
from Repositories.ProductRepository import ProductRepository
from Utilities.auth import get_current_seller, get_current_admin_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", dependencies=[Depends(rate_limiter_moderate)])
async def list_products(
    pagination: PaginationParams = Depends(),
    currency: Optional[str] = Query("USD", description="Currency code for price display"),
    main_category_id: Optional[int] = Query(None, description="Filter by main category ID"),
    main_subcategory_id: Optional[int] = Query(None, description="Filter by main subcategory ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all products with pagination, currency conversion, and stock visibility.
    
    Category Filtering:
    - main_category_id: Filter by main category (e.g., Electronics)
    - main_subcategory_id: Filter by subcategory (e.g., TV under Electronics)
    
    Stock Info:
    - Products show total stock_quantity
    - Each variant shows its own stock level
    """
    product_service = ProductService(db)
    product_repo = ProductRepository(db)
    inventory_service = SimpleInventoryService(product_repo)
    
    # Apply category filters
    if main_category_id or main_subcategory_id:
        from sqlalchemy import select
        from Models.Product import Product
        query = select(Product)
        
        if main_category_id:
            query = query.where(Product.main_category_id == main_category_id)
        if main_subcategory_id:
            query = query.where(Product.main_subcategory_id == main_subcategory_id)
        
        query = query.offset(pagination.skip).limit(pagination.limit)
        result = await db.execute(query)
        products = result.scalars().all()
    else:
        products = await product_service.get_products(
            skip=pagination.skip,
            limit=pagination.limit
        )
    
    # Enrich products with stock, currency, and variant info
    for product in products:
        # Add stock level (visible to all customers)
        product.stock_quantity = await inventory_service.get_stock_level(product.id)
        product.in_stock = product.stock_quantity > 0
        
        # Add variant stock levels
        if hasattr(product, 'variants') and product.variants:
            for variant in product.variants:
                variant.stock_quantity = variant.stock_quantity if hasattr(variant, 'stock_quantity') else 0
                variant.in_stock = variant.stock_quantity > 0
        
        # Convert prices if currency != USD
        if currency != "USD" and hasattr(product, 'price_cents'):
            currency_service = CurrencyConversionService()
            product.display_currency = currency
            product.display_price = currency_service.convert("USD", currency, product.price_cents / 100)
    
    return {
        "products": products,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "currency": currency,
        "filters": {
            "main_category_id": main_category_id,
            "main_subcategory_id": main_subcategory_id
        }
    }


@router.get("/{product_id}", dependencies=[Depends(rate_limiter_moderate)])
async def get_product(
    product_id: int,
    currency: Optional[str] = Query("USD", description="Currency code for price display"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get single product with stock, variant stock, and currency info.
    
    Includes:
    - Product stock level
    - Each variant's stock level (visible to customers)
    - Currency conversion
    """
    product_service = ProductService(db)
    product_repo = ProductRepository(db)
    inventory_service = SimpleInventoryService(product_repo)
    
    product = await product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Add stock level
    product.stock_quantity = await inventory_service.get_stock_level(product.id)
    product.in_stock = product.stock_quantity > 0
    
    # Add variant stock levels (visible to all customers)
    if hasattr(product, 'variants') and product.variants:
        for variant in product.variants:
            variant.stock_quantity = variant.stock_quantity if hasattr(variant, 'stock_quantity') else 0
            variant.in_stock = variant.stock_quantity > 0
    
    # Convert price if needed
    if currency != "USD" and hasattr(product, 'price_cents'):
        currency_service = CurrencyConversionService()
        product.display_currency = currency
        product.display_price = currency_service.convert("USD", currency, product.price_cents / 100)
    
    return product


@router.post("", response_model=ProductResponse, dependencies=[Depends(rate_limiter_moderate)])
async def create_product(
    product_data: ProductCreateRequest,
    current_user=Depends(get_current_seller),  # Sellers or admins can create products
    db: AsyncSession = Depends(get_db)
):
    """Create a new product (Seller/Admin only)"""
    product_service = ProductService(db)
    
    product = await product_service.create_product(
        name=product_data.name,
        description=product_data.description,
        price_cents=product_data.price_cents,
        seller_id=current_user.id
    )
    
    return product
