from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Review import Review
from Models.AuditLog import AuditLog


class ReviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Review
    
    async def update(self, review: Review):
        await self.db.merge(review)
        await self.db.commit()
        await self.db.refresh(review)
    
    async def create_audit_log(self, log_data: dict) -> AuditLog:
        audit_log = AuditLog(**log_data)
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        return audit_log
