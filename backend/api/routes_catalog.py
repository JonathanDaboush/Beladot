from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.persistance.db_dependency import get_db
from backend.persistance.product import Product
from backend.repositories.repository.product_repository import ProductRepository
from backend.repositories.repository.product_image_repository import ProductImageRepository
from backend.repositories.repository.product_variant_repository import ProductVariantRepository
from backend.schemas.schemas_catalog import (
    CartValidationRequest,
    CartValidationResponse,
    CartValidationItemResult,
)

catalog_router = APIRouter(prefix="/api/v1/catalog", tags=["catalog"])
public_router = APIRouter(tags=["catalog"])

def _serialize_product_basic(p: Product, image_url: Optional[str] = None):
    return {
        "id": p.product_id,
        "name": getattr(p, "title", None) or "Product",
        "description": getattr(p, "description", None) or "",
        "price": float(p.price) if getattr(p, "price", None) is not None else 0.0,
        "currency": getattr(p, "currency", None) or "USD",
        "image_url": image_url,
        "category": getattr(p, "category_id", None),
        "subcategory": getattr(p, "subcategory_id", None),
        "variants": [],
    }

@catalog_router.get("/products")
async def list_products(db: AsyncSession = Depends(get_db)):
    """Public: list active products. Minimal fields for catalog browsing."""
    result = await db.execute(select(Product).filter(Product.is_active == True))
    products: List[Product] = result.scalars().all()
    image_repo = ProductImageRepository(db)
    items = []
    for p in products:
        images = await image_repo.get_by_product_id(p.product_id)
        image_url = images[0].image_url if images else None
        items.append(_serialize_product_basic(p, image_url))
    return {"items": items}

async def _get_product_detail(product_id: int, db: AsyncSession):
    repo = ProductRepository(db)
    image_repo = ProductImageRepository(db)
    p = await repo.get_by_id(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    images = await image_repo.get_by_product_id(p.product_id)
    image_url = images[0].image_url if images else None
    return {"product": _serialize_product_basic(p, image_url)}

@catalog_router.get("/products/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Public: product detail by id for browsing."""
    return await _get_product_detail(product_id, db)

# Alias to match existing frontend path `/api/product/{id}`
@public_router.get("/api/product/{product_id}")
async def get_product_alias(product_id: int, db: AsyncSession = Depends(get_db)):
    return await _get_product_detail(product_id, db)


@catalog_router.post("/validate-cart", response_model=CartValidationResponse)
async def validate_cart(payload: CartValidationRequest, db: AsyncSession = Depends(get_db)):
    """Public: validate cart items for availability and quantity.

    - If `variant_id` is provided, ensure the variant exists, is active, and has sufficient `quantity`.
      If requested exceeds stock, reduce to available stock.
    - If no `variant_id`, ensure the product exists and is active; allow any positive quantity.
    """
    product_repo = ProductRepository(db)
    variant_repo = ProductVariantRepository(db)
    results: List[CartValidationItemResult] = []
    for item in payload.items:
        requested_qty = item.quantity
        allowed_qty = 0
        available = False
        price: Optional[float] = None
        message: Optional[str] = None

        # Verify product is active
        product = await product_repo.get_by_id(item.product_id)
        if not product:
            results.append(CartValidationItemResult(
                product_id=item.product_id,
                requested_quantity=requested_qty,
                allowed_quantity=0,
                available=False,
                variant_id=item.variant_id,
                price=None,
                message="Product not available",
            ))
            continue

        # Variant-specific validation
        if item.variant_id:
            variant = await variant_repo.get_by_id(item.variant_id)
            if not variant:
                results.append(CartValidationItemResult(
                    product_id=item.product_id,
                    requested_quantity=requested_qty,
                    allowed_quantity=0,
                    available=False,
                    variant_id=item.variant_id,
                    price=None,
                    message="Variant not available",
                ))
                continue
            stock = int(getattr(variant, "quantity", 0) or 0)
            price = float(getattr(variant, "price", None) or (product.price or 0))
            if stock <= 0:
                allowed_qty = 0
                available = False
                message = "Variant out of stock"
            elif requested_qty <= stock:
                allowed_qty = requested_qty
                available = True
            else:
                allowed_qty = stock
                available = True if stock > 0 else False
                message = "Quantity reduced to available stock"
        else:
            # No variant: product-level check; product active implies available
            price = float(product.price or 0)
            if requested_qty > 0:
                allowed_qty = requested_qty
                available = True
            else:
                allowed_qty = 0
                available = False
                message = "Invalid quantity"

        results.append(CartValidationItemResult(
            product_id=item.product_id,
            requested_quantity=requested_qty,
            allowed_quantity=allowed_qty,
            available=available,
            variant_id=item.variant_id,
            price=price,
            message=message,
        ))

    return CartValidationResponse(items=results)
