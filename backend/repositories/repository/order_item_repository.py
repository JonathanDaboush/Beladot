
# ------------------------------------------------------------------------------
# order_item_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing OrderItem records from the database.
# Provides async CRUD methods for order items.
# ------------------------------------------------------------------------------

from backend.persistance.order_item import OrderItem
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class OrderItemRepository:
    """
    Repository for OrderItem model.
    Provides async CRUD operations for order items.
    """

    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def get_by_order_id(self, order_id):
        """
        Retrieve all order items for a given order_id.
        """
        result = await self.db.execute(
            select(OrderItem).filter(OrderItem.order_id == order_id)
        )
        return result.scalars().all()

    async def get_by_id(self, order_item_id):
        """Retrieve an order item by its ID."""
        result = await self.db.execute(
            select(OrderItem).filter(OrderItem.order_item_id == order_item_id)
        )
        return result.scalars().first()

    async def save(self, order_item):
        """Save a new order item to the database."""
        self.db.add(order_item)
        await self.db.commit()
        await self.db.refresh(order_item)
        return order_item

    async def update(self, order_item_id, **kwargs):
        """Update an existing order item by ID with provided fields."""
        order_item = await self.get_by_id(order_item_id)
        if not order_item:
            return None
        for k, v in kwargs.items():
            if hasattr(order_item, k):
                setattr(order_item, k, v)
        await self.db.commit()
        return order_item

    async def delete(self, order_item_id):
        """Delete an order item by its ID."""
        order_item = await self.get_by_id(order_item_id)
        if order_item:
            await self.db.delete(order_item)
            await self.db.commit()
            return True
        return False
