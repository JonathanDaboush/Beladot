from sqlalchemy.ext.asyncio import AsyncSession
from Models.Category import Category


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Category
