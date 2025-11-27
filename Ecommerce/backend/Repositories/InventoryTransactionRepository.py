from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.InventoryTransaction import InventoryTransaction
from typing import List


class InventoryTransactionRepository:
    """
    Data access layer for InventoryTransaction entities.
    
    This repository manages inventory movement tracking with complete
    audit trails for stock changes (sales, reservations, restocks).
    
    Responsibilities:
        - Create inventory transactions (append-only)
        - Query transaction history by variant
        - Filter by transaction type
        - Support stock level calculations
    
    Design Patterns:
        - Append-Only: Transactions never updated/deleted
        - Repository Pattern: Isolates inventory data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = InventoryTransactionRepository(db_session)
        transaction = await repository.create(transaction_obj)
        history = await repository.get_by_variant(variant_id)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = InventoryTransaction
    
    async def create(self, transaction: InventoryTransaction) -> InventoryTransaction:
        """
        Record an inventory transaction (immutable).
        
        Args:
            transaction: InventoryTransaction object to persist
            
        Returns:
            InventoryTransaction: Created transaction with ID
            
        Side Effects:
            - Creates permanent inventory record
            - Cannot be updated or deleted (audit trail)
        """
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction
    
    async def get_by_variant(self, variant_id: int, limit: int = 100) -> List[InventoryTransaction]:
        """
        Get transaction history for a variant.
        
        Args:
            variant_id: The variant ID to query
            limit: Maximum transactions to return (default 100)
            
        Returns:
            List[InventoryTransaction]: Transactions in reverse chronological order
            
        Use Case:
            Display inventory movement history
        """
        result = await self.db.execute(
            select(InventoryTransaction)
            .where(InventoryTransaction.variant_id == variant_id)
            .order_by(InventoryTransaction.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_type(self, variant_id: int, transaction_type: str) -> List[InventoryTransaction]:
        """
        Get transactions of a specific type for a variant.
        
        Args:
            variant_id: The variant ID to query
            transaction_type: Type filter ('reservation', 'sale', 'restock', 'adjustment')
            
        Returns:
            List[InventoryTransaction]: Filtered transactions
            
        Use Case:
            Calculate reserved inventory or total sales
        """
        result = await self.db.execute(
            select(InventoryTransaction)
            .where(InventoryTransaction.variant_id == variant_id)
            .where(InventoryTransaction.transaction_type == transaction_type)
        )
        return result.scalars().all()
