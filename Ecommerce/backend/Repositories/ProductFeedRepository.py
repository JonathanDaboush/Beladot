from sqlalchemy.ext.asyncio import AsyncSession
from Models.ProductFeed import ProductFeed


class ProductFeedRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = ProductFeed
