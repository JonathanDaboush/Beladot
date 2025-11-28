from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Order import Order
from Models.Payment import Payment
from Models.Refund import Refund
from Models.AuditLog import AuditLog


class OrderRepository:
        async def get_orders_by_user_id(self, user_id: int):
            """
            Fetch all orders for a given user ID.
            Args:
                user_id (int): The ID of the user whose orders to fetch.
            Returns:
                List[Order]: List of Order objects for the user.
            """
            result = await self.db.execute(select(self.model).where(self.model.user_id == user_id))
            return result.scalars().all()
    """
    Data access layer for Order entities and related operations.
    
    This repository handles orders and their associated entities (payments, refunds,
    audit logs). It provides a unified interface for order-related database operations.
    
    Responsibilities:
        - Order CRUD operations
        - Payment creation and tracking
        - Refund processing
        - Audit log generation for order actions
    
    Design Patterns:
        - Repository Pattern: Isolates order data access
        - Aggregate Root: Order is the aggregate root for order items, payments, refunds
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = OrderRepository(db_session)
        await repository.update(order)
        payment = await repository.create_payment(payment_obj)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = Order
    
    async def update(self, order: Order):
        """
        Update an existing order in the database.
        
        Args:
            order: Order object with modifications
            
        Side Effects:
            - Updates order.updated_at via database trigger
            - Commits transaction immediately
            
        Design:
            Uses merge() to handle detached order objects from service layer
        """
        await self.db.merge(order)
        await self.db.commit()
        await self.db.refresh(order)
    
