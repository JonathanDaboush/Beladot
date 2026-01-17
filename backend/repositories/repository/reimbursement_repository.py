

"""
reimbursement_repository.py

Repository class for managing Reimbursement entities in the database.
Provides async CRUD operations and incident-based queries for reimbursements.
"""

from backend.persistance.reimbursement import Reimbursement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class ReimbursementRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_all(self):
        """
        Retrieve all non-deleted reimbursements.
        Returns:
            list[Reimbursement]: List of reimbursements.
        """
        result = await self.db.execute(select(Reimbursement).filter(Reimbursement.deleted == False))
        return result.scalars().all()

    async def delete(self, reimbursement_id):
        """
        Soft-delete a reimbursement by setting its deleted flag.
        Args:
            reimbursement_id (int): The ID of the reimbursement to delete.
        Returns:
            bool: True if deleted, False otherwise.
        """
        reimbursement = await self.get_by_id(reimbursement_id, include_deleted=True)
        if not reimbursement:
            return False
        reimbursement.deleted = True
        await self.db.commit()
        return True

    async def get_by_id(self, reimbursement_id, include_deleted=False):
        """
        Retrieve a reimbursement by ID.
        Args:
            reimbursement_id (int): The ID of the reimbursement.
            include_deleted (bool): Whether to include deleted reimbursements.
        Returns:
            Reimbursement or None
        """
        query = select(Reimbursement).filter(Reimbursement.reimbursement_id == reimbursement_id)
        if not include_deleted:
            query = query.filter(Reimbursement.deleted == False)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def save(self, reimbursement):
        """
        Save a new reimbursement to the database.
        Args:
            reimbursement (Reimbursement): The reimbursement to save.
        Returns:
            Reimbursement: The saved reimbursement.
        """
        self.db.add(reimbursement)
        await self.db.commit()
        await self.db.refresh(reimbursement)
        return reimbursement

    async def update(self, reimbursement_id, **kwargs):
        """
        Update a reimbursement by ID.
        Args:
            reimbursement_id (int): The ID of the reimbursement to update.
            **kwargs: Fields to update.
        Returns:
            Reimbursement or None: The updated reimbursement, or None if not found.
        """
        reimbursement = await self.get_by_id(reimbursement_id)
        if not reimbursement:
            return None
        for k, v in kwargs.items():
            if hasattr(reimbursement, k):
                setattr(reimbursement, k, v)
        await self.db.commit()
        return reimbursement

    async def get_by_incident_id(self, incident_id):
        """
        Retrieve reimbursements by incident ID.
        Args:
            incident_id (int): The incident ID to filter by.
        Returns:
            list[Reimbursement]: List of reimbursements for the incident.
        """
        result = await self.db.execute(
            select(Reimbursement).filter(Reimbursement.incident_id == incident_id)
        )
        return result.scalars().all()
