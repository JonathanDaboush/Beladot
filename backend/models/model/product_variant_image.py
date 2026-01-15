"""
product_variant_image.py

Model for product variant image entity.
Represents an image associated with a specific product variant.
"""

class ProductVariantImage:
    def __init__(self, image_id, variant_id, image_url):
        """
        Initialize ProductVariantImage.
        Args:
            image_id (int): Unique identifier for the image.
            variant_id (int): Associated variant ID.
            image_url (str): URL of the variant image.
        """
        self.image_id = image_id
        self.variant_id = variant_id
        self.image_url = image_url
