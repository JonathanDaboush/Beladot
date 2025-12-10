"""
Transfer Routes
Handles inventory transfer operations:
- Import/export inventory transfers
- Product management (view/update products related to transfers)
- Shipment tracking (note what happened to shipments)
- Inventory movement history
- Order status updates (delivery operations)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from schemas import MessageResponse
from Services.InventoryService import InventoryService
from Services.ProductService import ProductService
from Services.ShippingCarrierService import ShippingCarrierService
from Services.OrderService import OrderService
from Utilities.auth import get_current_transfer_user
from Utilities.rate_limiting import rate_limiter_moderate
from Utilities.email_service import send_shipping_update

router = APIRouter(prefix="/api/transfer", tags=["Transfer"])


# ============================================================================
# INVENTORY TRANSFERS
# ============================================================================

@router.post("/import", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def import_inventory(
    product_id: int,
    quantity: int,
    notes: Optional[str] = None,
    current_user=Depends(get_current_transfer_user),
    db: AsyncSession = Depends(get_db)
):
    """Import inventory transfer"""
    inventory_service = InventoryService(db)
    
    await inventory_service.import_inventory(
        product_id=product_id,
        quantity=quantity,
        transferred_by=current_user.id,
        notes=notes
    )
    
    return {"message": f"Import transfer of {quantity} units initiated for product {product_id}"}


@router.post("/export", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def export_inventory(
    product_id: int,
    quantity: int,
    notes: Optional[str] = None,
    current_user=Depends(get_current_transfer_user),
    db: AsyncSession = Depends(get_db)
):
    """Export inventory transfer"""
    inventory_service = InventoryService(db)
    
    await inventory_service.export_inventory(
        product_id=product_id,
        quantity=quantity,
        transferred_by=current_user.id,
        notes=notes
    )
    
    return {"message": f"Export transfer of {quantity} units initiated for product {product_id}"}


@router.get("/movements", dependencies=[Depends(rate_limiter_moderate)])
async def get_inventory_movements(
    current_user=Depends(get_current_transfer_user),
    db: AsyncSession = Depends(get_db)
):
    """Get inventory movement history"""
    inventory_service = InventoryService(db)
    
    movements = await inventory_service.get_recent_movements()
    
    return {"movements": movements}


# ============================================================================
# PRODUCT MANAGEMENT (TRANSFER VIEW)
# ============================================================================

@router.get("/products", dependencies=[Depends(rate_limiter_moderate)])
async def get_products_for_transfer(
    current_user=Depends(get_current_transfer_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all products (transfer user view for inventory management)"""
    product_service = ProductService(db)
    
    products = await product_service.get_all_products()
    
    return {"products": products}


@router.get("/products/{product_id}", dependencies=[Depends(rate_limiter_moderate)])
async def get_product_details(
    product_id: int,
    current_user=Depends(get_current_transfer_user),
    db: AsyncSession = Depends(get_db)
):
    """Get product details for transfer operations"""
    product_service = ProductService(db)
    
    product = await product_service.get_product(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return {"product": product}


@router.put("/products/{product_id}/stock", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_product_stock(
    product_id: int,
    new_stock: int,
    reason: str,
    current_user=Depends(get_current_transfer_user),
    db: AsyncSession = Depends(get_db)
):
    """Update product stock levels (transfer/delivery user access)"""
    from Services.SimpleInventoryService import SimpleInventoryService
    from Repositories.ProductRepository import ProductRepository
    
    product_repo = ProductRepository(db)
    inventory_service = SimpleInventoryService(product_repo)
    
    # Update stock to specific level
    await inventory_service.update_stock_level(product_id, new_stock)
    
    # Record the change in inventory transactions
    from Models.InventoryTransaction import InventoryTransaction
    transaction = InventoryTransaction(
        product_id=product_id,
        quantity_change=new_stock,  # This will be the new level set
        transaction_type='adjustment',
        reason=reason or f"Stock adjusted by transfer user {current_user.id}"
    )
    db.add(transaction)
    await db.commit()
    
    return {"message": f"Product {product_id} stock updated to {new_stock}"}


# ============================================================================
# SHIPMENT TRACKING & NOTES
# ============================================================================

@router.get("/shipments", dependencies=[Depends(rate_limiter_moderate)])
async def get_shipments(
    current_user=Depends(get_current_transfer_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all shipments (transfer user view)"""
    shipping_service = ShippingCarrierService(db)
    
    shipments = await shipping_service.get_all_shipments()
    
    return {"shipments": shipments}


@router.get("/shipments/{shipment_id}", dependencies=[Depends(rate_limiter_moderate)])
async def get_shipment_details(
    shipment_id: int,
    current_user=Depends(get_current_transfer_user),
    db: AsyncSession = Depends(get_db)
):
    """Get shipment details"""
    shipping_service = ShippingCarrierService(db)
    
    shipment = await shipping_service.get_shipment(shipment_id)
    
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )
    
    return {"shipment": shipment}


@router.post("/shipments/{shipment_id}/notes", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def add_shipment_note(
    shipment_id: int,
    note: str,
    current_user=Depends(get_current_transfer_user),
    db: AsyncSession = Depends(get_db)
):
    """Add note to shipment about what happened (damaged, delayed, etc.)"""
    shipping_service = ShippingCarrierService(db)
    
    await shipping_service.add_shipment_note(
        shipment_id=shipment_id,
        note=note,
        added_by=current_user.id
    )
    
    return {"message": "Shipment note added successfully"}


@router.put("/shipments/{shipment_id}/status", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_shipment_status(
    shipment_id: int,
    status: str,
    notes: Optional[str] = None,
    current_user=Depends(get_current_transfer_user),
    db: AsyncSession = Depends(get_db)
):
    """Update shipment status and add notes about what happened"""
    from sqlalchemy import select
    from Models.Shipment import Shipment
    from Models.Order import Order
    from Models.User import User
    
    shipping_service = ShippingCarrierService(db)
    
    await shipping_service.update_shipment_status(
        shipment_id=shipment_id,
        new_status=status,
        notes=notes,
        updated_by=current_user.id
    )
    
    # Send shipping update email to customer
    if status in ['shipped', 'in_transit', 'out_for_delivery', 'delivered']:
        try:
            # Get shipment, order, and user info
            result = await db.execute(
                select(Shipment).where(Shipment.id == shipment_id)
            )
            shipment = result.scalar_one_or_none()
            
            if shipment:
                order_result = await db.execute(
                    select(Order).where(Order.id == shipment.order_id)
                )
                order = order_result.scalar_one_or_none()
                
                if order:
                    user_result = await db.execute(
                        select(User).where(User.id == order.user_id)
                    )
                    user = user_result.scalar_one_or_none()
                    
                    if user:
                        await send_shipping_update(
                            to_email=user.email,
                            shipment_data={
                                "order_id": order.id,
                                "tracking_number": shipment.tracking_number or "N/A",
                                "carrier": shipment.carrier or "Standard",
                                "status": status,
                                "customer_name": f"{user.first_name} {user.last_name}",
                                "estimated_delivery": shipment.estimated_delivery.isoformat() if hasattr(shipment, 'estimated_delivery') and shipment.estimated_delivery else "TBD"
                            }
                        )
        except Exception as e:
            print(f"Failed to send shipping update email: {e}")
    
    return {"message": f"Shipment {shipment_id} status updated to {status}"}


# ============================================================================
# ORDER STATUS MANAGEMENT (DELIVERY OPERATIONS)
# ============================================================================

@router.put("/orders/{order_id}/status", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_order_status(
    order_id: int,
    new_status: str,
    notes: Optional[str] = None,
    current_user=Depends(get_current_transfer_user),
    db: AsyncSession = Depends(get_db)
):
    """Update order status for delivery operations (transfer permission)"""
    order_service = OrderService(db)
    
    try:
        await order_service.update_order_status(
            order_id=order_id,
            new_status=new_status,
            actor_role='transfer',
            notes=notes
        )
        return {"message": "Order status updated successfully"}
    except (PermissionError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/shipments/{shipment_id}/receive", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def receive_shipment(
    shipment_id: int,
    current_user=Depends(get_current_transfer_user),
    db: AsyncSession = Depends(get_db)
):
    """Receive shipment and update inventory"""
    from sqlalchemy import select
    from Models.Shipment import Shipment
    from Models.ShipmentItem import ShipmentItem
    from Services.SimpleInventoryService import SimpleInventoryService
    from Repositories.ProductRepository import ProductRepository
    
    # Get shipment
    result = await db.execute(select(Shipment).where(Shipment.id == shipment_id))
    shipment = result.scalar_one_or_none()
    
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )
    
    # Get shipment items
    items_result = await db.execute(select(ShipmentItem).where(ShipmentItem.shipment_id == shipment_id))
    items = items_result.scalars().all()
    
    # Update inventory for each item
    product_repo = ProductRepository(db)
    inventory_service = SimpleInventoryService(product_repo)
    
    for item in items:
        await inventory_service.restock_product(item.product_id, item.quantity)
    
    # Update shipment status
    shipment.status = 'received'
    shipment.notes = f"{shipment.notes or ''}\n[{current_user.id}] Shipment received and inventory updated"
    
    await db.commit()
    
    return {"message": f"Shipment {shipment_id} received and inventory updated"}

