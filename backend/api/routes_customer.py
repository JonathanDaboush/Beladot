from backend.persistance.db_dependency import get_db
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from backend.schemas_customer import (
    CartItemAdd, CartItemResponse, WishlistItemAdd, WishlistItemResponse
)

router = APIRouter(prefix="/api/v1/customer", tags=["customer"])

def require_role(role: str):
    async def dependency(request: Request):
        identity = getattr(request.state, "identity", {})
        if identity.get("role") != role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return identity
    return dependency

from backend.services.customerServices import add_item_to_cart, add_item_to_wishlist

@router.post("/cart/items", response_model=CartItemResponse)
async def add_item_to_cart_route(
    item: CartItemAdd,
    identity=Depends(require_role("user")),
    db=Depends(get_db),
):
    return await add_item_to_cart(
        user_id=identity["user_id"],
        product_id=item.product_id,
        quantity=item.quantity,
        db=db
    )

@router.post("/wishlist/items", response_model=WishlistItemResponse)
async def add_item_to_wishlist_route(
    item: WishlistItemAdd,
    identity=Depends(require_role("user")),
    db=Depends(get_db),
):
    return await add_item_to_wishlist(
        user_id=identity["user_id"],
        product_id=item.product_id,
        quantity=item.quantity,
        db=db
    )
