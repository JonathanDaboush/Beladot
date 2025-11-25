from sqlalchemy.ext.asyncio import AsyncSession
from Models.Blob import Blob


class BlobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Blob
