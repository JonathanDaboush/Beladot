"""
Catalog Management Routes
Handles product catalog operations:
- Product CRUD (sellers, CS, managers)
- Variant management (sellers only)
- Category/Subcategory management (admins only)
- Product listing (all users)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime

from database import get_db
from Utilities.auth import get_current_active_user, get_current_admin_user
from Utilities.rate_limiting import rate_limiter_moderate
from Models.User import UserRole

router = APIRouter(prefix="/api/catalog", tags=["Catalog"])


# ============================================================================
# CATEGORY & SUBCATEGORY MANAGEMENT (Admin Only)
# ============================================================================

@router.post("/categories", dependencies=[Depends(rate_limiter_moderate)])
async def create_category(
    name: str,
    description: str = None,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create main category (Admin only).
    
    Examples: Electronics, Clothing, Home & Garden
    """
    from sqlalchemy import select
    from Models.Category import Category
    
    # Check if category already exists
    result = await db.execute(
        select(Category).where(Category.name == name)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists"
        )
    
    category = Category(
        name=name,
        description=description,
        is_active=True
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "message": "Category created successfully"
    }


@router.post("/categories/{category_id}/subcategories", dependencies=[Depends(rate_limiter_moderate)])
async def create_subcategory(
    category_id: int,
    name: str,
    description: str = None,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create subcategory under a category (Admin only).
    
    Examples: Under Electronics -> Televisions, Phones, Computers
    """
    from sqlalchemy import select
    from Models.Category import Category, Subcategory
    
    # Verify category exists
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check if subcategory already exists
    result = await db.execute(
        select(Subcategory).where(
            Subcategory.category_id == category_id,
            Subcategory.name == name
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subcategory already exists"
        )
    
    subcategory = Subcategory(
        category_id=category_id,
        name=name,
        description=description,
        is_active=True
    )
    db.add(subcategory)
    await db.commit()
    await db.refresh(subcategory)
    
    return {
        "id": subcategory.id,
        "category_id": category_id,
        "category_name": category.name,
        "name": subcategory.name,
        "description": subcategory.description,
        "message": "Subcategory created successfully"
    }


@router.get("/categories", dependencies=[Depends(rate_limiter_moderate)])
async def list_categories(
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    List all categories with their subcategories.
    
    Available to all users for browsing products.
    """
    from sqlalchemy import select
    from Models.Category import Category, Subcategory
    
    query = select(Category)
    if not include_inactive:
        query = query.where(Category.is_active == True)
    
    result = await db.execute(query.order_by(Category.name))
    categories = result.scalars().all()
    
    # Add subcategories
    category_list = []
    for cat in categories:
        result = await db.execute(
            select(Subcategory).where(Subcategory.category_id == cat.id)
        )
        subcats = result.scalars().all()
        
        category_list.append({
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "is_active": cat.is_active,
            "subcategories": [
                {
                    "id": sub.id,
                    "name": sub.name,
                    "description": sub.description,
                    "is_active": sub.is_active
                }
                for sub in subcats
            ]
        })
    
    return {"categories": category_list}


# ============================================================================
# PRODUCT CRUD (Sellers, CS, Managers)
# ============================================================================

@router.post("/products", dependencies=[Depends(rate_limiter_moderate)])
async def create_product(
    name: str,
    description: str,
    price_cents: int,
    category_id: int,
    subcategory_id: int = None,
    sku: str = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create product.
    
    - Sellers: Create for themselves
    - CS/Managers: Create for any seller (admin mode)
    """
    from Services.CatalogService import CatalogService
    from sqlalchemy import select
    from Models.Seller import Seller
    
    # Determine seller_id
    seller_id = None
    if current_user.role == UserRole.SELLER:
        # Get seller record
        result = await db.execute(
            select(Seller).where(Seller.user_id == current_user.id)
        )
        seller = result.scalar_one_or_none()
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seller profile not found"
            )
        seller_id = seller.id
    elif current_user.role in [UserRole.CUSTOMER_SERVICE, UserRole.MANAGER, UserRole.ADMIN]:
        # CS/Managers can create products (need seller_id in payload)
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers, CS, or managers can create products"
        )
    
    catalog_service = CatalogService(db)
    
    product_data = {
        "name": name,
        "description": description,
        "price_cents": price_cents,
        "category_id": category_id,
        "subcategory_id": subcategory_id,
        "sku": sku or f"PRD{datetime.now().timestamp()}",
        "seller_id": seller_id
    }
    
    product = await catalog_service.create_product(
        payload=product_data,
        actor_id=current_user.id
    )
    
    return {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "price_cents": product.price_cents,
        "message": "Product created successfully"
    }


@router.put("/products/{product_id}", dependencies=[Depends(rate_limiter_moderate)])
async def update_product(
    product_id: int,
    name: str = None,
    description: str = None,
    price_cents: int = None,
    category_id: int = None,
    subcategory_id: int = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update product.
    
    - Sellers: Update own products only
    - CS/Managers: Update any product
    """
    from Services.CatalogService import CatalogService
    from sqlalchemy import select
    from Models.Product import Product
    from Models.Seller import Seller
    
    # Get product
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check ownership for sellers
    if current_user.role == UserRole.SELLER:
        result = await db.execute(
            select(Seller).where(Seller.user_id == current_user.id)
        )
        seller = result.scalar_one_or_none()
        
        if not seller or product.seller_id != seller.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own products"
            )
    elif current_user.role not in [UserRole.CUSTOMER_SERVICE, UserRole.MANAGER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Build update data
    update_data = {}
    if name:
        update_data['name'] = name
    if description:
        update_data['description'] = description
    if price_cents is not None:
        update_data['price_cents'] = price_cents
    if category_id:
        update_data['category_id'] = category_id
    if subcategory_id:
        update_data['subcategory_id'] = subcategory_id
    
    catalog_service = CatalogService(db)
    updated_product = await catalog_service.update_product(
        product_id=product_id,
        patch=update_data,
        actor_id=current_user.id
    )
    
    return {
        "id": updated_product.id,
        "name": updated_product.name,
        "price_cents": updated_product.price_cents,
        "message": "Product updated successfully"
    }


# ============================================================================
# VARIANT MANAGEMENT (Sellers Only)
# ============================================================================

@router.post("/products/{product_id}/variants", dependencies=[Depends(rate_limiter_moderate)])
async def create_variant(
    product_id: int,
    sku: str,
    name: str,
    price_cents: int,
    stock_quantity: int = 0,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create product variant (Seller only).
    
    Examples: Different sizes, colors, configurations
    """
    from Services.CatalogService import CatalogService
    from sqlalchemy import select
    from Models.Product import Product
    from Models.Seller import Seller
    
    # Only sellers can create variants
    if current_user.role != UserRole.SELLER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can create variants"
        )
    
    # Verify product exists and seller owns it
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    result = await db.execute(
        select(Seller).where(Seller.user_id == current_user.id)
    )
    seller = result.scalar_one_or_none()
    
    if not seller or product.seller_id != seller.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create variants for your own products"
        )
    
    catalog_service = CatalogService(db)
    variant = await catalog_service.create_variant(
        product_id=product_id,
        variant_payload={
            "sku": sku,
            "name": name,
            "price_cents": price_cents,
            "stock_quantity": stock_quantity
        },
        actor_id=current_user.id
    )
    
    return {
        "id": variant.id,
        "sku": variant.sku,
        "name": variant.name,
        "price_cents": variant.price_cents,
        "message": "Variant created successfully"
    }


@router.put("/variants/{variant_id}", dependencies=[Depends(rate_limiter_moderate)])
async def update_variant(
    variant_id: int,
    name: str = None,
    price_cents: int = None,
    stock_quantity: int = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update product variant (Seller only).
    """
    from Services.CatalogService import CatalogService
    from sqlalchemy import select
    from Models.ProductVariant import ProductVariant
    from Models.Product import Product
    from Models.Seller import Seller
    
    # Only sellers can update variants
    if current_user.role != UserRole.SELLER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can update variants"
        )
    
    # Get variant and verify ownership
    result = await db.execute(
        select(ProductVariant).where(ProductVariant.id == variant_id)
    )
    variant = result.scalar_one_or_none()
    
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant not found"
        )
    
    # Check product ownership
    result = await db.execute(
        select(Product).where(Product.id == variant.product_id)
    )
    product = result.scalar_one_or_none()
    
    result = await db.execute(
        select(Seller).where(Seller.user_id == current_user.id)
    )
    seller = result.scalar_one_or_none()
    
    if not seller or product.seller_id != seller.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update variants for your own products"
        )
    
    # Build update
    update_data = {}
    if name:
        update_data['name'] = name
    if price_cents is not None:
        update_data['price_cents'] = price_cents
    if stock_quantity is not None:
        update_data['stock_quantity'] = stock_quantity
    
    catalog_service = CatalogService(db)
    updated_variant = await catalog_service.update_variant(
        variant_id=variant_id,
        patch=update_data,
        actor_id=current_user.id
    )
    
    return {
        "id": updated_variant.id,
        "name": updated_variant.name,
        "price_cents": updated_variant.price_cents,
        "message": "Variant updated successfully"
    }


# ============================================================================
# IMAGE UPLOAD (Sellers Only)
# ============================================================================

@router.post("/products/{product_id}/images", dependencies=[Depends(rate_limiter_moderate)])
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    alt_text: str = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload product image (Seller only).
    """
    from Services.CatalogService import CatalogService
    from sqlalchemy import select
    from Models.Product import Product
    from Models.Seller import Seller
    
    # Only sellers can upload images
    if current_user.role != UserRole.SELLER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can upload product images"
        )
    
    # Verify product ownership
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    result = await db.execute(
        select(Seller).where(Seller.user_id == current_user.id)
    )
    seller = result.scalar_one_or_none()
    
    if not seller or product.seller_id != seller.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload images for your own products"
        )
    
    # Upload image
    catalog_service = CatalogService(db)
    image = await catalog_service.upload_image(
        product_id=product_id,
        variant_id=None,
        file_stream=file.file,
        filename=file.filename,
        actor_id=current_user.id
    )
    
    return {
        "id": image.id,
        "product_id": product_id,
        "filename": file.filename,
        "message": "Image uploaded successfully"
    }
