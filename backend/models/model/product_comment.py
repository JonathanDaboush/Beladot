"""
product_comment.py

Model for product comment entity.
Represents a user's comment on a product.
"""

class ProductComment:
    def __init__(self, id, product_id, user_id, comment, created_at=None):
        """
        Initialize ProductComment.
        Args:
            id (int): Unique identifier for the comment.
            product_id (int): Associated product ID.
            user_id (int): User ID who made the comment.
            comment (str): Comment text.
            created_at (datetime, optional): Creation timestamp.
        """
        self.id = id
        self.product_id = product_id
        self.user_id = user_id
        self.comment = comment
        self.created_at = created_at
