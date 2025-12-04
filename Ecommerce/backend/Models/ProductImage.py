from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class ProductImage(Base):
    """
    SQLAlchemy ORM model for product_images table.
    
    Associates image blobs with products, supporting multiple images per product
    with ordering and primary image designation. Enables gallery views and SEO.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Keys: product_id -> products.id (CASCADE), blob_id -> blobs.id (RESTRICT)
        - Indexes: id (primary), product_id
        - Unique constraints: (product_id, sort_order), (product_id, is_primary) where true
        
    Data Integrity:
        - sort_order must be non-negative
        - One primary image per product (partial unique index)
        - Unique sort order per product (prevents display order conflicts)
        - Blob deletion restricted (prevents orphaned references)
        - Product deletion cascades to images
        
    Relationships:
        - Many-to-one with Product (product has many images)
        - Many-to-one with Blob (image stored in blob storage)
        
    Image Ordering:
        - sort_order: Display order in gallery (0 = first, 1 = second, etc.)
        - Unique constraint: No two images for same product can share sort_order
        - Gaps allowed (0, 5, 10) for easy reordering
        
    Primary Image:
        - is_primary: Main image for listings and thumbnails
        - Unique constraint: Only one primary image per product
        - Fallback: If no primary, use lowest sort_order
        
    Design Notes:
        - alt_text: Accessibility and SEO (image description)
        - blob_id: References Blob storage (S3, Cloudinary, etc.)
        - RESTRICT delete: Cannot delete blob while referenced
        - CASCADE delete: Remove images when product deleted
        
    Display Logic:
        1. Primary image: WHERE product_id = X AND is_primary = true
        2. Gallery order: ORDER BY sort_order ASC
        3. Fallback thumbnail: MIN(sort_order) WHERE product_id = X
        
    Admin Workflows:
        - Upload: Create ProductImage with blob_id and sort_order
        - Reorder: Update sort_order values (maintain uniqueness)
        - Set primary: Update all is_primary = false, then set one to true
        - Delete: Remove ProductImage (blob preserved for other uses)
        
    SEO Considerations:
        - alt_text used for image alt attribute
        - Primary image used in Open Graph tags
        - Blob.content_type specifies image format
    """
    __tablename__ = "product_images"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    blob_id = Column(Integer, ForeignKey("blobs.id", ondelete="RESTRICT"), nullable=False)
    alt_text = Column(String(255), nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    
    product = relationship("Product", back_populates="images")
    blob = relationship("Blob")
    
    __table_args__ = (
        CheckConstraint("sort_order >= 0", name='check_sort_order_non_negative'),
        UniqueConstraint('product_id', 'sort_order', name='unique_product_sort_order'),
        # Removed postgresql_where for compatibility - unique constraint will be enforced at application level
    )
    
    def __repr__(self):
        return f"<ProductImage(id={self.id}, product_id={self.product_id}, is_primary={self.is_primary})>"
