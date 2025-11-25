from sqlalchemy.ext.asyncio import AsyncSession
from Models.Review import Review


class ReviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Review
