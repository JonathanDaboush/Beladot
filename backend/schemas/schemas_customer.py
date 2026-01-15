from pydantic import BaseModel, Field
from typing import Optional, List

class CartItemAdd(BaseModel):
    product_id: int
    quantity: int
    db: Optional[str] = None

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    user_id: int

class WishlistItemAdd(BaseModel):
    product_id: int
    db: Optional[str] = None

class WishlistItemResponse(BaseModel):
    id: int
    product_id: int
    user_id: int

class CustomerDeleteResponse(BaseModel):
    result: bool
