from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Category import Category


class CategoryRepository:
    """
    Data access layer for Category entities.
    
    This repository handles category data access, supporting hierarchical
    category trees with parent-child relationships.
    
    Responsibilities:
        - CRUD operations for Category entities
        - Support hierarchical category queries
        - Manage category tree integrity
    
    Design Patterns:
        - Repository Pattern: Isolates category data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = CategoryRepository(db_session)
        category = await repository.get_by_id(category_id)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = Category
    
    async def get_by_id(self, category_id: int) -> Category:
        """
        Retrieve a category by its unique identifier.
        
        Args:
            category_id: The unique ID of the category
            
        Returns:
            Category: The category object if found, None otherwise
        """
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()
    
    async def update(self, category: Category):
        """
        Update an existing category.
        
        Args:
            category: Category object with modifications
            
        Side Effects:
            - Updates category.updated_at
            - Commits transaction immediately
        """
        await self.db.merge(category)
        await self.db.commit()
        await self.db.refresh(category)
