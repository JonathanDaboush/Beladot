from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Subcategory(Base):
    """
    SQLAlchemy ORM model for subcategories table.
    
    Represents second-level product taxonomy under main categories.
    Examples: Under Electronics -> Televisions, Phones, Computers
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Key: category_id -> categories.id (CASCADE)
        - Indexes: id (primary), category_id, name
        
    Data Integrity:
        - Cascade delete when category deleted
        - Name cannot be empty
        - Timestamps: updated_at >= created_at
        
    Relationships:
        - Many-to-one with Category (category has many subcategories)
        - One-to-many with Product (subcategory has many products)
        
    Design Notes:
        - Simpler alternative to recursive category tree
        - Two-level hierarchy: Category -> Subcategory -> Products
        - is_active: Soft delete for seasonal/discontinued categories
    """
    __tablename__ = "subcategories"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory")
    
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name='check_subcategory_name_present'),
        CheckConstraint("updated_at >= created_at", name='check_subcategory_updated_after_created'),
    )
    
    def __repr__(self):
        return f"<Subcategory(id={self.id}, name={self.name}, category_id={self.category_id})>"
