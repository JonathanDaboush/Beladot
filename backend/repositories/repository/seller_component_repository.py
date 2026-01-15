"""
seller_component_repository.py

Repository class for managing SellerComponent entities in the database.
Provides async CRUD operations for seller components.
"""

from backend.persistance.seller_component import SellerComponent
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class SellerComponentRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_all(self):
        """
        Retrieve all seller components.
        Returns:
            list[SellerComponent]: List of seller components.
        """
        result = await self.db.execute(select(SellerComponent))
        return result.scalars().all()

    async def get_by_id(self, id):
        """
        Retrieve a seller component by ID.
        Args:
            id (int): The ID of the seller component.
        Returns:
            SellerComponent or None
        """
        result = await self.db.execute(select(SellerComponent).filter(SellerComponent.id == id))
        return result.scalars().first()

    async def create(self, img_url, description):
        """
        Create a new seller component.
        Args:
            img_url (str): Image URL for the component.
            description (str): Description of the component.
        Returns:
            SellerComponent: The created seller component.
        """
        component = SellerComponent(img_url=img_url, description=description)
        self.db.add(component)
        await self.db.commit()
        await self.db.refresh(component)
        return component

    async def update(self, id, **kwargs):
        """
        Update a seller component by ID.
        Args:
            id (int): The ID of the seller component to update.
            **kwargs: Fields to update.
        Returns:
            SellerComponent or None: The updated component, or None if not found.
        """
        component = await self.get_by_id(id)
        if not component:
            return None
        for k, v in kwargs.items():
            if hasattr(component, k):
                setattr(component, k, v)
        await self.db.commit()
        return component

    async def delete(self, id):
        """
        Delete a seller component by ID.
        Args:
            id (int): The ID of the seller component to delete.
        Returns:
            bool: True if deleted, False otherwise.
        """
        component = await self.get_by_id(id)
        if not component:
            return False
        await self.db.delete(component)
        await self.db.commit()
        return True
