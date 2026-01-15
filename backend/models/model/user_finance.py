"""
user_finance.py

Model for user finance entity.
Represents a user's financial information, including bank, card, and account details.
"""

class UserFinance:
    def __init__(self, uf_id, user_id, bank, pin, cvv, credit_card_number, account_type):
        """
        Initialize UserFinance.
        Args:
            uf_id (int): Unique identifier for the user finance record.
            user_id (int): Associated user ID.
            bank (str): Bank name.
            pin (str): Bank PIN code.
            cvv (str): Card CVV code.
            credit_card_number (str): Credit card number.
            account_type (str): Type of account (e.g., checking, savings).
        """
        self.uf_id = uf_id
        self.user_id = user_id
        self.bank = bank
        self.pin = pin
        self.cvv = cvv
        self.credit_card_number = credit_card_number
        self.account_type = account_type
