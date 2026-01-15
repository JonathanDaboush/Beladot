"""
seller_review_response.py

Model for seller review response entity.
Represents a seller's response to a product review, including text and timestamps.
"""

class SellerReviewResponse:
    def __init__(self, response_id, review_id, seller_id, response_text, created_at):
        """
        Initialize SellerReviewResponse.
        Args:
            response_id (int): Unique identifier for the response.
            review_id (int): Associated review ID.
            seller_id (int): Seller ID.
            response_text (str): Text of the response.
            created_at (datetime): Creation timestamp.
        """
        self.response_id = response_id
        self.review_id = review_id
        self.seller_id = seller_id
        self.response_text = response_text
        self.created_at = created_at
