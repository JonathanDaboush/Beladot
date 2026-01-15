"""
wishlist_item.py

Model for wishlist item entity.
Represents an item in a user's wishlist, including product and variant details.
"""

class WishlistItem:
    def __init__(self, wishlist_item_id, wishlist_id, product_id, variant_id, quantity):
        """
        Initialize WishlistItem.
        Args:
            wishlist_item_id (int): Unique identifier for the wishlist item.
            wishlist_id (int): Associated wishlist ID.
            product_id (int): Product ID.
            variant_id (int): Variant ID.
            quantity (int): Quantity of the item.
        """
        self.wishlist_item_id = wishlist_item_id
        self.wishlist_id = wishlist_id
        self.product_id = product_id
        self.variant_id = variant_id
        self.quantity = quantity
