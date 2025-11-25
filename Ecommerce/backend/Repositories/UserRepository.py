from sqlalchemy.ext.asyncio import AsyncSession
from Models.User import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = User
