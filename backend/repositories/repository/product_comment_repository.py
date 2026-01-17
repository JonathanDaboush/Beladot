
# ------------------------------------------------------------------------------
# product_comment_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing ProductComment records from the database.
# Provides async CRUD methods for product comments and product-specific queries.
# ------------------------------------------------------------------------------

from backend.persistance.product_comment import ProductComment
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class ProductCommentRepository:
    """
    Repository for ProductComment model.
    Provides async CRUD operations for product comments and product-specific queries.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def get_by_id(self, comment_id):
        """Retrieve a product comment by its ID, excluding deleted comments."""
        result = await self.db.execute(
            select(ProductComment).filter(ProductComment.comment_id == comment_id, ProductComment.is_deleted == False)
        )
        return result.scalars().first()

    async def save(self, comment):
        """Save a new product comment to the database."""
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def update(self, comment_id, **kwargs):
        """Update an existing product comment by ID with provided fields."""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return None
        for k, v in kwargs.items():
            if hasattr(comment, k):
                setattr(comment, k, v)
        await self.db.commit()
        return comment

    async def delete(self, comment_id):
        """Delete a product comment by its ID."""
        comment = await self.get_by_id(comment_id)
        if comment:
            await self.db.delete(comment)
            await self.db.commit()
            return True
        return False

    async def get_comments_for_product(self, product_id):
        """Retrieve all comments for a specific product, excluding deleted comments."""
        result = await self.db.execute(
            select(ProductComment).filter(ProductComment.product_id == product_id, ProductComment.is_deleted == False)
        )
        return result.scalars().all()
