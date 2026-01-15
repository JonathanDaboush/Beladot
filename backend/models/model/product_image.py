"""
product_image.py

Model for product image entity.
Represents an image associated with a product.
"""

class ProductImage:
    def __init__(self, image_id, product_id, image_url):
        """
        Initialize ProductImage.
        Args:
            image_id (int): Unique identifier for the image.
            product_id (int): Associated product ID.
            image_url (str): URL of the product image.
        """
        self.image_id = image_id
        self.product_id = product_id
        self.image_url = image_url
