from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Job import Job


class JobRepository:
    """
    Data access layer for Job entities (background task queue).
    
    This repository manages asynchronous job persistence for background
    tasks like email sending, feed generation, and report processing.
    
    Responsibilities:
        - Job CRUD operations
        - Track job status (pending, processing, completed, failed)
        - Support job queue management
    
    Design Patterns:
        - Repository Pattern: Isolates job data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = JobRepository(db_session)
        job = await repository.create(job_obj)
        await repository.update(job)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = Job
    
    async def update(self, job: Job):
        """
        Update job status and results.
        
        Args:
            job: Job object with modifications
            
        Side Effects:
            - Updates job status
            - Stores error messages or results
            - Commits transaction immediately
        """
        await self.db.merge(job)
        await self.db.commit()
        await self.db.refresh(job)
    
    async def create(self, job: Job) -> Job:
        """
        Queue a new background job.
        
        Args:
            job: Job object to persist
            
        Returns:
            Job: Created job with database-generated ID
            
        Side Effects:
            - Job enters pending queue
            - Worker picks it up asynchronously
        """
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job
