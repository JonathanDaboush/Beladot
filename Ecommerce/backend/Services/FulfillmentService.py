from typing import Any, Optional, Dict
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from Models.Shipment import Shipment, ShipmentStatus
from Models.Order import Order
from Models.AuditLog import AuditLog


class FulfillmentService:
    """
    Shipping and Fulfillment Service
    Handles shipment creation, label generation, carrier integrations, and shipment tracking.
    
    Supports:
    - Auto-shipment creation on order confirmation
    - Multi-carrier support (Purolator, FedEx, DHL, UPS, Canada Post)
    - Shipment tracking with real-time updates
    - Label storage in blob system
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize FulfillmentService.
        
        Args:
            db: Async SQLAlchemy session
        """
        self.db = db
    
    async def create_shipment(
        self,
        order_id: int,
        carrier: str = "AUTO",
        actor_id: int = None
    ) -> Shipment:
        """
        Create a shipment for an order.
        
        Args:
            order_id: Order to ship
            carrier: Carrier name or "AUTO" for automatic selection
            actor_id: User creating shipment (for audit)
            
        Returns:
            Shipment: Created shipment record
            
        Raises:
            ValueError: If order not found or already shipped
        """
        # Get order
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        # Check if shipment already exists
        result = await self.db.execute(
            select(Shipment).where(Shipment.order_id == order_id)
        )
        existing_shipment = result.scalar_one_or_none()
        
        if existing_shipment:
            # Audit log
            audit_entry = AuditLog(
                actor_id=actor_id,
                actor_type="USER",
                action="create_shipment_duplicate",
                target_type="order",
                target_id=str(order_id),
                item_metadata={"message": "Shipment already exists"},
                created_at=datetime.now(timezone.utc)
            )
            self.db.add(audit_entry)
            await self.db.commit()
            
            return existing_shipment
        
        # Auto-select carrier based on destination
        if carrier == "AUTO":
            carrier = self._select_carrier(order)
        
        # Generate tracking number (placeholder - would integrate with carrier API)
        tracking_number = f"{carrier.upper()}{order_id:010d}{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create shipment
        shipment = Shipment(
            order_id=order_id,
            tracking_number=tracking_number,
            carrier=carrier,
            status=ShipmentStatus.PENDING,
            shipped_at=None,
            estimated_delivery=None,
            delivered_at=None,
            cost_cents=0,  # Would be set by carrier API
            label_blob_id=None,  # Would be set after label generation
            idempotency_key=f"shipment_{order_id}_{datetime.now().timestamp()}",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.db.add(shipment)
        
        # Audit log
        audit_entry = AuditLog(
            actor_id=actor_id,
            actor_type="USER",
            action="create_shipment",
            target_type="order",
            target_id=str(order_id),
            item_metadata={
                "carrier": carrier,
                "tracking_number": tracking_number,
                "status": shipment.status.value
            },
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(audit_entry)
        
        await self.db.commit()
        await self.db.refresh(shipment)
        
        return shipment
    
    async def track_shipment(
        self,
        shipment_id: int,
        actor_id: int = None
    ) -> Dict[str, Any]:
        """
        Get tracking information for a shipment.
        
        Args:
            shipment_id: Shipment to track
            actor_id: User requesting tracking (for audit)
            
        Returns:
            dict: Tracking information with status, events, estimated delivery
            
        Raises:
            ValueError: If shipment not found
        """
        # Get shipment
        result = await self.db.execute(
            select(Shipment).where(Shipment.id == shipment_id)
        )
        shipment = result.scalar_one_or_none()
        
        if not shipment:
            raise ValueError(f"Shipment {shipment_id} not found")
        
        # Audit log
        audit_entry = AuditLog(
            actor_id=actor_id,
            actor_type="USER",
            action="track_shipment",
            target_type="shipment",
            target_id=str(shipment_id),
            item_metadata={
                "tracking_number": shipment.tracking_number,
                "carrier": shipment.carrier
            },
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(audit_entry)
        await self.db.commit()
        
        # Build tracking response (placeholder - would query carrier API)
        tracking_data = {
            "status": shipment.status.value,
            "tracking_number": shipment.tracking_number,
            "carrier": shipment.carrier,
            "shipped_at": shipment.shipped_at.isoformat() if shipment.shipped_at else None,
            "estimated_delivery": shipment.estimated_delivery.isoformat() if shipment.estimated_delivery else None,
            "delivered_at": shipment.delivered_at.isoformat() if shipment.delivered_at else None,
            "last_updated": shipment.updated_at.isoformat() if shipment.updated_at else None,
            "events": self._get_tracking_events(shipment)
        }
        
        return tracking_data
    
    def _select_carrier(self, order: Order) -> str:
        """
        Auto-select carrier based on order destination and preferences.
        
        Args:
            order: Order to ship
            
        Returns:
            str: Selected carrier name
        """
        # Placeholder logic - would consider:
        # - Destination country/region
        # - Package weight/dimensions
        # - Delivery speed requirements
        # - Carrier rates
        # - Customer preferences
        
        return "purolator"  # Default Canadian carrier
    
    def _get_tracking_events(self, shipment: Shipment) -> list:
        """
        Generate tracking event timeline.
        
        Args:
            shipment: Shipment to get events for
            
        Returns:
            list: Timeline of tracking events
        """
        events = []
        
        if shipment.status == ShipmentStatus.PENDING:
            events.append({
                "timestamp": shipment.created_at.isoformat(),
                "status": "Shipment created",
                "location": "Warehouse"
            })
        elif shipment.status == ShipmentStatus.SHIPPED:
            events.extend([
                {
                    "timestamp": shipment.created_at.isoformat(),
                    "status": "Shipment created",
                    "location": "Warehouse"
                },
                {
                    "timestamp": shipment.shipped_at.isoformat() if shipment.shipped_at else shipment.created_at.isoformat(),
                    "status": "Picked up by carrier",
                    "location": "Warehouse"
                }
            ])
        elif shipment.status == ShipmentStatus.DELIVERED:
            events.extend([
                {
                    "timestamp": shipment.created_at.isoformat(),
                    "status": "Shipment created",
                    "location": "Warehouse"
                },
                {
                    "timestamp": shipment.shipped_at.isoformat() if shipment.shipped_at else shipment.created_at.isoformat(),
                    "status": "Picked up by carrier",
                    "location": "Warehouse"
                },
                {
                    "timestamp": shipment.delivered_at.isoformat() if shipment.delivered_at else shipment.updated_at.isoformat(),
                    "status": "Delivered",
                    "location": "Customer address"
                }
            ])
        
        return events
    
    # handle_tracking_update removed - webhook handling done elsewhere

