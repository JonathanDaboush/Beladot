
# ------------------------------------------------------------------------------
# customer_component_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing SellerComponent records from the database.
# Provides async CRUD methods for seller components.
# ------------------------------------------------------------------------------

from backend.persistance.seller_component import SellerComponent
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class SellerComponentRepository:
    """
    Repository for SellerComponent model.
    Provides async CRUD operations for seller components.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def get_all(self):
        """Retrieve all seller components."""
        result = await self.db.execute(select(SellerComponent))
        return result.scalars().all()

    async def get_by_id(self, id):
        """Retrieve a seller component by its ID."""
        result = await self.db.execute(select(SellerComponent).filter(SellerComponent.id == id))
        return result.scalars().first()

    async def create(self, img_url, description):
        """Create a new seller component."""
        component = SellerComponent(img_url=img_url, description=description)
        self.db.add(component)
        await self.db.commit()
        await self.db.refresh(component)
        return component

    async def update(self, id, **kwargs):
        """Update an existing seller component by ID with provided fields."""
        component = await self.get_by_id(id)
        if not component:
            return None
        for k, v in kwargs.items():
            if hasattr(component, k):
                setattr(component, k, v)
        await self.db.commit()
        return component

    async def delete(self, id):
        """Delete a seller component by its ID."""
        component = await self.get_by_id(id)
        if not component:
            return False
        await self.db.delete(component)
        await self.db.commit()
        return True
