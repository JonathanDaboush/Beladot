from sqlalchemy.ext.asyncio import AsyncSession
from Models.Payment import Payment


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Payment
