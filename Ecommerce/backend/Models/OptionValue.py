from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class OptionValue(Base):
    __tablename__ = "option_values"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("option_categories.id", ondelete="CASCADE"), nullable=False)
    value = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<OptionValue(id={self.id}, category_id={self.category_id}, value={self.value})>"
