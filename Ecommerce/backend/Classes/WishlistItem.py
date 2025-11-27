# Represents a single product saved in a user's wishlist.
# Tracks what products user is interested in for future purchase consideration.

class WishlistItem:
    """
    Domain model representing a single product variant in a wishlist.
    
    This class represents one saved product variant, tracking when it was added.
    It's owned by the Wishlist aggregate.
    
    Key Responsibilities:
        - Link variant to wishlist
        - Track when variant was added
    
    Design Pattern:
        - Value Object within Wishlist aggregate
        - Owned entity (lifecycle controlled by Wishlist)
    
    Design Notes:
        - Minimal entity (just foreign keys and timestamp)
        - This is a domain object; persistence handled by WishlistItemRepository
    """
    def __init__(self, id, wishlist_id, variant_id, added_at):
        """
        Initialize a WishlistItem domain object.
        
        Args:
            id: Unique identifier (None for new items before persistence)
            wishlist_id: Foreign key to parent wishlist
            variant_id: Product variant identifier
            added_at: When variant was added to wishlist
        """
        self.id = id
        self.wishlist_id = wishlist_id
        self.variant_id = variant_id
        self.added_at = added_at
