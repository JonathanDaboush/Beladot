
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from backend.model.base import Base

class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    cart_id = Column(Integer, ForeignKey('cart.id', ondelete='SET NULL'), index=True)
    order_status = Column(String(32), nullable=False)
    total_amount = Column(Float, nullable=False)
    order_number = Column(String(64), unique=True, nullable=False)
    address = Column(String(256))
    postal_code = Column(String(32))
    country = Column(String(64))
    city = Column(String(64))

    # Relationships (example)
    # user = relationship('User', back_populates='orders', lazy='selectin')

    __table_args__ = (
        Index('ix_order_user_id', 'user_id'),
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
