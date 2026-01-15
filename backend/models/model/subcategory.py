"""
subcategory.py

Model for subcategory entity.
Represents a product subcategory, linked to a category and optional image.
"""

class Subcategory:
    def __init__(self, subcategory_id, category_id, name, image_url=None):
        """
        Initialize Subcategory.
        Args:
            subcategory_id (int): Unique identifier for the subcategory.
            category_id (int): Associated category ID.
            name (str): Name of the subcategory.
            image_url (str, optional): URL of the subcategory image.
        """
        self.subcategory_id = subcategory_id
        self.category_id = category_id
        self.name = name
        self.image_url = image_url
