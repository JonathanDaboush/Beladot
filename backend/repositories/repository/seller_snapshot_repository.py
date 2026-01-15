


"""
seller_snapshot_repository.py

Repository class for managing SellerSnapshot entities in the database.
Provides async method for retrieving seller snapshots by store name.
"""

from backend.model.seller_snapshot import SellerSnapshot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class SellerSnapshotRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_id(self, store_name):
        """
        Retrieve a seller snapshot by store name.
        Args:
            store_name (str): The name of the store.
        Returns:
            SellerSnapshot or None
        """
        result = await self.db.execute(
            select(SellerSnapshot).filter(SellerSnapshot.store_name == store_name)
        )
        return result.scalars().first()
