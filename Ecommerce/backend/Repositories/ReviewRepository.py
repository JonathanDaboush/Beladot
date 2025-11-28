from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Review import Review
from Models.AuditLog import AuditLog


class ReviewRepository:
    """
    Data access layer for Review entities (product reviews and ratings).
    
    This repository manages product review persistence with audit logging
    for moderation and quality control.
    
    Responsibilities:
        - Review CRUD operations
        - Track review status (published, hidden, flagged)
        - Audit log for moderation actions
    
    Design Patterns:
        - Repository Pattern: Isolates review data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = ReviewRepository(db_session)
        await repository.update(review)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = Review
    
    async def update(self, review: Review):
        """
        Update review content or status.
        
        Args:
            review: Review object with modifications
            
        Side Effects:
            - Updates review.updated_at
            - Commits transaction immediately
            
        Common Updates:
            - Moderation status changes
            - Rating/comment edits
            - Helpfulness vote counts
        """
        await self.db.merge(review)
        await self.db.commit()
        await self.db.refresh(review)
    
