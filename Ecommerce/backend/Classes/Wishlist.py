from datetime import datetime, timezone

class Wishlist:
    """
    Domain model representing a user's wishlist for future purchase consideration.
    
    This class manages a user's saved products, enabling customers to bookmark items
    for later purchase. It prevents duplicates and tracks when items were added.
    
    Key Responsibilities:
        - Store user's saved product variants
        - Add variants without duplicates
        - Remove variants from list
        - Track wishlist modification timestamps
    
    Design Pattern:
        - Aggregate Root: Owns WishlistItems lifecycle
        - One-to-many with WishlistItems
    
    Use Cases:
        - Save for later: Customer bookmarks interesting products
        - Price tracking: Monitor saved items for price drops
        - Gift registry: Share wishlist with others
    
    Design Notes:
        - Items stored by variant_id (specific size/color/etc.)
        - Duplicate prevention at add time (idempotent)
        - This is a domain object; persistence handled by WishlistRepository
    """
    def __init__(self, id, user_id, created_at, updated_at):
        """
        Initialize a Wishlist domain object.
        
        Args:
            id: Unique identifier (None for new wishlists before persistence)
            user_id: Foreign key to the owning user
            created_at: Wishlist creation timestamp
            updated_at: Last modification timestamp
        """
        self.id = id
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
        self._items = []
    
    def add(self, variant_id: str, repository=None) -> None:
        """
        Add a product variant to the wishlist (idempotent, prevents duplicates).
        
        Args:
            variant_id: Product variant to add
            repository: Repository for persisting item and wishlist (optional)
            
        Side Effects:
            - Creates WishlistItem if not already present
            - Appends item to self._items
            - Updates self.updated_at
            - Persists item and wishlist via repository
            
        Design Notes:
            - Idempotent (returns early if variant already in wishlist)
            - No error on duplicate (silent success)
        """
        if any(item.variant_id == variant_id for item in self._items):
            return
        
        from Classes.WishlistItem import WishlistItem
        item = WishlistItem(
            id=None,
            wishlist_id=self.id,
            variant_id=variant_id,
            added_at=datetime.now(timezone.utc)
        )
        
        if repository:
            item = repository.create_item(item)
        
        self._items.append(item)
        self.updated_at = datetime.now(timezone.utc)
        
        if repository:
            repository.update(self)
    
    def remove(self, variant_id: str, repository=None) -> None:
        """
        Remove a product variant from the wishlist.
        
        Args:
            variant_id: Product variant to remove
            repository: Repository for deleting item and updating wishlist (optional)
            
        Side Effects:
            - Removes item from self._items
            - Deletes item from database via repository
            - Updates self.updated_at
            - Persists wishlist via repository
            
        Design Notes:
            - Safe to call with non-existent variant (no error)
        """
        self._items = [item for item in self._items if item.variant_id != variant_id]
        
        if repository:
            repository.delete_item_by_variant(self.id, variant_id)
        
        self.updated_at = datetime.now(timezone.utc)
        
        if repository:
            repository.update(self)