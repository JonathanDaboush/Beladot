from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from Models.Coupon import Coupon


class CouponRepository:
    """
    Data access layer for Coupon entities.
    
    This repository manages coupon/promotion code data access and tracks
    usage statistics for per-user and global usage limits.
    
    Responsibilities:
        - Coupon CRUD operations
        - Track coupon usage by user
        - Support coupon validation queries
    
    Design Patterns:
        - Repository Pattern: Isolates coupon data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = CouponRepository(db_session)
        usage_count = await repository.get_coupon_usage_count(user_id, coupon_id)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = Coupon
    
    async def get_coupon_usage_count(self, user_id: int, coupon_id: int) -> int:
        """
        Get the number of times a user has used a specific coupon.
        Note: This assumes you have a coupon_usages table or track usage in orders.
        Adjust the query based on your actual schema for tracking coupon usage.
        """
        # Placeholder implementation - adjust based on your actual usage tracking
        from Models.Order import Order
        result = await self.db.execute(
            select(func.count(Order.id))
            .where(Order.user_id == user_id)
            # TODO: Add proper coupon tracking join/filter based on your schema
        )
        return result.scalar() or 0
