from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.OrderItem import OrderItem
from typing import List


class OrderItemRepository:
    """
    Data access layer for OrderItem entities (order line items).
    
    This repository manages order line item persistence, providing
    queries for individual items and order-level item lists.
    
    Responsibilities:
        - OrderItem CRUD operations
        - Query items by order
        - Support order detail displays
    
    Design Patterns:
        - Repository Pattern: Isolates order item data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = OrderItemRepository(db_session)
        items = await repository.get_by_order(order_id)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = OrderItem
    
    async def get_by_id(self, item_id: int) -> OrderItem:
        """
        Retrieve an order item by ID.
        
        Args:
            item_id: The unique ID of the order item
            
        Returns:
            OrderItem: The item object if found, None otherwise
        """
        result = await self.db.execute(select(OrderItem).where(OrderItem.id == item_id))
        return result.scalar_one_or_none()
    
    async def get_by_order(self, order_id: int) -> List[OrderItem]:
        """
        Get all items for a specific order.
        
        Args:
            order_id: The order ID to query
            
        Returns:
            List[OrderItem]: All line items for the order
        """
        result = await self.db.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        return result.scalars().all()
    
    async def create(self, order_item: OrderItem) -> OrderItem:
        """
        Create an order line item.
        
        Args:
            order_item: OrderItem object to persist
            
        Returns:
            OrderItem: Created item with database-generated ID
        """
        self.db.add(order_item)
        await self.db.commit()
        await self.db.refresh(order_item)
        return order_item
    
    async def update(self, order_item: OrderItem):
        """
        Update order item (rarely used - items are snapshots).
        
        Args:
            order_item: OrderItem object with modifications
            
        Note:
            Order items are typically immutable after creation
        """
        await self.db.merge(order_item)
        await self.db.commit()
        await self.db.refresh(order_item)
    
    async def get_by_orders_and_seller(self, order_ids: list, seller_id: int):
        """
        Get all order items for a list of orders and a seller.
        """
        from Models.Product import Product
        result = await self.db.execute(
            select(self.model).join(self.model.product).where(
                self.model.order_id.in_(order_ids),
                Product.seller_id == seller_id
            )
        )
        return result.scalars().all()
