from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.CartItem import CartItem
from typing import List


class CartItemRepository:
    """
    Data access layer for CartItem entities.
    
    This repository manages cart item persistence, supporting individual
    item operations and cart-level item queries.
    
    Responsibilities:
        - CartItem CRUD operations
        - Query items by cart
        - Support cart management
    
    Design Patterns:
        - Repository Pattern: Isolates cart item data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = CartItemRepository(db_session)
        items = await repository.get_by_cart(cart_id)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = CartItem
    
    async def get_by_id(self, item_id: int) -> CartItem:
        """
        Retrieve a cart item by ID.
        
        Args:
            item_id: The unique ID of the cart item
            
        Returns:
            CartItem: The item object if found, None otherwise
        """
        result = await self.db.execute(select(CartItem).where(CartItem.id == item_id))
        return result.scalar_one_or_none()
    
    async def get_by_cart(self, cart_id: int) -> List[CartItem]:
        """
        Get all items in a specific cart.
        
        Args:
            cart_id: The cart ID to query
            
        Returns:
            List[CartItem]: All items in the cart
        """
        result = await self.db.execute(
            select(CartItem).where(CartItem.cart_id == cart_id)
        )
        return result.scalars().all()
    
    async def create(self, cart_item: CartItem) -> CartItem:
        """
        Add an item to a cart.
        
        Args:
            cart_item: CartItem object to persist
            
        Returns:
            CartItem: Created item with database-generated ID
        """
        self.db.add(cart_item)
        await self.db.commit()
        await self.db.refresh(cart_item)
        return cart_item
    
    async def update(self, cart_item: CartItem):
        """
        Update cart item quantity or price.
        
        Args:
            cart_item: CartItem object with modifications
        """
        await self.db.merge(cart_item)
        await self.db.commit()
        await self.db.refresh(cart_item)
    
    async def delete(self, item_id: int):
        """
        Remove an item from a cart.
        
        Args:
            item_id: ID of the cart item to delete
            
        Side Effects:
            - Permanently deletes cart item
        """
        item = await self.get_by_id(item_id)
        if item:
            await self.db.delete(item)
            await self.db.commit()
