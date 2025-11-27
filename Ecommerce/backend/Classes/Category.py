from typing import Any, Optional

class Category:
    """
    Domain model representing a product category with hierarchical tree structure.
    
    This class manages product categorization with support for nested categories,
    preventing cycles, and generating breadcrumb trails. It enables multi-level
    category hierarchies like Electronics → Computers → Laptops.
    
    Key Responsibilities:
        - Store category information (name, description, slug)
        - Manage parent-child relationships
        - Prevent circular references in hierarchy
        - Generate breadcrumb trails for navigation
        - Support metadata for custom attributes
    
    Hierarchy Features:
        - Unlimited depth (with safeguards)
        - Cycle detection prevents infinite loops
        - Breadcrumbs for navigation (e.g., Home → Electronics → Laptops)
        - Parent caching for performance
    
    Design Patterns:
        - Composite Pattern: Recursive tree structure
        - Self-referential: parent_id references same table
    
    Design Notes:
        - slug used for SEO-friendly URLs
        - metadata enables custom fields without schema changes
        - This is a domain object; persistence handled by CategoryRepository
    """
    def __init__(self, id, parent_id, name, description, slug, metadata, created_at, updated_at):
        """
        Initialize a Category domain object.
        
        Args:
            id: Unique identifier (None for new categories before persistence)
            parent_id: Foreign key to parent category (None for root categories)
            name: Category name
            description: Category description
            slug: URL-friendly identifier (e.g., 'electronics')
            metadata: Custom attributes dictionary
            created_at: Category creation timestamp
            updated_at: Last modification timestamp
        """
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
        """
        Add a child category to this category with cycle detection.
        
        Args:
            child: Category to add as child
            repository: Repository for persisting the parent_id change
            
        Raises:
            ValueError: If child is None, has no ID, is self, or would create cycle
            
        Side Effects:
            - Sets child.parent_id to self.id
            - Persists child via repository
            
        Design Notes:
            - Cycle detection prevents infinite loops during traversal
            - Validates child existence before operation
            - Self-parenting explicitly prevented
        """
        if child is None or child.id is None:
            raise ValueError("Child category must exist and have an id")
        
        if child.id == self.id:
            raise ValueError("Category cannot be a child of itself")
        
        if self._would_create_cycle(child):
            raise ValueError("Adding this child would create a cycle in the category hierarchy")
        
        child.parent_id = self.id
        repository.update(child)
    
    def _would_create_cycle(self, child: 'Category') -> bool:
        """
        Check if adding child would create a circular reference.
        
        Args:
            child: Proposed child category
            
        Returns:
            bool: True if cycle detected, False otherwise
            
        Algorithm:
            - Traverse up the parent chain from self
            - Check if any ancestor is the proposed child
            - Track visited nodes to detect existing cycles
            
        Design Notes:
            - Uses parent cache when available for performance
            - Visited set prevents infinite loops
        """
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
        """
        Generate breadcrumb trail from root to this category.
        
        Args:
            repository: Repository for loading parent categories (optional)
            
        Returns:
            list: Categories from root to self (e.g., [Home, Electronics, Laptops])
            
        Safeguards:
            - Max depth of 10 levels (prevents infinite loops)
            - Visited set detects cycles
            - Breaks on missing parent
            
        Design Notes:
            - Without repository, returns only self
            - Inserts at front for correct order
            - Gracefully handles broken references
        """
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
        """
        Convert category to dictionary for API responses.
        
        Args:
            include_parent: If True, include parent_id field
            
        Returns:
            dict: Category data with optional parent_id
            
        Design Notes:
            - parent_id excluded by default (reduces payload for listings)
            - metadata included for custom attributes
        """
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