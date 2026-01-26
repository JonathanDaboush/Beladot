"""
Script to create all tables without foreign keys for divina_dev database.
"""
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Text, Numeric, Boolean, DateTime, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    dob = Column(Date)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(20))
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(Date)
    img_location = Column(String(255))
    account_status = Column(String(5), nullable=False, default='True')

class Category(Base):
    __tablename__ = 'category'
    category_id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    image_url = Column(String(255), nullable=True)

class Subcategory(Base):
    __tablename__ = 'subcategory'
    subcategory_id = Column(BigInteger, primary_key=True)
    category_id = Column(BigInteger)  # FK added later
    name = Column(String(100), nullable=False)
    image_url = Column(String(255), nullable=True)

class Product(Base):
    __tablename__ = 'product'
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(BigInteger)
    category_id = Column(BigInteger)
    subcategory_id = Column(BigInteger)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10,2))
    currency = Column(String(10))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Cart(Base):
    __tablename__ = 'cart'
    cart_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class CartItem(Base):
    __tablename__ = 'cart_item'
    cart_item_id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(BigInteger)
    product_id = Column(BigInteger)
    variant_id = Column(BigInteger)
    quantity = Column(Integer)

class Wishlist(Base):
    __tablename__ = 'wishlist'
    wishlist_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class WishlistItem(Base):
    __tablename__ = 'wishlist_item'
    wishlist_item_id = Column(BigInteger, primary_key=True)
    wishlist_id = Column(BigInteger)
    product_id = Column(BigInteger)
    variant_id = Column(BigInteger)
    quantity = Column(Integer)
    user_id = Column(BigInteger)

# Add more tables as needed from your persistance directory

def main():
    engine = create_engine('postgresql+psycopg2://postgres:password@localhost:5432/divina_dev')
    Base.metadata.create_all(engine)
    print('Tables created without foreign keys.')

if __name__ == '__main__':
    main()
