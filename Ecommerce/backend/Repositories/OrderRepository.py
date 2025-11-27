from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Order import Order
from Models.Payment import Payment
from Models.Refund import Refund
from Models.AuditLog import AuditLog


class OrderRepository:
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
    
    async def create_payment(self, payment: Payment) -> Payment:
        """
        Create a payment record associated with an order.
        
        Args:
            payment: Payment object to persist
            
        Returns:
            Payment: Created payment with database-generated ID
            
        Side Effects:
            - Sets payment.id
            - Sets created_at and updated_at
            - Commits transaction immediately
            
        Design:
            Payments are owned by orders but created via repository for transaction control
        """
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment
    
    async def create_audit_log(self, log_data: dict) -> AuditLog:
        """
        Create an audit log entry for order-related actions.
        
        Args:
            log_data: Dictionary with audit log fields (actor_id, action, target_type, etc.)
            
        Returns:
            AuditLog: Created audit log entry
            
        Side Effects:
            - Creates immutable audit record
            - Commits transaction immediately
            
        Audit Trail:
            Used for compliance, security, and debugging order operations
        """
        audit_log = AuditLog(**log_data)
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        return audit_log
    
    async def create_refund(self, refund: Refund) -> Refund:
        """
        Create a refund record for an order payment.
        
        Args:
            refund: Refund object to persist
            
        Returns:
            Refund: Created refund with database-generated ID
            
        Side Effects:
            - Sets refund.id
            - Sets timestamps
            - Commits transaction immediately
            
        Design:
            Refunds reference both order and payment for complete traceability
        """
        self.db.add(refund)
        await self.db.commit()
        await self.db.refresh(refund)
        return refund
