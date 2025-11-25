from sqlalchemy.ext.asyncio import AsyncSession
from Models.APIKey import APIKey


class APIKeyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = APIKey
