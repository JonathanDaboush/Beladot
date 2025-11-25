from sqlalchemy.ext.asyncio import AsyncSession
from Models.Job import Job


class JobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Job
