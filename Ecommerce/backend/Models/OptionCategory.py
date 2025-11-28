from sqlalchemy import Column, Integer, String
from database import Base

class OptionCategory(Base):
    __tablename__ = "option_categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<OptionCategory(id={self.id}, name={self.name})>"
