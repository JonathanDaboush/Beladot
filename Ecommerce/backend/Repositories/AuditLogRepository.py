from sqlalchemy.ext.asyncio import AsyncSession
from Models.AuditLog import AuditLog


class AuditLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = AuditLog
