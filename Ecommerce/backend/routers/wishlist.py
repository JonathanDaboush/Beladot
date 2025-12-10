"""
Wishlist Routes
Handles user wishlist functionality
- Add product to wishlist
- Remove from wishlist
- View wishlist
- Move wishlist item to cart
- Clear wishlist
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from database import get_db
from Utilities.auth import get_current_active_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/wishlist", tags=["Wishlist"])


class AddToWishlistRequest(BaseModel):
    product_id: str


@router.get("", dependencies=[Depends(rate_limiter_moderate)])
async def get_wishlist(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's wishlist with product details"""
    from Models.Wishlist import Wishlist
    from Models.WishlistItem import WishlistItem
    from Models.Product import Product
    from sqlalchemy import select
    
    # Get or create wishlist
    result = await db.execute(
        select(Wishlist).where(Wishlist.user_id == current_user.id)
    )
    wishlist = result.scalar_one_or_none()
    
    if not wishlist:
        wishlist = Wishlist(user_id=current_user.id)
        db.add(wishlist)
        await db.commit()
        await db.refresh(wishlist)
        return {"items": [], "total_items": 0}
    
    # Get wishlist items with product details
    result = await db.execute(
        select(WishlistItem, Product)
        .join(Product)
        .where(WishlistItem.wishlist_id == wishlist.id)
    )
    items_with_products = result.all()
    
    # Format response
    items_list = [
        {
            "id": item.id,
            "product_id": item.product_id,
            "added_at": item.created_at,
            "product": {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price_cents / 100 if product.price_cents else 0,
                "currency": product.currency,
                "image_url": product.image_url,
                "in_stock": product.quantity > 0,
                "quantity": product.quantity
            }
        }
        for item, product in items_with_products
    ]
    
    return {
        "items": items_list,
        "total_items": len(items_list)
    }


@router.post("", dependencies=[Depends(rate_limiter_moderate)])
async def add_to_wishlist(
    data: AddToWishlistRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Add product to wishlist"""
    from Models.Wishlist import Wishlist
    from Models.WishlistItem import WishlistItem
    from Models.Product import Product
    from sqlalchemy import select, and_
    
    # Check if product exists
    result = await db.execute(select(Product).where(Product.id == data.product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get or create wishlist
    result = await db.execute(
        select(Wishlist).where(Wishlist.user_id == current_user.id)
    )
    wishlist = result.scalar_one_or_none()
    
    if not wishlist:
        wishlist = Wishlist(user_id=current_user.id)
        db.add(wishlist)
        await db.flush()
    
    # Check if already in wishlist
    result = await db.execute(
        select(WishlistItem).where(
            and_(
                WishlistItem.wishlist_id == wishlist.id,
                WishlistItem.product_id == data.product_id
            )
        )
    )
    existing_item = result.scalar_one_or_none()
    
    if existing_item:
        return {
            "message": "Product already in wishlist",
            "item_id": existing_item.id
        }
    
    # Add to wishlist
    wishlist_item = WishlistItem(
        wishlist_id=wishlist.id,
        product_id=data.product_id
    )
    db.add(wishlist_item)
    await db.commit()
    await db.refresh(wishlist_item)
    
    return {
        "item_id": wishlist_item.id,
        "message": "Product added to wishlist"
    }


@router.delete("/{item_id}", dependencies=[Depends(rate_limiter_moderate)])
async def remove_from_wishlist(
    item_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove product from wishlist"""
    from Models.WishlistItem import WishlistItem
    from Models.Wishlist import Wishlist
    from sqlalchemy import select
    
    # Get wishlist item
    result = await db.execute(
        select(WishlistItem, Wishlist)
        .join(Wishlist)
        .where(WishlistItem.id == item_id)
    )
    item_with_wishlist = result.one_or_none()
    
    if not item_with_wishlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist item not found"
        )
    
    item, wishlist = item_with_wishlist
    
    # Check ownership
    if wishlist.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only remove items from your own wishlist"
        )
    
    await db.delete(item)
    await db.commit()
    
    return {"message": "Product removed from wishlist"}


@router.post("/{item_id}/move-to-cart", dependencies=[Depends(rate_limiter_moderate)])
async def move_to_cart(
    item_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Move wishlist item to cart"""
    from Models.WishlistItem import WishlistItem
    from Models.Wishlist import Wishlist
    from Models.Cart import Cart
    from Models.CartItem import CartItem
    from sqlalchemy import select, and_
    
    # Get wishlist item
    result = await db.execute(
        select(WishlistItem, Wishlist)
        .join(Wishlist)
        .where(WishlistItem.id == item_id)
    )
    item_with_wishlist = result.one_or_none()
    
    if not item_with_wishlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist item not found"
        )
    
    item, wishlist = item_with_wishlist
    
    # Check ownership
    if wishlist.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only move items from your own wishlist"
        )
    
    # Get or create cart
    result = await db.execute(
        select(Cart).where(Cart.user_id == current_user.id)
    )
    cart = result.scalar_one_or_none()
    
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        await db.flush()
    
    # Check if already in cart
    result = await db.execute(
        select(CartItem).where(
            and_(
                CartItem.cart_id == cart.id,
                CartItem.product_id == item.product_id
            )
        )
    )
    cart_item = result.scalar_one_or_none()
    
    if cart_item:
        # Increment quantity if already in cart
        cart_item.quantity += 1
    else:
        # Add to cart
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=1
        )
        db.add(cart_item)
    
    # Remove from wishlist
    await db.delete(item)
    await db.commit()
    
    return {
        "message": "Product moved to cart",
        "cart_item_id": cart_item.id
    }


@router.delete("", dependencies=[Depends(rate_limiter_moderate)])
async def clear_wishlist(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Clear all items from wishlist"""
    from Models.Wishlist import Wishlist
    from Models.WishlistItem import WishlistItem
    from sqlalchemy import select, delete
    
    # Get wishlist
    result = await db.execute(
        select(Wishlist).where(Wishlist.user_id == current_user.id)
    )
    wishlist = result.scalar_one_or_none()
    
    if not wishlist:
        return {"message": "Wishlist is already empty"}
    
    # Delete all items
    await db.execute(
        delete(WishlistItem).where(WishlistItem.wishlist_id == wishlist.id)
    )
    await db.commit()
    
    return {"message": "Wishlist cleared successfully"}
