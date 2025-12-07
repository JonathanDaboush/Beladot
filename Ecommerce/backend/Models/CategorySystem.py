from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base


class MainCategory(Base):
    """
    Main product categorization (e.g., Electronics, Clothing, Home & Garden).
    Used for catalog organization and filtering.
    
    Relationships:
    - One-to-many with Product (products.main_category_id)
    - One-to-many with MainSubcategory (subcategories)
    
    Example:
    MainCategory: "Electronics"
    ├── MainSubcategory: "Television"
    ├── MainSubcategory: "Audio"
    └── MainSubcategory: "Cameras"
    """
    __tablename__ = "main_categories"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    subcategories = relationship("MainSubcategory", back_populates="main_category", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="main_category")
    
    def __repr__(self):
        return f"<MainCategory(id={self.id}, name={self.name})>"


class MainSubcategory(Base):
    """
    Subcategories under main categories (e.g., Television under Electronics).
    
    Relationships:
    - Many-to-one with MainCategory
    - One-to-many with Product (products can belong to a specific subcategory)
    
    Example:
    MainCategory: "Electronics" → MainSubcategory: "Television"
    MainCategory: "Clothing" → MainSubcategory: "Shirts"
    """
    __tablename__ = "main_subcategories"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    main_category_id = Column(Integer, ForeignKey("main_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    main_category = relationship("MainCategory", back_populates="subcategories")
    products = relationship("Product", back_populates="main_subcategory")
    
    def __repr__(self):
        return f"<MainSubcategory(id={self.id}, name={self.name}, main_category_id={self.main_category_id})>"


class VariantCategory(Base):
    """
    Variant-specific categorization for product variations (optional).
    Used by sellers to organize their product variants (e.g., T-shirt colors, sizes).
    
    Relationships:
    - One-to-many with VariantSubcategory
    - One-to-many with ProductVariant (variants can be tagged with these categories)
    
    Example:
    VariantCategory: "T-Shirt Colors"
    ├── VariantSubcategory: "Green"
    ├── VariantSubcategory: "Blue"
    └── VariantSubcategory: "Red"
    
    VariantCategory: "Sizes"
    ├── VariantSubcategory: "Small"
    ├── VariantSubcategory: "Medium"
    └── VariantSubcategory: "Large"
    """
    __tablename__ = "variant_categories"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    seller_id = Column(Integer, ForeignKey("sellers.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    seller = relationship("Seller", back_populates="variant_categories")
    subcategories = relationship("VariantSubcategory", back_populates="variant_category", cascade="all, delete-orphan")
    variants = relationship("ProductVariant", back_populates="variant_category")
    
    def __repr__(self):
        return f"<VariantCategory(id={self.id}, name={self.name}, seller_id={self.seller_id})>"


class VariantSubcategory(Base):
    """
    Subcategories for variant categorization (e.g., "Green" under "T-Shirt Colors").
    
    Relationships:
    - Many-to-one with VariantCategory
    - One-to-many with ProductVariant
    
    Example:
    VariantCategory: "T-Shirt Colors" → VariantSubcategory: "Green"
    VariantCategory: "Sizes" → VariantSubcategory: "Medium"
    """
    __tablename__ = "variant_subcategories"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    variant_category_id = Column(Integer, ForeignKey("variant_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    variant_category = relationship("VariantCategory", back_populates="subcategories")
    variants = relationship("ProductVariant", back_populates="variant_subcategory")
    
    def __repr__(self):
        return f"<VariantSubcategory(id={self.id}, name={self.name}, variant_category_id={self.variant_category_id})>"
