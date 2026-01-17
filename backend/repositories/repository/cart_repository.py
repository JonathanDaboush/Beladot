
# ------------------------------------------------------------------------------
# cart_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing Cart records from the database.
# Provides async CRUD methods for carts.
# ------------------------------------------------------------------------------

from typing import Optional
from backend.persistance.cart import Cart
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class CartRepository:
    """
    Repository for Cart model.
    Provides async CRUD operations for carts.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with DB session."""
        self.db = db

    async def get_by_id(self, cart_id: int) -> Optional[Cart]:
        """Retrieve a cart by its ID."""
        result = await self.db.execute(
            select(Cart).filter(Cart.cart_id == cart_id)
        )
        return result.scalars().first()

    async def save(self, cart: Cart) -> Cart:
        """Save a new cart to the database."""
        self.db.add(cart)
        await self.db.commit()
        await self.db.refresh(cart)
        return cart

    async def update(self, cart_id: int, **kwargs) -> Optional[Cart]:
        """Update an existing cart by ID with provided fields."""
        cart = await self.get_by_id(cart_id)
        if not cart:
            return None
        for k, v in kwargs.items():
            if hasattr(cart, k):
                setattr(cart, k, v)
        await self.db.commit()
        return cart

    async def delete(self, cart_id: int) -> bool:
        """Delete a cart by its ID."""
        cart = await self.get_by_id(cart_id)
        if cart:
            self.db.delete(cart)
            await self.db.commit()
            return True
        return False
