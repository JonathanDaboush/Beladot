"""
Seller Routes
Handles seller-specific operations (sales reports, product management, payouts)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
from typing import Optional

from database import get_db
from Services.SellerService import SellerService
from Services.ProductService import ProductService
from Services.SimpleInventoryService import SimpleInventoryService
from Repositories.ProductRepository import ProductRepository
from Repositories.OrderRepository import OrderRepository
from Repositories.OrderItemRepository import OrderItemRepository
from Repositories.ReturnRepository import ReturnRepository
from Repositories.RefundRepository import RefundRepository
from Repositories.SellerPayoutRepository import SellerPayoutRepository
from Utilities.auth import get_current_seller
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/seller", tags=["Seller"])


@router.get("/sales", dependencies=[Depends(rate_limiter_moderate)])
async def get_sales_report(
    current_seller=Depends(get_current_seller),
    db: AsyncSession = Depends(get_db)
):
    """Get seller's sales report"""
    seller_service = SellerService(db)
    
    sales = await seller_service.get_sales_report(current_seller.id)
    
    return {"sales": sales}


@router.get("/products", dependencies=[Depends(rate_limiter_moderate)])
async def get_seller_products(
    current_seller=Depends(get_current_seller),
    db: AsyncSession = Depends(get_db)
):
    """Get all products owned by seller with stock levels"""
    seller_service = SellerService(db)
    product_repo = ProductRepository(db)
    inventory_service = SimpleInventoryService(product_repo)
    
    products = await seller_service.get_seller_products(current_seller.id)
    
    # Add stock levels to each product
    for product in products:
        product.stock_quantity = await inventory_service.get_stock_level(product.id)
    
    return {"products": products}


@router.patch("/products/{product_id}", dependencies=[Depends(rate_limiter_moderate)])
async def update_seller_product(
    product_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    price_cents: Optional[int] = None,
    current_seller=Depends(get_current_seller),
    db: AsyncSession = Depends(get_db)
):
    """Edit product details (seller must own the product)"""
    product_service = ProductService(db)
    
    # Verify seller owns this product
    product = await product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product.seller_id != current_seller.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own products"
        )
    
    # Update product
    update_data = {}
    if name:
        update_data['name'] = name
    if description:
        update_data['description'] = description
    if price_cents is not None:
        update_data['price_cents'] = price_cents
    
    updated_product = await product_service.update_product(product_id, update_data)
    
    return {"message": "Product updated successfully", "product": updated_product}


@router.patch("/products/{product_id}/stock", dependencies=[Depends(rate_limiter_moderate)])
async def update_product_stock(
    product_id: int,
    quantity: int = Query(..., description="New stock quantity (use negative to reduce)"),
    current_seller=Depends(get_current_seller),
    db: AsyncSession = Depends(get_db)
):
    """Update product stock (sellers can increase or decrease their own products)"""
    product_service = ProductService(db)
    product_repo = ProductRepository(db)
    inventory_service = SimpleInventoryService(product_repo)
    
    # Verify seller owns this product
    product = await product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product.seller_id != current_seller.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage stock for your own products"
        )
    
    # Update stock level
    await inventory_service.update_stock_level(product_id, quantity)
    new_stock = await inventory_service.get_stock_level(product_id)
    
    return {"message": "Stock updated successfully", "product_id": product_id, "new_stock": new_stock}


@router.get("/earnings", dependencies=[Depends(rate_limiter_moderate)])
async def calculate_earnings(
    start_date: Optional[date] = Query(None, description="Start date for earnings calculation"),
    end_date: Optional[date] = Query(None, description="End date for earnings calculation"),
    current_seller=Depends(get_current_seller),
    db: AsyncSession = Depends(get_db)
):
    """Calculate seller earnings for delivered products (excluding returns/refunds)"""
    from Repositories.SellerRepository import SellerRepository
    from Repositories.SellerFinanceRepository import SellerFinanceRepository
    
    # Default to last 30 days if not specified
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    seller_repo = SellerRepository(db)
    finance_repo = SellerFinanceRepository(db)
    order_repo = OrderRepository(db)
    order_item_repo = OrderItemRepository(db)
    return_repo = ReturnRepository(db)
    refund_repo = RefundRepository(db)
    
    seller_service = SellerService(seller_repo, finance_repo)
    
    earnings = await seller_service.calculate_earnings(
        seller_id=current_seller.id,
        start_date=start_date,
        end_date=end_date,
        order_repo=order_repo,
        order_item_repo=order_item_repo,
        return_repo=return_repo,
        refund_repo=refund_repo
    )
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        **earnings
    }


@router.post("/payout", dependencies=[Depends(rate_limiter_moderate)])
async def trigger_payout(
    current_seller=Depends(get_current_seller),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger payout for eligible sales.
    Only processes orders delivered 14+ days ago (return window closed).
    """
    from Repositories.SellerRepository import SellerRepository
    from Repositories.SellerFinanceRepository import SellerFinanceRepository
    
    payout_date = date.today()
    
    seller_repo = SellerRepository(db)
    finance_repo = SellerFinanceRepository(db)
    order_repo = OrderRepository(db)
    order_item_repo = OrderItemRepository(db)
    return_repo = ReturnRepository(db)
    refund_repo = RefundRepository(db)
    payout_repo = SellerPayoutRepository(db)
    
    seller_service = SellerService(seller_repo, finance_repo)
    
    payout = await seller_service.trigger_payout(
        seller_id=current_seller.id,
        payout_date=payout_date,
        order_repo=order_repo,
        order_item_repo=order_item_repo,
        return_repo=return_repo,
        refund_repo=refund_repo,
        payout_repo=payout_repo
    )
    
    if not payout:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No eligible orders for payout (must be delivered 14+ days ago)"
        )
    
    return {
        "message": "Payout initiated successfully",
        "payout_id": payout.id,
        "amount": payout.amount,
        "status": payout.status
    }


@router.get("/payouts", dependencies=[Depends(rate_limiter_moderate)])
async def get_payout_history(
    current_seller=Depends(get_current_seller),
    db: AsyncSession = Depends(get_db)
):
    """Get seller payout history with detailed breakdown"""
    payout_repo = SellerPayoutRepository(db)
    order_item_repo = OrderItemRepository(db)
    
    # Get all payouts for this seller
    payouts = await payout_repo.get_by_seller(current_seller.id)
    
    # Enrich each payout with product details
    enriched_payouts = []
    for payout in payouts:
        # Parse order IDs from related_order_ids
        order_ids = [int(oid) for oid in payout.related_order_ids.split(',') if oid.strip()]
        
        # Get order items for these orders
        items = await order_item_repo.get_by_orders_and_seller(order_ids, current_seller.id)
        
        # Only include items that were paid out
        paid_items = [item for item in items if item.paid_out]
        
        # Build product summary
        product_summary = {}
        for item in paid_items:
            if item.product_name not in product_summary:
                product_summary[item.product_name] = {
                    'quantity': 0,
                    'total_sales': 0
                }
            product_summary[item.product_name]['quantity'] += item.quantity
            product_summary[item.product_name]['total_sales'] += item.total_price_cents
        
        enriched_payouts.append({
            'payout_id': payout.id,
            'amount': payout.amount,
            'payout_date': payout.payout_date,
            'status': payout.status,
            'product_summary': product_summary,
            'total_items': len(paid_items),
            'order_count': len(order_ids)
        })
    
    return {"payouts": enriched_payouts}


# ===== VARIANT CATEGORY MANAGEMENT =====

@router.get("/variant-categories", dependencies=[Depends(rate_limiter_moderate)])
async def get_variant_categories(
    current_seller=Depends(get_current_seller),
    db: AsyncSession = Depends(get_db)
):
    """
    Get seller's variant categories with subcategories.
    
    Variant categories are seller-specific ways to organize variants:
    - Example: Seller creates "Colors" category with "Red", "Blue", "Green" subcategories
    - Example: Seller creates "Sizes" category with "Small", "Medium", "Large" subcategories
    """
    from sqlalchemy import select
    from Models.CategorySystem import VariantCategory, VariantSubcategory
    
    result = await db.execute(
        select(VariantCategory)
        .where(VariantCategory.seller_id == current_seller.id)
        .where(VariantCategory.is_active == True)
    )
    categories = result.scalars().all()
    
    # Load subcategories for each
    enriched_categories = []
    for cat in categories:
        result = await db.execute(
            select(VariantSubcategory)
            .where(VariantSubcategory.variant_category_id == cat.id)
            .where(VariantSubcategory.is_active == True)
        )
        subcategories = result.scalars().all()
        
        enriched_categories.append({
            'id': cat.id,
            'name': cat.name,
            'description': cat.description,
            'subcategories': [
                {'id': sub.id, 'name': sub.name, 'description': sub.description}
                for sub in subcategories
            ]
        })
    
    return {"variant_categories": enriched_categories}


@router.post("/variant-categories", dependencies=[Depends(rate_limiter_moderate)])
async def create_variant_category(
    name: str,
    description: Optional[str] = None,
    current_seller=Depends(get_current_seller),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new variant category for seller.
    
    Example: Create "Colors" category to organize color variants.
    """
    from Models.CategorySystem import VariantCategory
    
    category = VariantCategory(
        seller_id=current_seller.id,
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
        "message": f"Variant category '{name}' created successfully"
    }


@router.post("/variant-categories/{category_id}/subcategories", dependencies=[Depends(rate_limiter_moderate)])
async def create_variant_subcategory(
    category_id: int,
    name: str,
    description: Optional[str] = None,
    current_seller=Depends(get_current_seller),
    db: AsyncSession = Depends(get_db)
):
    """
    Create subcategory under variant category.
    
    Example: Under "Colors" category, create "Red", "Blue", "Green" subcategories.
    """
    from sqlalchemy import select
    from Models.CategorySystem import VariantCategory, VariantSubcategory
    
    # Verify seller owns this category
    result = await db.execute(
        select(VariantCategory).where(VariantCategory.id == category_id)
    )
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant category not found"
        )
    
    if category.seller_id != current_seller.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create subcategory in another seller's category"
        )
    
    subcategory = VariantSubcategory(
        variant_category_id=category_id,
        name=name,
        description=description,
        is_active=True
    )
    
    db.add(subcategory)
    await db.commit()
    await db.refresh(subcategory)
    
    return {
        "id": subcategory.id,
        "name": subcategory.name,
        "category_name": category.name,
        "message": f"Subcategory '{name}' created under '{category.name}'"
    }


@router.patch("/products/{product_id}/variants/{variant_id}/category", dependencies=[Depends(rate_limiter_moderate)])
async def assign_variant_category(
    product_id: int,
    variant_id: int,
    variant_category_id: Optional[int] = None,
    variant_subcategory_id: Optional[int] = None,
    current_seller=Depends(get_current_seller),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign variant categories to product variant.
    
    This allows sellers to organize their variants with custom categorization.
    Example: Assign variant to "Colors > Red" or "Sizes > Large"
    """
    from sqlalchemy import select
    from Models.Product import Product
    from Models.ProductVariant import ProductVariant
    
    # Verify seller owns product
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if product.seller_id != current_seller.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify another seller's product")
    
    # Get variant
    result = await db.execute(
        select(ProductVariant).where(ProductVariant.id == variant_id, ProductVariant.product_id == product_id)
    )
    variant = result.scalar_one_or_none()
    
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
    
    # Update variant categories
    variant.variant_category_id = variant_category_id
    variant.variant_subcategory_id = variant_subcategory_id
    
    await db.commit()
    await db.refresh(variant)
    
    return {
        "variant_id": variant.id,
        "variant_category_id": variant_category_id,
        "variant_subcategory_id": variant_subcategory_id,
        "message": "Variant category assignment updated"
    }

