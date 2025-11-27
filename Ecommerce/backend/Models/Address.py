from sqlalchemy import Boolean, CheckConstraint, Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class Address(Base):
    """
    SQLAlchemy ORM model for addresses table.
    
    Stores physical mailing addresses for users with validation constraints.
    Supports one default address per user via unique constraint.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Key: user_id -> users.id (CASCADE delete)
        - Indexes: id (primary)
        
    Data Integrity:
        - Country must be exactly 2 characters (ISO-2 code)
        - Required fields validated as non-empty (address_line1, city, postal_code)
        - One default address per user (unique constraint with filter)
        - Cascading delete when user deleted
        
    Relationships:
        - Many-to-one with User (one user has many addresses)
        
    Design Notes:
        - address_line2 optional for apartments/suites
        - country stored as ISO 3166-1 alpha-2 code (US, CA, GB, etc.)
        - is_default flag with partial unique index (PostgreSQL-specific)
        - State/province stored as string (not standardized)
    """
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
