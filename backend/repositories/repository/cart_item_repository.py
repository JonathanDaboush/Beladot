
# ------------------------------------------------------------------------------
# cart_item_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing CartItem records from the database.
# Provides async CRUD methods for cart items.
# ------------------------------------------------------------------------------

from backend.model.cart_item import CartItem

class CartItemRepository:
    """
    Repository for CartItem model.
    Provides async CRUD operations for cart items.
    """
    def __init__(self, db):
        """Initialize repository with DB session."""
        self.db = db

    def get_by_cart_id(self, cart_id):
        """Retrieve all cart items for a given cart ID."""
        return self.db.query(CartItem).filter(CartItem.cart_id == cart_id).all()

    async def get_by_id(self, cart_item_id):
        """Retrieve a cart item by its ID."""
        return await self.db.query(CartItem).filter(CartItem.cart_item_id == cart_item_id).first()

    async def save(self, cart_item):
        """Save a new cart item to the database."""
        self.db.add(cart_item)
        await self.db.commit()
        await self.db.refresh(cart_item)
        return cart_item

    async def update(self, cart_item_id, **kwargs):
        """Update an existing cart item by ID with provided fields."""
        cart_item = await self.get_by_id(cart_item_id)
        if not cart_item:
            return None
        for k, v in kwargs.items():
            if hasattr(cart_item, k):
                setattr(cart_item, k, v)
        await self.db.commit()
        return cart_item

    async def delete(self, cart_item_id):
        """Delete a cart item by its ID."""
        cart_item = await self.get_by_id(cart_item_id)
        if cart_item:
            self.db.delete(cart_item)
            await self.db.commit()
            return True
        return False
