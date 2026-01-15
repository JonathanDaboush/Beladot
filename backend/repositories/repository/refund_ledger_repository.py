"""
refund_ledger_repository.py

Repository class for managing RefundLedger entities in the database.
Provides async methods for saving refund ledger entries.
"""

from backend.model.refund_ledger import RefundLedger
from sqlalchemy.ext.asyncio import AsyncSession

class RefundLedgerRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def save(self, ledger_entry):
        """
        Save a new refund ledger entry to the database.
        Args:
            ledger_entry (RefundLedger): The ledger entry to save.
        Returns:
            RefundLedger: The saved ledger entry.
        """
        self.db.add(ledger_entry)
        await self.db.commit()
        await self.db.refresh(ledger_entry)
        return ledger_entry
