from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.ProductFeed import ProductFeed
from Models.Job import Job


class ProductFeedRepository:
    """
    Data access layer for ProductFeed entities (catalog export feeds).
    
    This repository manages product feed configurations and generation jobs
    for external integrations (Google Shopping, Facebook, etc.).
    
    Responsibilities:
        - ProductFeed CRUD operations
        - Job creation for feed generation
        - Track feed generation history
    
    Design Patterns:
        - Repository Pattern: Isolates feed data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = ProductFeedRepository(db_session)
        await repository.update(feed)
        job = await repository.create_job(job_obj)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = ProductFeed
    
    async def update(self, product_feed: ProductFeed):
        """
        Update feed configuration or generation status.
        
        Args:
            product_feed: ProductFeed object with modifications
            
        Side Effects:
            - Updates feed.updated_at
            - Commits transaction immediately
        """
        await self.db.merge(product_feed)
        await self.db.commit()
        await self.db.refresh(product_feed)
    
    async def create_job(self, job: Job) -> Job:
        """
        Create a feed generation job.
        
        Args:
            job: Job object to persist
            
        Returns:
            Job: Created job with database-generated ID
            
        Use Case:
            Queue async feed generation task
        """
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job
