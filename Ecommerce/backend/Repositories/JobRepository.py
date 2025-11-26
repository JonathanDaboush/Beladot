from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Job import Job


class JobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Job
    
    async def update(self, job: Job):
        await self.db.merge(job)
        await self.db.commit()
        await self.db.refresh(job)
    
    async def create(self, job: Job) -> Job:
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job
