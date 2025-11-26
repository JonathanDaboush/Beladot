from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.ProductFeed import ProductFeed
from Models.Job import Job


class ProductFeedRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = ProductFeed
    
    async def update(self, product_feed: ProductFeed):
        await self.db.merge(product_feed)
        await self.db.commit()
        await self.db.refresh(product_feed)
    
    async def create_job(self, job: Job) -> Job:
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job
