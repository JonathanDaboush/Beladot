from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    metadata = Column(JSON, nullable=True)
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
