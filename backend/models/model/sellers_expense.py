"""
sellers_expense.py

SQLAlchemy model for seller expense entity.
Represents an expense record for a seller, linked to an order.
"""

from sqlalchemy import Column, Integer, Float, ForeignKey
from backend.persistance.base import Base

class SellerExpense(Base):
    __tablename__ = 'sellers_expense'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.order_id'), nullable=False)
    amount = Column(Float, nullable=False)  # Negative for owed, positive for given

    def __init__(self, order_id, amount):
        """
        Initialize SellerExpense.
        Args:
            order_id (int): Associated order ID.
            amount (float): Expense amount (negative for owed, positive for given).
        """
        self.order_id = order_id
        self.amount = amount
