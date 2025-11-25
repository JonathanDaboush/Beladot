from sqlalchemy.ext.asyncio import AsyncSession
from Models.Session import Session


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Session
