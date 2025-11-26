from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.APIKey import APIKey
from Models.AuditLog import AuditLog


class APIKeyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = APIKey
    
    async def update(self, api_key: APIKey):
        await self.db.merge(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
    
    async def create_audit_log(self, log_data: dict) -> AuditLog:
        audit_log = AuditLog(**log_data)
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        return audit_log
