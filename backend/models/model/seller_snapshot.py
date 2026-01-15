"""
seller_snapshot.py

Model for seller snapshot entity.
Represents a snapshot of a seller's store, contact, and approval details.
"""

class SellerSnapshot:
    def __init__(self, store_name, contact_email, seller_type, approved_by_name):
        """
        Initialize SellerSnapshot.
        Args:
            store_name (str): Name of the seller's store.
            contact_email (str): Seller's contact email.
            seller_type (str): Type of seller.
            approved_by_name (str): Name of the approver.
        """
        self.store_name = store_name
        self.contact_email = contact_email
        self.seller_type = seller_type
        self.approved_by_name = approved_by_name
