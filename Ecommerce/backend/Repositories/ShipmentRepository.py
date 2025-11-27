from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Shipment import Shipment


class ShipmentRepository:
    """
    Data access layer for Shipment entities.
    
    This repository manages shipment records, tracking packages from label
    generation through delivery, including carrier tracking updates.
    
    Responsibilities:
        - Shipment CRUD operations
        - Track shipping status updates
        - Store carrier tracking information
        - Link shipments to shipping labels (blobs)
    
    Design Patterns:
        - Repository Pattern: Isolates shipment data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = ShipmentRepository(db_session)
        await repository.update(shipment)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = Shipment
    
    async def update(self, shipment: Shipment):
        """
        Update shipment tracking and status information.
        
        Args:
            shipment: Shipment object with modifications
            
        Side Effects:
            - Updates shipment.updated_at
            - Commits transaction immediately
            
        Common Updates:
            - Tracking number assignment
            - Status changes (pending → shipped → delivered)
            - Carrier updates from webhook callbacks
        """
        await self.db.merge(shipment)
        await self.db.commit()
        await self.db.refresh(shipment)
