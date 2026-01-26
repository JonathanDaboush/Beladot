from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.persistance.db_dependency import get_db
from backend.persistance.user import User
from backend.persistance.user_finance import UserFinance
from backend.persistance.customer_shipment import CustomerShipment
from backend.persistance.seller_snapshot import SellerSnapshot
from backend.schemas.schemas_auth import (
    UserRegisterRequest,
    UserUpdateRequest,
    SellerUpgradeRequest,
)

router = APIRouter(prefix="/api/v1", tags=["user"])

async def require_identity(request: Request):
    identity = getattr(request.state, "identity", {})
    if not identity or not identity.get("id"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return identity

@router.post("/public/register")
async def register_user(payload: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    # Uniqueness check on email
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    # Profile image rule: if provided, persist path in user record
    img_path = payload.profile_image
    u = User(
        full_name=payload.full_name,
        dob=payload.dob,
        password=payload.password,
        phone_number=payload.phone_number,
        email=payload.email,
        img_location=img_path or "",
        account_status="active",
    )
    db.add(u)
    await db.flush()
    # Optional finance info
    if payload.finance:
        f = UserFinance(
            user_id=u.user_id,
            bank=payload.finance.bank,
            pin=payload.finance.pin,
            cvv=payload.finance.cvv,
            credit_card_number=payload.finance.credit_card_number,
            account_type=payload.finance.account_type,
        )
        db.add(f)
    # Optional shipping info
    if payload.shipping and payload.shipping.postal_code:
        s = CustomerShipment(
            cs_id=None,
            customer_id=u.user_id,
            postal_code=payload.shipping.postal_code,
            street_line_1=payload.shipping.street_line_1,
            street_line_2=payload.shipping.street_line_2,
            city=payload.shipping.city,
            state_province=payload.shipping.state_province,
            country=payload.shipping.country,
        )
        db.add(s)
    await db.commit()
    await db.refresh(u)
    return {"user_id": u.user_id, "email": u.email, "status": u.account_status}

@router.put("/user/profile")
async def update_profile(payload: UserUpdateRequest, identity=Depends(require_identity), db: AsyncSession = Depends(get_db)):
    # Disallow password or ID changes via this endpoint
    forbidden_keys = {"password", "user_id", "finance_id", "shipment_id"}
    for k in forbidden_keys:
        if getattr(payload, k, None) is not None:
            raise HTTPException(status_code=400, detail=f"Field '{k}' cannot be edited here")
    u = await db.execute(select(User).where(User.user_id == identity["id"]))
    u = u.scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    # Apply simple updates
    for field in ["full_name", "dob", "email", "phone_number", "profile_image", "account_status"]:
        val = getattr(payload, field, None)
        if val is not None:
            if field == "profile_image":
                u.img_location = val
            elif field == "account_status":
                u.account_status = val
            else:
                setattr(u, field if field != "profile_image" else "img_location", val)
    # Finance update
    if payload.finance:
        fin = await db.execute(select(UserFinance).where(UserFinance.user_id == u.user_id))
        fin = fin.scalars().first()
        if not fin:
            fin = UserFinance(user_id=u.user_id)
            db.add(fin)
        for attr in ["bank", "credit_card_number", "cvv", "pin", "account_type"]:
            val = getattr(payload.finance, attr, None)
            if val is not None:
                setattr(fin, attr, val)
    # Shipping update
    if payload.shipping:
        ship = await db.execute(select(CustomerShipment).where(CustomerShipment.customer_id == u.user_id))
        ship = ship.scalars().first()
        if not ship:
            ship = CustomerShipment(customer_id=u.user_id)
            db.add(ship)
        for attr in ["postal_code", "street_line_1", "street_line_2", "city", "state_province", "country"]:
            val = getattr(payload.shipping, attr, None)
            if val is not None:
                setattr(ship, attr, val)
    await db.commit()
    return {"updated": True}

@router.post("/user/upgrade-to-seller")
async def upgrade_to_seller(payload: SellerUpgradeRequest, identity=Depends(require_identity), db: AsyncSession = Depends(get_db)):
    # Create/update a seller snapshot to persist required seller fields
    # Upsert by store_name (primary key) to avoid duplicate key errors
    snap = await db.execute(select(SellerSnapshot).where(SellerSnapshot.store_name == payload.store_name))
    snap = snap.scalars().first()
    if not snap:
        snap = SellerSnapshot(
            store_name=payload.store_name,
            contact_email=payload.contact_email,
            seller_type="general",
            approved_by_name="system",
        )
        db.add(snap)
    else:
        snap.contact_email = payload.contact_email
    # Optional finance mirrors user finance
    if payload.finance:
        fin = await db.execute(select(UserFinance).where(UserFinance.user_id == identity["id"]))
        fin = fin.scalars().first()
        if not fin:
            fin = UserFinance(user_id=identity["id"])
            db.add(fin)
        for attr in ["bank", "credit_card_number", "cvv", "pin", "account_type"]:
            val = getattr(payload.finance, attr, None)
            if val is not None:
                setattr(fin, attr, val)
    # Optional ship-from address: reuse CustomerShipment for now
    if payload.shipping:
        ship = await db.execute(select(CustomerShipment).where(CustomerShipment.customer_id == identity["id"]))
        ship = ship.scalars().first()
        if not ship:
            ship = CustomerShipment(customer_id=identity["id"]) 
            db.add(ship)
        for attr in ["postal_code", "street_line_1", "street_line_2", "city", "state_province", "country"]:
            val = getattr(payload.shipping, attr, None)
            if val is not None:
                setattr(ship, attr, val)
    await db.commit()
    # Return guidance for client to use seller role
    return {"upgraded": True, "seller_id": identity["id"], "set_headers": {"X-Auth-Role": "seller", "X-Auth-Seller-Id": identity["id"]}}
