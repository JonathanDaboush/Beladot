
# ------------------------------------------------------------------------------
# customer_shipment_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing CustomerShipment records from the database.
# Provides async CRUD methods for customer shipments.
# ------------------------------------------------------------------------------

from backend.persistance.customer_shipment import CustomerShipment
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class CustomerShipmentRepository:
    """
    Repository for CustomerShipment model.
    Provides async CRUD operations for customer shipments.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def get_by_id(self, cs_id):
        """Retrieve a customer shipment by its ID."""
        result = await self.db.execute(
            select(CustomerShipment).filter(CustomerShipment.cs_id == cs_id)
        )
        return result.scalars().first()

    async def create(self, **kwargs):
        """Create a new customer shipment."""
        shipment = CustomerShipment(**kwargs)
        self.db.add(shipment)
        await self.db.commit()
        await self.db.refresh(shipment)
        return shipment

    async def update(self, cs_id, **kwargs):
        """Update an existing customer shipment by ID with provided fields."""
        shipment = await self.get_by_id(cs_id)
        if not shipment:
            return None
        for k, v in kwargs.items():
            if hasattr(shipment, k):
                setattr(shipment, k, v)
        await self.db.commit()
        return shipment

    async def delete(self, cs_id):
        """Delete a customer shipment by its ID."""
        shipment = await self.get_by_id(cs_id)
        if shipment:
            await self.db.delete(shipment)
            await self.db.commit()
            return True
        return False
