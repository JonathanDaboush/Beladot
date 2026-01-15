"""
seller_payout.py

Model for seller payout entity.
Represents a payout to a seller, including amount, currency, and status.
"""

class SellerPayout:
    def __init__(self, payout_id, seller_id, amount, currency, date_of_payment, status, created_at):
        """
        Initialize SellerPayout.
        Args:
            payout_id (int): Unique identifier for the payout.
            seller_id (int): Seller ID.
            amount (float): Payout amount.
            currency (str): Currency code.
            date_of_payment (datetime): Date of payment.
            status (str): Payout status.
            created_at (datetime): Creation timestamp.
        """
        self.payout_id = payout_id
        self.seller_id = seller_id
        self.amount = amount
        self.currency = currency
        self.date_of_payment = date_of_payment
        self.status = status
        self.created_at = created_at
