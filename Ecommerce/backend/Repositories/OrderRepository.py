from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Order import Order
from Models.Payment import Payment
from Models.Refund import Refund
from Models.AuditLog import AuditLog


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Order
    
    async def update(self, order: Order):
        await self.db.merge(order)
        await self.db.commit()
        await self.db.refresh(order)
    
    async def create_payment(self, payment: Payment) -> Payment:
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment
    
    async def create_audit_log(self, log_data: dict) -> AuditLog:
        audit_log = AuditLog(**log_data)
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        return audit_log
    
    async def create_refund(self, refund: Refund) -> Refund:
        self.db.add(refund)
        await self.db.commit()
        await self.db.refresh(refund)
        return refund
