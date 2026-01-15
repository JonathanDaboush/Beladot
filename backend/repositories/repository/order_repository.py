
# ------------------------------------------------------------------------------
# order_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing Order records from the database.
# Provides async CRUD and filtering methods for orders, including advanced filters.
# ------------------------------------------------------------------------------

from backend.model.order import Order
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class OrderRepository:
    """
    Repository for Order model.
    Provides async CRUD operations and advanced filtering for orders.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def filter_orders(self, product_id=None, age_range=None, sex=None, start_date=None, end_date=None):
        """
        Retrieve orders filtered by product, user age range, sex, and date range.
        Args:
            product_id (int, optional): Filter by product ID.
            age_range (tuple, optional): (min_age, max_age) to filter users by age.
            sex (str, optional): Filter users by sex.
            start_date (date, optional): Filter orders created after this date.
            end_date (date, optional): Filter orders created before this date.
        Returns:
            list[Order]: List of filtered Order objects.
        """
        stmt = select(Order).filter(Order.is_deleted == False)
        if start_date:
            stmt = stmt.filter(Order.created_at >= start_date)
        if end_date:
            stmt = stmt.filter(Order.created_at <= end_date)
        if product_id:
            from backend.model.order_item import OrderItem
            result = await self.db.execute(select(OrderItem).filter(OrderItem.product_id == product_id))
            order_ids = [oi.order_id for oi in result.scalars().all()]
            stmt = stmt.filter(Order.order_id.in_(order_ids))
        if age_range or sex:
            from backend.model.user import User
            stmt = stmt.join(User, Order.user_id == User.user_id)
            if age_range:
                import datetime
                today = datetime.date.today()
                min_age, max_age = age_range
                min_dob = today.replace(year=today.year - max_age)
                max_dob = today.replace(year=today.year - min_age)
                stmt = stmt.filter(User.dob >= min_dob, User.dob <= max_dob)
            if sex:
                if hasattr(User, 'sex'):
                    stmt = stmt.filter(User.sex == sex)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, order_id):
        """Retrieve an order by its ID, excluding deleted orders."""
        result = await self.db.execute(
            select(Order).filter(Order.order_id == order_id, Order.is_deleted == False)
        )
        return result.scalars().first()

    async def save(self, order):
        """Save a new order to the database."""
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def update(self, order_id, **kwargs):
        """Update an existing order by ID with provided fields."""
        order = await self.get_by_id(order_id)
        if not order:
            return None
        for k, v in kwargs.items():
            if hasattr(order, k):
                setattr(order, k, v)
        await self.db.commit()
        return order

    async def delete(self, order_id):
        """Soft delete an order by its ID (marks as deleted)."""
        order = await self.get_by_id(order_id)
        if order:
            await self.db.delete(order)
            await self.db.commit()
            return True
        return False
