from backend.persistance.db_dependency import get_db
from fastapi import APIRouter, Depends, HTTPException, Request
from backend.schemas_seller import (
    SellerProductCreate, SellerProductUpdate, SellerProductResponse
)
from backend.services import sellerServices

router = APIRouter(prefix="/api/v1/seller", tags=["seller"])

def require_role(role: str):
    async def dependency(request: Request):
        identity = getattr(request.state, "identity", {})
        if identity.get("role") != role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return identity
    return dependency

async def dummy_seller_service():
    class DummyService:
        async def create_product(self, product):
            return product
        async def edit_product(self, product_id, **kwargs):
            return {"id": product_id, **kwargs}
    return DummyService()

@router.post("/products", response_model=SellerProductResponse)
async def create_product(
    product: SellerProductCreate,
    # sellerService dependency removed for import safety
    identity=Depends(require_role("seller")),
    db=Depends(get_db),
):
    return await sellerServices.create_product(seller_id=identity["seller_id"], db=db, **product.dict())

@router.put("/products/{product_id}", response_model=SellerProductResponse)
async def update_product(
    product_id: int,
    product: SellerProductUpdate,
    # sellerService dependency removed for import safety
    identity=Depends(require_role("seller")),
    db=Depends(get_db),
):
    return sellerServices.edit_product(seller_id=identity["seller_id"], product_id=product_id, db=db, **product.dict(exclude_unset=True))
