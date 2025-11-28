from sqlalchemy import Column, Integer, ForeignKey
from database import Base

class ProductOptionCategory(Base):
    __tablename__ = "product_option_categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    option_category_id = Column(Integer, ForeignKey("option_categories.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"<ProductOptionCategory(id={self.id}, product_id={self.product_id}, option_category_id={self.option_category_id})>"
