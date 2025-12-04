from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Return import Return
from Models.Refund import Refund
from Models.AuditLog import AuditLog


class ReturnRepository:
    """
    Data access layer for Return entities (customer returns/RMAs).
    
    This repository manages product return requests and associated refunds,
    tracking the return lifecycle from initiation through completion.
    
    Responsibilities:
        - Return CRUD operations
        - Refund creation for approved returns
        - Audit log for return lifecycle events
    
    Design Patterns:
        - Repository Pattern: Isolates return data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = ReturnRepository(db_session)
        await repository.update(return_obj)
        refund = await repository.create_refund(refund_obj)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = Return
    
    async def update(self, return_obj: Return):
        """
        Update return status and processing details.
        
        Args:
            return_obj: Return object with modifications
            
        Side Effects:
            - Updates return.updated_at
            - Commits transaction immediately
            
        Common Updates:
            - Status changes (requested → approved → completed)
            - Inspection notes
            - Resolution details
        """
        await self.db.merge(return_obj)
        await self.db.commit()
        await self.db.refresh(return_obj)
    
    async def get_returned_item_ids(self, order_ids: list) -> set:
        """
        Get set of order_item_ids that have been returned for given orders.
        """
        result = await self.db.execute(
            select(self.model.return_items).where(self.model.order_id.in_(order_ids))
        )
        returned = set()
        for row in result:
            items = row[0] or []
            for entry in items:
                returned.add(entry.get('order_item_id'))
        return returned
    
