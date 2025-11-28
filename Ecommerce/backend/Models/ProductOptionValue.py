from sqlalchemy import Column, Integer, ForeignKey
from database import Base

class ProductOptionValue(Base):
    __tablename__ = "product_option_values"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    option_value_id = Column(Integer, ForeignKey("option_values.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"<ProductOptionValue(id={self.id}, product_id={self.product_id}, option_value_id={self.option_value_id})>"
