from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.ShipmentItem import ShipmentItem
from typing import List


class ShipmentItemRepository:
    """
    Data access layer for ShipmentItem entities (line items in shipments).
    
    This repository manages shipment line items, tracking which order items
    are included in each shipment (for partial or split shipments).
    
    Responsibilities:
        - ShipmentItem CRUD operations
        - Query items by shipment
        - Support split shipment management
    
    Design Patterns:
        - Repository Pattern: Isolates shipment item data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = ShipmentItemRepository(db_session)
        items = await repository.get_by_shipment(shipment_id)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = ShipmentItem
    
    async def get_by_id(self, item_id: int) -> ShipmentItem:
        """
        Retrieve a shipment item by ID.
        
        Args:
            item_id: The unique ID of the shipment item
            
        Returns:
            ShipmentItem: The item if found, None otherwise
        """
        result = await self.db.execute(select(ShipmentItem).where(ShipmentItem.id == item_id))
        return result.scalar_one_or_none()
    
    async def get_by_shipment(self, shipment_id: int) -> List[ShipmentItem]:
        """
        Retrieve all items in a shipment.
        
        Args:
            shipment_id: The shipment ID
            
        Returns:
            List[ShipmentItem]: All items in the shipment
        """
        result = await self.db.execute(
            select(ShipmentItem).where(ShipmentItem.shipment_id == shipment_id)
        )
        return result.scalars().all()
    
    async def create(self, shipment_item: ShipmentItem) -> ShipmentItem:
        """
        Create a new shipment item record.
        
        Args:
            shipment_item: ShipmentItem object to persist
            
        Returns:
            ShipmentItem: Created item with database-generated ID
            
        Side Effects:
            Commits transaction immediately
        """
        self.db.add(shipment_item)
        await self.db.commit()
        await self.db.refresh(shipment_item)
        return shipment_item
    
    async def update(self, shipment_item: ShipmentItem):
        """
        Update a shipment item.
        
        Args:
            shipment_item: ShipmentItem object with modifications
            
        Side Effects:
            Commits transaction immediately
        """
        await self.db.merge(shipment_item)
        await self.db.commit()
        await self.db.refresh(shipment_item)
