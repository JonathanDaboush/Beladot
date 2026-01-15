"""
product_rating.py

Model for product rating entity.
Represents a user's rating for a product.
"""

class ProductRating:
    def __init__(self, rating_id, product_id, user_id, rating, created_at):
        """
        Initialize ProductRating.
        Args:
            rating_id (int): Unique identifier for the rating.
            product_id (int): Associated product ID.
            user_id (int): User ID who made the rating.
            rating (float): Rating value.
            created_at (datetime): Creation timestamp.
        """
        self.rating_id = rating_id
        self.product_id = product_id
        self.user_id = user_id
        self.rating = rating
        self.created_at = created_at
