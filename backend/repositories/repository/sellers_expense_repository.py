"""
sellers_expense_repository.py

Repository class for managing SellerExpense entities in the database.
Provides async CRUD operations for seller expenses.
"""

from backend.model.sellers_expense import SellerExpense
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class SellerExpenseRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_id(self, expense_id):
        """
        Retrieve a seller expense by ID.
        Args:
            expense_id (int): The ID of the seller expense.
        Returns:
            SellerExpense or None
        """
        result = await self.db.execute(
            select(SellerExpense).filter(SellerExpense.id == expense_id)
        )
        return result.scalars().first()

    async def save(self, seller_expense):
        """
        Save a new seller expense to the database.
        Args:
            seller_expense (SellerExpense): The seller expense to save.
        Returns:
            SellerExpense: The saved seller expense.
        """
        self.db.add(seller_expense)
        await self.db.commit()
        await self.db.refresh(seller_expense)
        return seller_expense

    async def update(self, expense_id, **kwargs):
        """
        Update a seller expense by ID.
        Args:
            expense_id (int): The ID of the seller expense to update.
            **kwargs: Fields to update.
        Returns:
            SellerExpense or None: The updated expense, or None if not found.
        """
        expense = await self.get_by_id(expense_id)
        if not expense:
            return None
        for k, v in kwargs.items():
            if hasattr(expense, k):
                setattr(expense, k, v)
        await self.db.commit()
        return expense

    async def delete(self, expense_id):
        """
        Delete a seller expense by ID.
        Args:
            expense_id (int): The ID of the seller expense to delete.
        Returns:
            bool: True if deleted, False otherwise.
        """
        expense = await self.get_by_id(expense_id)
        if expense:
            await self.db.delete(expense)
            await self.db.commit()
            return True
        return False
