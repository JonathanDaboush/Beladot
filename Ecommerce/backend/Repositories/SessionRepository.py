from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Session import Session


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Session
    
    async def update(self, session: Session):
        await self.db.merge(session)
        await self.db.commit()
        await self.db.refresh(session)
