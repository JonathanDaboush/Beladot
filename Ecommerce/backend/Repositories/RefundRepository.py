from sqlalchemy.ext.asyncio import AsyncSession
from Models.Refund import Refund


class RefundRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Refund
