

from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, Index
from sqlalchemy.orm import relationship
from backend.model.base import Base
from backend.model.enums import UserAccountStatus
import datetime

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    full_name = Column(String(128), nullable=False)
    dob = Column(DateTime, nullable=False)
    password = Column(String(256), nullable=False)
    phone_number = Column(String(32), nullable=False)
    email = Column(String(128), nullable=False, unique=True, index=True)
    img_location = Column(String(256))
    account_status = Column(Enum(UserAccountStatus), default=UserAccountStatus.ACTIVE, nullable=False)

    # Relationships (example)
    # orders = relationship('Order', back_populates='user', lazy='selectin')

    __table_args__ = (
        Index('ix_user_email', 'email'),
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name != 'password'}
