from pydantic import BaseModel, Field
from typing import Optional

class SellerProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category_id: int
    subcategory_id: Optional[int] = None
    img_url: Optional[str] = None

class SellerProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    img_url: Optional[str] = None

class SellerProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category_id: int
    subcategory_id: Optional[int] = None
    img_url: Optional[str] = None
    seller_id: int

class SellerDeleteResponse(BaseModel):
    result: bool
