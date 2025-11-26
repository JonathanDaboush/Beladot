from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Payment import Payment


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Payment
    
    async def update(self, payment: Payment):
        await self.db.merge(payment)
        await self.db.commit()
        await self.db.refresh(payment)
