from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Return import Return
from Models.Refund import Refund
from Models.AuditLog import AuditLog


class ReturnRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Return
    
    async def update(self, return_obj: Return):
        await self.db.merge(return_obj)
        await self.db.commit()
        await self.db.refresh(return_obj)
    
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
