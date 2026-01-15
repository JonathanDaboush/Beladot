"""
product_review.py

Model for product review entity.
Represents a user's review for a product, including rating and text.
"""

class ProductReview:
    def __init__(self, review_id, product_id, user_id, rating_id, review_text, created_at):
        """
        Initialize ProductReview.
        Args:
            review_id (int): Unique identifier for the review.
            product_id (int): Associated product ID.
            user_id (int): User ID who made the review.
            rating_id (int): Associated rating ID.
            review_text (str): Review text.
            created_at (datetime): Creation timestamp.
        """
        self.review_id = review_id
        self.product_id = product_id
        self.user_id = user_id
        self.rating_id = rating_id
        self.review_text = review_text
        self.created_at = created_at
