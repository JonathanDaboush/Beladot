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
    
    async def get_by_code(self, code: str) -> Coupon:
        result = await self.db.execute(select(self.model).where(self.model.code == code))
        return result.scalar_one_or_none()
    
    async def create(self, coupon) -> Coupon:
        """
        Create a new coupon record in the database.
        Args:
            coupon: Coupon domain object
        Returns:
            Coupon: Created coupon with database-generated ID
        """
        db_coupon = self.model(
            code=coupon.code,
            description=coupon.description,
            discount_type=coupon.discount_type,
            discount_value_cents=coupon.discount_value_cents,
            min_purchase_amount_cents=coupon.min_purchase_amount_cents,
            max_discount_amount_cents=coupon.max_discount_amount_cents,
            applicable_product_ids=coupon.applicable_product_ids,
            applicable_category_ids=coupon.applicable_category_ids,
            usage_limit=coupon.usage_limit,
            usage_count=coupon.usage_count,
            per_user_limit=coupon.per_user_limit,
            is_active=coupon.is_active,
            starts_at=coupon.starts_at,
            expires_at=coupon.expires_at,
            created_at=coupon.created_at,
            updated_at=coupon.updated_at,
            external_metadata=coupon.external_metadata,
            promotion=getattr(coupon, 'promotion', False),
            promotion_metadata=getattr(coupon, 'promotion_metadata', None)
        )
        self.db.add(db_coupon)
        await self.db.commit()
        await self.db.refresh(db_coupon)
        return db_coupon
