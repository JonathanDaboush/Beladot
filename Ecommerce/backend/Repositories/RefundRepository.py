from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Refund import Refund
from typing import List


class RefundRepository:
    """
    Data access layer for Refund entities.
    
    This repository handles database operations for refunds, supporting queries
    by ID and by order, enabling refund tracking and management.
    
    Responsibilities:
        - CRUD operations for Refund entities
        - Query refunds by order (all refunds for an order)
        - Support refund lifecycle tracking
    
    Design Patterns:
        - Repository Pattern: Isolates refund data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = RefundRepository(db_session)
        refunds = await repository.get_by_order(order_id)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = Refund
    
    async def get_by_id(self, refund_id: int) -> Refund:
        """
        Retrieve a refund by its unique identifier.
        
        Args:
            refund_id: The unique ID of the refund
            
        Returns:
            Refund: The refund object if found, None otherwise
        """
        result = await self.db.execute(select(Refund).where(Refund.id == refund_id))
        return result.scalar_one_or_none()
    
    async def get_by_order(self, order_id: int) -> List[Refund]:
        """
        Retrieve all refunds associated with a specific order.
        
        Args:
            order_id: The order ID to find refunds for
            
        Returns:
            List[Refund]: List of refund objects for the order
            
        Use Case:
            Used to display refund history and calculate total refunded amount
        """
        result = await self.db.execute(
            select(Refund).where(Refund.order_id == order_id)
        )
        return result.scalars().all()
    
    async def create(self, refund: Refund) -> Refund:
        """
        Create a new refund record in the database.
        
        Args:
            refund: Refund object to persist
            
        Returns:
            Refund: Created refund with database-generated ID
            
        Side Effects:
            - Commits transaction immediately
            - Sets timestamps via database defaults
        """
        self.db.add(refund)
        await self.db.commit()
        await self.db.refresh(refund)
        return refund
    
    async def update(self, refund: Refund):
        """
        Update an existing refund record.
        
        Args:
            refund: Refund object with modifications
            
        Side Effects:
            - Updates timestamps
            - Commits transaction immediately
        """
        await self.db.merge(refund)
        await self.db.commit()
        await self.db.refresh(refund)
