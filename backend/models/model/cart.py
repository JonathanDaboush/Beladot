
from sqlalchemy import Column, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.model.base import Base

class Cart(Base):
    __tablename__ = 'cart'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)

    # Relationships (example)
    # user = relationship('User', back_populates='cart', lazy='selectin')

    __table_args__ = (
        Index('ix_cart_user_id', 'user_id'),
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
