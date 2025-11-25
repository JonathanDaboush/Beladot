from sqlalchemy import Boolean, CheckConstraint, Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)  # ✅ Shortened
    country = Column(String(2), nullable=False)  # ✅ Matches ISO-2 constraint
    postal_code = Column(String(20), nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)  # ✅ Proper boolean
    
    # Relationships
    user = relationship("User", back_populates="addresses")
    
    __table_args__ = (
        CheckConstraint("length(country) = 2", name='check_country_iso2'),
        CheckConstraint("length(trim(postal_code)) > 0", name='check_postal_code_present'),
        CheckConstraint("length(trim(city)) > 0", name='check_city_present'),
        CheckConstraint("length(trim(address_line1)) > 0", name='check_line1_present'),
        UniqueConstraint('user_id', 'is_default', 
                        name='unique_default_per_user',
                        postgresql_where="is_default = true"),
    )
