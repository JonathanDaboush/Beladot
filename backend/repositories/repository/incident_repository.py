
# ------------------------------------------------------------------------------
# incident_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing Incident records from the database.
# Provides CRUD methods for incidents, including soft delete.
# ------------------------------------------------------------------------------

from backend.persistance.incident import Incident
from sqlalchemy import select, update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

class IncidentRepository:
    """
    Repository for Incident model.
    Provides CRUD operations for incidents, including soft delete.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def get_by_id(self, incident_id, include_deleted=False):
        """Async retrieve an incident by its ID, optionally including deleted incidents."""
        stmt = select(Incident).where(Incident.incident_id == incident_id)
        if not include_deleted:
            stmt = stmt.where(Incident.deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, incident):
        """Async save a new incident to the database."""
        self.db.add(incident)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(incident)
        return incident

    async def update(self, incident_id, **kwargs):
        """Async update an existing incident by ID with provided fields."""
        incident = await self.get_by_id(incident_id)
        if not incident:
            return None
        for k, v in kwargs.items():
            if hasattr(incident, k):
                setattr(incident, k, v)
        await self.db.commit()
        return incident

    async def delete(self, incident_id):
        """Async soft delete an incident by its ID (marks as deleted)."""
        incident = await self.get_by_id(incident_id, include_deleted=True)
        if not incident:
            return False
        incident.deleted = True
        await self.db.commit()
        return True

    async def get_all(self):
        """Async retrieve all non-deleted incidents."""
        stmt = select(Incident).where(Incident.deleted == False)
        result = await self.db.execute(stmt)
        return result.scalars().all()
