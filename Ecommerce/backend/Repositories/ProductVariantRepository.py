from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.ProductVariant import ProductVariant
from Models.InventoryTransaction import InventoryTransaction
from typing import List


class ProductVariantRepository:
    """
    Data access layer for ProductVariant entities and inventory tracking.
    
    This repository manages product variant persistence and inventory
    transactions (reservations, sales, restocks), providing atomic
    inventory operations.
    
    Responsibilities:
        - ProductVariant CRUD operations
        - Inventory transaction creation
        - Query active inventory reservations
        - Support stock level calculations
    
    Design Patterns:
        - Repository Pattern: Isolates variant data access
        - Transaction Management: Atomic inventory operations
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = ProductVariantRepository(db_session)
        variant = await repository.get_by_id(variant_id)
        reservations = await repository.get_active_reservations(variant_id)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = ProductVariant
    
    async def get_by_id(self, variant_id: int) -> ProductVariant:
        """
        Retrieve a product variant by ID.
        
        Args:
            variant_id: The unique ID of the variant
            
        Returns:
            ProductVariant: The variant object if found, None otherwise
        """
        result = await self.db.execute(select(ProductVariant).where(ProductVariant.id == variant_id))
        return result.scalar_one_or_none()
    
    async def update(self, variant: ProductVariant):
        """
        Update variant details (price, stock, attributes).
        
        Args:
            variant: ProductVariant object with modifications
            
        Side Effects:
            - Updates variant.updated_at
            - Commits transaction immediately
        """
        await self.db.merge(variant)
        await self.db.commit()
        await self.db.refresh(variant)
    
    
    async def get_active_reservations(self, variant_id: int) -> List[InventoryTransaction]:
        """
        Get all active inventory reservations for a variant.
        
        Args:
            variant_id: The variant ID to query
            
        Returns:
            List[InventoryTransaction]: Active reservation transactions
            
        Use Case:
            Calculate available stock (physical - reserved = available)
        """
        result = await self.db.execute(
            select(InventoryTransaction)
            .where(InventoryTransaction.variant_id == variant_id)
            .where(InventoryTransaction.transaction_type == 'reservation')
        )
        return result.scalars().all()
