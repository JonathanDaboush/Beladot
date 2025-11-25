from typing import Any, Optional

class Category:
    def __init__(self, id, parent_id, name, description, slug, metadata, created_at, updated_at):
        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.description = description
        self.slug = slug
        self.metadata = metadata
        self.created_at = created_at
        self.updated_at = updated_at
        self._parent_cache: Optional['Category'] = None
    
    def add_child(self, child: 'Category', repository) -> None:
        if child is None or child.id is None:
            raise ValueError("Child category must exist and have an id")
        
        if child.id == self.id:
            raise ValueError("Category cannot be a child of itself")
        
        if self._would_create_cycle(child):
            raise ValueError("Adding this child would create a cycle in the category hierarchy")
        
        child.parent_id = self.id
        repository.update(child)
    
    def _would_create_cycle(self, child: 'Category') -> bool:
        current = self
        visited = set()
        
        while current and current.parent_id:
            if current.id in visited:
                return True
            visited.add(current.id)
            
            if current.parent_id == child.id:
                return True
            
            if hasattr(current, '_parent_cache') and current._parent_cache:
                current = current._parent_cache
            else:
                break
        
        return False
    
    def get_breadcrumbs(self, repository=None) -> list['Category']:
        breadcrumbs = []
        current = self
        visited = set()
        max_depth = 10
        
        while current and len(breadcrumbs) < max_depth:
            if current.id in visited:
                break
            
            breadcrumbs.insert(0, current)
            visited.add(current.id)
            
            if current.parent_id is None:
                break
            
            if repository:
                try:
                    parent = repository.get_by_id(current.parent_id)
                    if parent:
                        current = parent
                    else:
                        break
                except:
                    break
            else:
                break
        
        return breadcrumbs
    
    def to_dict(self, include_parent: bool = False) -> dict[str, Any]:
        result = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_parent:
            result["parent_id"] = self.parent_id
        
        return result