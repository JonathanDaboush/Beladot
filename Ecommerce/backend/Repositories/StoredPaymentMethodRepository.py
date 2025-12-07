from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from Models.StoredPaymentMethod import StoredPaymentMethod


class StoredPaymentMethodRepository:
    """Repository for stored payment method operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, payment_method: StoredPaymentMethod) -> StoredPaymentMethod:
        """Create a new stored payment method."""
        self.session.add(payment_method)
        await self.session.commit()
        await self.session.refresh(payment_method)
        return payment_method
    
    async def get_by_id(self, payment_method_id: int) -> Optional[StoredPaymentMethod]:
        """Get payment method by ID."""
        result = await self.session.execute(
            select(StoredPaymentMethod).where(StoredPaymentMethod.id == payment_method_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user(self, user_id: int, active_only: bool = True) -> List[StoredPaymentMethod]:
        """Get all payment methods for a user."""
        query = select(StoredPaymentMethod).where(StoredPaymentMethod.user_id == user_id)
        if active_only:
            query = query.where(StoredPaymentMethod.is_active == True)
        result = await self.session.execute(query.order_by(StoredPaymentMethod.is_default.desc()))
        return list(result.scalars().all())
    
    async def get_default_for_user(self, user_id: int) -> Optional[StoredPaymentMethod]:
        """Get user's default payment method."""
        result = await self.session.execute(
            select(StoredPaymentMethod).where(
                StoredPaymentMethod.user_id == user_id,
                StoredPaymentMethod.is_default == True,
                StoredPaymentMethod.is_active == True
            )
        )
        return result.scalar_one_or_none()
    
    async def set_default(self, payment_method_id: int, user_id: int) -> StoredPaymentMethod:
        """Set a payment method as default and unset others."""
        # Unset all other defaults for this user
        await self.session.execute(
            update(StoredPaymentMethod)
            .where(StoredPaymentMethod.user_id == user_id)
            .values(is_default=False)
        )
        
        # Set this one as default
        await self.session.execute(
            update(StoredPaymentMethod)
            .where(StoredPaymentMethod.id == payment_method_id)
            .values(is_default=True)
        )
        
        await self.session.commit()
        
        result = await self.session.execute(
            select(StoredPaymentMethod).where(StoredPaymentMethod.id == payment_method_id)
        )
        return result.scalar_one()
    
    async def update(self, payment_method: StoredPaymentMethod) -> StoredPaymentMethod:
        """Update payment method."""
        await self.session.commit()
        await self.session.refresh(payment_method)
        return payment_method
    
    async def delete(self, payment_method_id: int) -> bool:
        """Soft delete by marking as inactive."""
        await self.session.execute(
            update(StoredPaymentMethod)
            .where(StoredPaymentMethod.id == payment_method_id)
            .values(is_active=False, is_default=False)
        )
        await self.session.commit()
        return True
