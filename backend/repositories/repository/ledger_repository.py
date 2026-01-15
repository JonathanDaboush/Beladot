
# ------------------------------------------------------------------------------
# ledger_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing LedgerEntry records from the database.
# Provides async methods for saving ledger entries.
# ------------------------------------------------------------------------------

from backend.model.ledger import LedgerEntry
from sqlalchemy.ext.asyncio import AsyncSession

class LedgerRepository:
    """
    Repository for LedgerEntry model.
    Provides async methods to save ledger entries.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def save(self, ledger_entry):
        """Save a new ledger entry to the database."""
        self.db.add(ledger_entry)
        await self.db.commit()
        await self.db.refresh(ledger_entry)
        return ledger_entry
