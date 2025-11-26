from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.AuditLog import AuditLog
from typing import List


class AuditLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = AuditLog
    
    async def create(self, log_data: dict) -> AuditLog:
        audit_log = AuditLog(**log_data)
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        return audit_log
    
    async def get_by_target(self, target_type: str, target_id: int, limit: int = 50) -> List[AuditLog]:
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.target_type == target_type)
            .where(AuditLog.target_id == target_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
