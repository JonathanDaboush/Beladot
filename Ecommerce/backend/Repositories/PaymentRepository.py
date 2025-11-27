from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Payment import Payment


class PaymentRepository:
    """
    Data access layer for Payment entities.
    
    This repository handles payment record persistence and updates, tracking
    payment lifecycle (pending, completed, refunded) and gateway transactions.
    
    Responsibilities:
        - Update payment status and metadata
        - Track gateway transaction details
        - Support payment lifecycle management
    
    Design Patterns:
        - Repository Pattern: Isolates payment data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = PaymentRepository(db_session)
        await repository.update(payment)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = Payment
    
    async def update(self, payment: Payment):
        """
        Update payment status and gateway response data.
        
        Args:
            payment: Payment object with modifications
            
        Side Effects:
            - Updates payment.updated_at
            - Commits transaction immediately
            
        Common Updates:
            - Status changes (pending → completed)
            - Gateway transaction ID assignment
            - Raw gateway response storage
        """
        await self.db.merge(payment)
        await self.db.commit()
        await self.db.refresh(payment)
