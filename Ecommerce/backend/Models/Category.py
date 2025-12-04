from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Category(Base):
    """
    SQLAlchemy ORM model for categories table.
    
    Hierarchical product taxonomy supporting unlimited nesting depth.
    Uses self-referential foreign key (parent_id) for tree structure.
    Slugs enable SEO-friendly URLs.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Key: parent_id -> categories.id (SET NULL, self-referential)
        - Indexes: id (primary), parent_id, name, slug (unique)
        
    Data Integrity:
        - Name and slug cannot be empty
        - Slug must be unique across all categories
        - Cannot be own parent (self-parent check)
        - Timestamps: updated_at >= created_at
        
    Relationships:
        - Self-referential: parent/children (tree structure)
        - One-to-many with Product (category has many products)
        
    Tree Structure:
        - Root categories: parent_id = NULL
        - Leaf categories: No children
        - Subtree deletion: CASCADE removes all descendants
        - Example: Electronics -> Computers -> Laptops
        
    Design Notes:
        - slug: URL-safe identifier (e.g., "mens-shoes")
        - metadata: JSON for custom attributes (icon, banner_url, etc.)
        - description: Rich text for category landing pages
        - No depth limit (supports arbitrary nesting)
        - Parent deletion sets children.parent_id to NULL (orphan handling)
        
    Query Patterns:
        - Root categories: parent_id IS NULL
        - Subcategories: parent_id = X
        - Product count: COUNT(products) GROUP BY category_id
        - Breadcrumbs: Recursive CTE traversal up parent chain
        
    SEO Considerations:
        - Slugs used in URLs: /categories/{slug}
        - Name used for display and meta tags
        - Description for category page content
    """
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    category_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' to avoid SQLAlchemy reserved word
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all")
    products = relationship("Product", back_populates="category")
    
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name='check_name_present'),
        CheckConstraint("length(trim(slug)) > 0", name='check_slug_present'),
        CheckConstraint("id != parent_id", name='check_no_self_parent'),
        CheckConstraint("updated_at >= created_at", name='check_updated_after_created'),
    )
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"
