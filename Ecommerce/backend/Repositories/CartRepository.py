from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from Models.Cart import Cart
from Models.CartItem import CartItem


class CartRepository:
    """
    Data access layer for Cart and CartItem entities.
    
    This repository manages shopping cart persistence, including cart updates
    and cart item CRUD operations. Carts are aggregate roots that own cart items.
    
    Responsibilities:
        - Cart updates (timestamps, metadata)
        - CartItem CRUD operations
        - Cascade delete handling for cart items
    
    Design Patterns:
        - Aggregate Root: Cart owns CartItems
        - Repository Pattern: Unified cart data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = CartRepository(db_session)
        await repository.update(cart)
        item = await repository.create_item(cart_item)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = Cart
    
    async def update(self, cart: Cart):
        """
        Update cart metadata (timestamps, user association).
        
        Args:
            cart: Cart object with modifications
            
        Side Effects:
            - Updates cart.updated_at
            - Commits transaction immediately
        """
        await self.db.merge(cart)
        await self.db.commit()
        await self.db.refresh(cart)
    
    async def create_item(self, cart_item: CartItem) -> CartItem:
        """
        Add a new item to a cart.
        
        Args:
            cart_item: CartItem object to create
            
        Returns:
            CartItem: Created cart item with database-generated ID
            
        Side Effects:
            - Sets added_at timestamp
            - Commits transaction immediately
        """
        self.db.add(cart_item)
        await self.db.commit()
        await self.db.refresh(cart_item)
        return cart_item
    
    async def update_item(self, cart_item: CartItem):
        """
        Update an existing cart item (quantity, price).
        
        Args:
            cart_item: CartItem object with modifications
            
        Side Effects:
            - Commits transaction immediately
        """
        await self.db.merge(cart_item)
        await self.db.commit()
        await self.db.refresh(cart_item)
    
    async def delete_item(self, cart_item_id: int):
        """
        Remove an item from a cart.
        
        Args:
            cart_item_id: ID of the cart item to delete
            
        Side Effects:
            - Permanently deletes cart item
            - Commits transaction immediately
        """
        await self.db.execute(delete(CartItem).where(CartItem.id == cart_item_id))
        await self.db.commit()
