"""
product_variant.py

Model for product variant entity.
Represents a specific variant of a product, including price, stock, and availability.
"""

from backend.model.enums import AvailabilityStatus

class ProductVariant:
    def __init__(self, variant_id, product_id, name, price, stock, is_available=AvailabilityStatus.AVAILABLE):
        """
        Initialize ProductVariant.
        Args:
            variant_id (int): Unique identifier for the variant.
            product_id (int): Associated product ID.
            name (str): Name of the variant.
            price (float): Price of the variant.
            stock (int): Stock quantity.
            is_available (AvailabilityStatus, optional): Availability status.
        """
        self.variant_id = variant_id
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock
        self.is_available = is_available
