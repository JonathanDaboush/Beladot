"""
user_repository.py

Repository class for managing User entities in the database.
Provides async CRUD operations and password management for users.
"""

from typing import Optional, List
from backend.persistance.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User, int]):
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get(self, user_id: int) -> Optional[User]:
        """
        Retrieve a user by their ID.
        Args:
            user_id (int): The ID of the user.
        Returns:
            User or None
        """
        result = await self.db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.
        Args:
            email (str): The email address of the user.
        Returns:
            User or None
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    async def list(self, *, limit: int = 100, offset: int = 0) -> List[User]:
        """
        List users with pagination and deterministic ordering.
        Args:
            limit (int): Max number of users to return.
            offset (int): Number of users to skip.
        Returns:
            List[User]
        """
        result = await self.db.execute(
            select(User).order_by(User.user_id).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def add(self, user: User) -> User:
        """
        Add a new user to the database.
        Args:
            user (User): The user to add.
        Returns:
            User: The added user.
        """
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: int, user: User) -> User | None:
        """
        Update an existing user in the database.
        Args:
            user (User): The user to update.
        Returns:
            User: The updated user.
        """
        self.db.merge(user)
        await self.db.flush()
        return user

    async def update_password_by_email(self, email: str, new_password: str) -> bool:
        """
        Update a user's password by their email address.
        Args:
            email (str): The email address of the user.
            new_password (str): The new password to set.
        Returns:
            bool: True if updated, False otherwise.
        """
        user = await self.get_by_email(email)
        if user:
            user.password = new_password
            await self.update(user.user_id, user)
            return True
        return False

    async def delete(self, user_id: int) -> Optional[User]:
        """
        Remove a user from the database by their ID.
        Args:
            user_id (int): The ID of the user to remove.
        Returns:
            User or None: The removed user, or None if not found.
        """
        user = await self.get(user_id)
        if user:
            self.db.delete(user)
            await self.db.flush()
        return user

    async def remove_user(self, user: User) -> User:
        """
        Remove a user from the database.
        Args:
            user (User): The user to remove.
        Returns:
            User: The removed user.
        """
        self.db.delete(user)
        await self.db.flush()
        return user
