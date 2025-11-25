from datetime import datetime, timezone

class Wishlist:
    def __init__(self, id, user_id, created_at, updated_at):
        self.id = id
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
        self._items = []
    
    def add(self, variant_id: str, repository=None) -> None:
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
        self._items = [item for item in self._items if item.variant_id != variant_id]
        
        if repository:
            repository.delete_item_by_variant(self.id, variant_id)
        
        self.updated_at = datetime.now(timezone.utc)
        
        if repository:
            repository.update(self)