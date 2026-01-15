
# ------------------------------------------------------------------------------
# category_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing Category records from the database.
# Provides async methods for retrieving categories by ID.
# ------------------------------------------------------------------------------

from backend.model.category import Category

class CategoryRepository:
    """
    Repository for Category model.
    Provides async methods to retrieve categories by ID.
    """
    def __init__(self, db):
        """Initialize repository with DB session."""
        self.db = db

    async def get_by_id(self, category_id):
        """Retrieve a category by its ID."""
        return await self.db.query(Category).filter(Category.category_id == category_id).first()
