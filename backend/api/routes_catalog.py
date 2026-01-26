from fastapi import APIRouter, Depends, HTTPException
from urllib.parse import quote
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.persistance.db_dependency import get_db
from backend.persistance.product import Product
from backend.repositories.repository.product_repository import ProductRepository
from backend.repositories.repository.product_image_repository import ProductImageRepository
from backend.persistance.category import Category
from backend.persistance.subcategory import Subcategory
from backend.repositories.repository.product_variant_repository import ProductVariantRepository
from backend.schemas.schemas_catalog import (
    CartValidationRequest,
    CartValidationResponse,
    CartValidationItemResult,
)

catalog_router = APIRouter(prefix="/api/v1/catalog", tags=["catalog"])
public_router = APIRouter(tags=["catalog"])


def _static_url(path: str | None) -> str | None:
    if not path:
        return None
    # Normalize Windows paths to forward slashes, ensure single /static prefix, then URL-encode
    normalized = str(path).replace("\\", "/")
    if normalized.startswith("/static/"):
        raw = normalized
    else:
        raw = f"/static/{normalized.lstrip('/')}"
    return quote(raw, safe="/")

def _serialize_product_basic(p: Product, image_url: Optional[str] = None):
    return {
        "id": p.product_id,
        "name": getattr(p, "title", None) or "Product",
        "description": getattr(p, "description", None) or "",
        "price": float(p.price) if getattr(p, "price", None) is not None else 0.0,
        "currency": getattr(p, "currency", None) or "USD",
        "image_url": image_url,
        # keep ids for linking
        "category_id": getattr(p, "category_id", None),
        "subcategory_id": getattr(p, "subcategory_id", None),
        # human-readable names populated in list/detail handlers
        "category": None,
        "subcategory": None,
        "subcategory_name": None,
        "variants": [],
    }

@catalog_router.get("/products")
async def list_products(db: AsyncSession = Depends(get_db)):
    """Public: list active products. Minimal fields for catalog browsing."""
    cols = (
        Product.product_id,
        Product.title,
        Product.description,
        Product.price,
        Product.currency,
        Product.category_id,
        Product.subcategory_id,
    )
    result = await db.execute(select(*cols).filter(Product.is_active == True))
    rows = result.all()
    image_repo = ProductImageRepository(db)
    items = []
    for row in rows:
        pid = row[0]
        images = await image_repo.get_by_product_id(pid)
        # Primary product image (if any), normalized
        image_url = _static_url(images[0]) if images else None
        # Resolve category/subcategory names
        cat_name = None
        subcat_name = None
        cat_img = None
        subcat_img = None
        if row[5] is not None:
            c_row = (await db.execute(select(Category.name, Category.image_url).filter(Category.category_id == row[5]))).first()
            if c_row:
                cat_name = c_row[0]
                cat_img = c_row[1]
        if row[6] is not None:
            s_row = (await db.execute(select(Subcategory.name, Subcategory.image_url).filter(Subcategory.subcategory_id == row[6]))).first()
            if s_row:
                subcat_name = s_row[0]
                subcat_img = s_row[1]
        # Fallback to subcategory image, then category image
        if not image_url and subcat_img:
            image_url = _static_url(subcat_img)
        if not image_url and cat_img:
            image_url = _static_url(cat_img)
        item = {
            "id": pid,
            "name": row[1] or "Product",
            "description": row[2] or "",
            "price": float(row[3] or 0.0),
            "currency": row[4] or "USD",
            "image_url": image_url,
            "category_id": row[5],
            "subcategory_id": row[6],
            "category": cat_name,
            "subcategory": subcat_name,
            "subcategory_name": subcat_name,
            "variants": [],
        }
        items.append(item)
    return {"items": items}

async def _get_product_detail(product_id: int, db: AsyncSession):
    image_repo = ProductImageRepository(db)
    cols = (
        Product.product_id,
        Product.title,
        Product.description,
        Product.price,
        Product.currency,
        Product.category_id,
        Product.subcategory_id,
        Product.is_active,
    )
    result = await db.execute(select(*cols).filter(Product.product_id == product_id, Product.is_active == True))
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    pid = row[0]
    images = await image_repo.get_by_product_id(pid)
    image_url = _static_url(images[0]) if images else None
    cat_name = None
    subcat_name = None
    cat_img = None
    subcat_img = None
    if row[5] is not None:
        c_row = (await db.execute(select(Category.name, Category.image_url).filter(Category.category_id == row[5]))).first()
        if c_row:
            cat_name = c_row[0]
            cat_img = c_row[1]
    if row[6] is not None:
        s_row = (await db.execute(select(Subcategory.name, Subcategory.image_url).filter(Subcategory.subcategory_id == row[6]))).first()
        if s_row:
            subcat_name = s_row[0]
            subcat_img = s_row[1]
    if not image_url and subcat_img:
        image_url = _static_url(subcat_img)
    if not image_url and cat_img:
        image_url = _static_url(cat_img)
    item = {
        "id": pid,
        "name": row[1] or "Product",
        "description": row[2] or "",
        "price": float(row[3] or 0.0),
        "currency": row[4] or "USD",
        "image_url": image_url,
        "category_id": row[5],
        "subcategory_id": row[6],
        "category": cat_name,
        "subcategory": subcat_name,
        "subcategory_name": subcat_name,
        "variants": [],
    }
    return {"product": item}

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
        # Read product attributes as plain columns to avoid ORM instance detachment issues
        prod_cols = (Product.product_id, Product.price, Product.is_active)
        prod_row = (await db.execute(select(*prod_cols).filter(Product.product_id == item.product_id))).first()
        product = None
        if prod_row:
            product = {
                "product_id": prod_row[0],
                "price": float(prod_row[1] or 0),
                "is_active": bool(prod_row[2]),
            }
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
            # Read variant attributes as plain columns
            from backend.persistance.product_variant import ProductVariant
            var_cols = (ProductVariant.variant_id, ProductVariant.quantity, ProductVariant.price, ProductVariant.is_active)
            var_row = (await db.execute(select(*var_cols).filter(ProductVariant.variant_id == item.variant_id))).first()
            variant = None
            if var_row:
                variant = {
                    "variant_id": var_row[0],
                    "quantity": int(var_row[1] or 0),
                    "price": float(var_row[2] or 0),
                    "is_active": bool(var_row[3]),
                }
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
            stock = int(variant["quantity"])
            price = float(variant["price"] or product["price"])
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
            price = float(product["price"])
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

from sqlalchemy.orm import selectinload
# --------------------------------------------------
# Category/Subcategory endpoints for frontend pages
# --------------------------------------------------
@public_router.get("/api/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Category).options(selectinload(Category.subcategories))
    )
    categories = []
    for category in result.scalars().unique():
        subs = [
            {
                "subcategory_id": sub.subcategory_id,
                "name": sub.name or "",
                "image_url": _static_url(sub.image_url),
            }
            for sub in category.subcategories
        ]
        categories.append({
            "category_id": category.category_id,
            "name": category.name or "",
            "image_url": _static_url(category.image_url),
            "subcategories": subs,
        })
    return {"categories": categories}

@public_router.get("/api/category/{category_id}")
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    row = (await db.execute(select(Category.category_id, Category.name, Category.image_url).filter(Category.category_id == category_id))).first()
    if not row:
        raise HTTPException(status_code=404, detail="Category not found")
    cid, name, img = row
    sub_rows = (await db.execute(select(Subcategory.subcategory_id, Subcategory.name, Subcategory.image_url).filter(Subcategory.category_id == cid))).all()
    subs = [
        {
            "subcategory_id": s_id,
            "name": s_name or "",
            "image_url": _static_url(s_img),
        }
        for (s_id, s_name, s_img) in sub_rows
    ]
    return {
        "category": {
            "category_id": cid,
            "name": name or "",
            "image_url": _static_url(img),
        },
        "subcategories": subs,
    }
