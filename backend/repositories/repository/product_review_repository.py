
# ------------------------------------------------------------------------------
# product_review_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing ProductReview records from the database.
# Provides async methods for retrieving product reviews by ID.
# ------------------------------------------------------------------------------

from backend.model.product_review import ProductReview
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class ProductReviewRepository:
    """
    Repository for ProductReview model.
    Provides async methods to retrieve product reviews by ID.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def get_by_id(self, review_id):
        """Retrieve a product review by its ID."""
        result = await self.db.execute(
            select(ProductReview).filter(ProductReview.review_id == review_id)
        )
        return result.scalars().first()
