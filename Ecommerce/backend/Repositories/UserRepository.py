from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.User import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = User
    
    async def get_by_id(self, user_id: int) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> User:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update(self, user: User):
        await self.db.merge(user)
        await self.db.commit()
        await self.db.refresh(user)
