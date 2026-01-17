
# ------------------------------------------------------------------------------
# cart_item_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing CartItem records from the database.
# Provides async CRUD methods for cart items.
# ------------------------------------------------------------------------------

from typing import List, Optional
from backend.persistance.cart_item import CartItem
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class CartItemRepository:
    """
    Repository for CartItem model.
    Provides async CRUD operations for cart items.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with the given database session."""
        self.db = db

    async def get_by_cart_id(self, cart_id: int) -> List[CartItem]:
        """Retrieve all cart items for a given cart ID."""
        result = await self.db.execute(
            select(CartItem).filter(CartItem.cart_id == cart_id)
        )
        return result.scalars().all()

    async def get_by_id(self, cart_item_id: int) -> Optional[CartItem]:
        """Retrieve a cart item by its ID."""
        result = await self.db.execute(
            select(CartItem).filter(CartItem.cart_item_id == cart_item_id)
        )
        return result.scalars().first()

    async def save(self, cart_item: CartItem) -> CartItem:
        """Save a new cart item to the database."""
        self.db.add(cart_item)
        await self.db.commit()
        await self.db.refresh(cart_item)
        return cart_item

    async def update(self, cart_item_id: int, **kwargs) -> Optional[CartItem]:
        """Update an existing cart item by ID with provided fields."""
        cart_item = await self.get_by_id(cart_item_id)
        if not cart_item:
            return None
        for k, v in kwargs.items():
            if hasattr(cart_item, k):
                setattr(cart_item, k, v)
        await self.db.commit()
        return cart_item

    async def delete(self, cart_item_id: int) -> bool:
        """Delete a cart item by its ID."""
        cart_item = await self.get_by_id(cart_item_id)
        if cart_item:
            self.db.delete(cart_item)
            await self.db.commit()
            return True
        return False
