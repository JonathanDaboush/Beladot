"""
user_repository.py

Repository class for managing User entities in the database.
Provides async CRUD operations and password management for users.
"""

from backend.model.user import User

class UserRepository:
    def __init__(self, db):
        """
        Initialize the repository with a database session.
        Args:
            db: SQLAlchemy session or async session.
        """
        self.db = db

    async def get_by_id(self, user_id):
        """
        Retrieve a user by their ID.
        Args:
            user_id (int): The ID of the user.
        Returns:
            User or None
        """
        return await self.db.query(User).filter(User.user_id == user_id).first()

    async def get_by_email(self, email):
        """
        Retrieve a user by their email address.
        Args:
            email (str): The email address of the user.
        Returns:
            User or None
        """
        return await self.db.query(User).filter(User.email == email).first()

    async def add_user(self, user: User):
        """
        Add a new user to the database.
        Args:
            user (User): The user to add.
        Returns:
            User: The added user.
        """
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def set_user_for_update(self, user: User):
        """
        Update an existing user in the database.
        Args:
            user (User): The user to update.
        Returns:
            User: The updated user.
        """
        self.db.merge(user)
        await self.db.commit()
        return user

    async def update_password_by_email(self, email, new_password):
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
            await self.set_user_for_update(user)
            return True
        return False

    async def remove_user_by_id(self, user_id):
        """
        Remove a user from the database by their ID.
        Args:
            user_id (int): The ID of the user to remove.
        Returns:
            User or None: The removed user, or None if not found.
        """
        user = await self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            await self.db.commit()
        return user

    async def remove_user(self, user: User):
        """
        Remove a user from the database.
        Args:
            user (User): The user to remove.
        Returns:
            User: The removed user.
        """
        self.db.delete(user)
        await self.db.commit()
        return user
