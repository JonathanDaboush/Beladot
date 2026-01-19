from pydantic import BaseModel, Field
from typing import List, Optional


class CartValidationItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    variant_id: Optional[int] = Field(None, gt=0)


class CartValidationRequest(BaseModel):
    items: List[CartValidationItem]


class CartValidationItemResult(BaseModel):
    product_id: int
    requested_quantity: int
    allowed_quantity: int
    available: bool
    variant_id: Optional[int] = None
    price: Optional[float] = None
    message: Optional[str] = None


class CartValidationResponse(BaseModel):
    items: List[CartValidationItemResult]
