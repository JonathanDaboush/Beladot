from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class ProductImage(Base):
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
        UniqueConstraint('product_id', 'is_primary', name='unique_product_primary', postgresql_where="is_primary = true"),
    )
    
    def __repr__(self):
        return f"<ProductImage(id={self.id}, product_id={self.product_id}, is_primary={self.is_primary})>"
