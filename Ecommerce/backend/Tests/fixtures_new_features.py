"""
Pytest Fixtures for New Features Tests
Provides test data and setup for email, upload, reviews, wishlist, password reset tests
"""
import pytest
from datetime import datetime, timedelta, timezone
import secrets


@pytest.fixture
async def password_reset_token(db_session, test_user):
    """Create a valid password reset token"""
    from Models.PasswordResetToken import PasswordResetToken
    
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    reset_token = PasswordResetToken(
        user_id=test_user["id"],
        token=token,
        expires_at=expires_at,
        is_used=False
    )
    
    db_session.add(reset_token)
    await db_session.commit()
    
    return token


@pytest.fixture
async def test_product_image(db_session, test_product):
    """Create a test product image"""
    from Models.ProductImage import ProductImage
    
    image = ProductImage(
        product_id=test_product["id"],
        image_url="/uploads/products/test_image.jpg",
        thumbnail_url="/uploads/products/thumbnails/test_image.jpg",
        is_primary=True
    )
    
    db_session.add(image)
    await db_session.commit()
    await db_session.refresh(image)
    
    return {
        "id": image.id,
        "product_id": image.product_id,
        "image_url": image.image_url,
        "thumbnail_url": image.thumbnail_url
    }


@pytest.fixture
async def delivered_order(db_session, test_user, test_product):
    """Create a delivered order for testing reviews"""
    from Models.Order import Order, OrderStatus
    from Models.OrderItem import OrderItem
    
    order = Order(
        user_id=test_user["id"],
        status=OrderStatus.DELIVERED,
        total_cents=test_product.get("price_cents", 10000),
        currency="USD"
    )
    
    db_session.add(order)
    await db_session.flush()
    
    order_item = OrderItem(
        order_id=order.id,
        product_id=test_product["id"],
        quantity=1,
        unit_price_cents=test_product.get("price_cents", 10000),
        total_price_cents=test_product.get("price_cents", 10000)
    )
    
    db_session.add(order_item)
    await db_session.commit()
    
    return {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status
    }


@pytest.fixture
async def test_review(db_session, test_user, test_product, delivered_order):
    """Create a test review"""
    from Models.Review import Review
    
    review = Review(
        user_id=test_user["id"],
        product_id=test_product["id"],
        rating=5,
        title="Great product!",
        comment="This is an excellent product. Highly recommend!",
        helpful_count=0
    )
    
    db_session.add(review)
    await db_session.commit()
    await db_session.refresh(review)
    
    return {
        "id": review.id,
        "user_id": review.user_id,
        "product_id": review.product_id,
        "rating": review.rating,
        "title": review.title
    }


@pytest.fixture
async def wishlist_item(db_session, test_user, test_product):
    """Create a single wishlist item"""
    from Models.Wishlist import Wishlist
    from Models.WishlistItem import WishlistItem
    
    # Get or create wishlist
    from sqlalchemy import select
    result = await db_session.execute(
        select(Wishlist).where(Wishlist.user_id == test_user["id"])
    )
    wishlist = result.scalar_one_or_none()
    
    if not wishlist:
        wishlist = Wishlist(user_id=test_user["id"])
        db_session.add(wishlist)
        await db_session.flush()
    
    # Create wishlist item
    item = WishlistItem(
        wishlist_id=wishlist.id,
        product_id=test_product["id"]
    )
    
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    
    return {
        "id": item.id,
        "wishlist_id": item.wishlist_id,
        "product_id": item.product_id
    }


@pytest.fixture
async def wishlist_with_items(db_session, test_user, test_products):
    """Create a wishlist with multiple items"""
    from Models.Wishlist import Wishlist
    from Models.WishlistItem import WishlistItem
    
    # Create wishlist
    wishlist = Wishlist(user_id=test_user["id"])
    db_session.add(wishlist)
    await db_session.flush()
    
    # Add multiple items
    items = []
    for product in test_products[:3]:  # Add first 3 products
        item = WishlistItem(
            wishlist_id=wishlist.id,
            product_id=product["id"]
        )
        db_session.add(item)
        items.append(item)
    
    await db_session.commit()
    
    return {
        "wishlist_id": wishlist.id,
        "item_count": len(items),
        "items": items
    }


@pytest.fixture
async def test_products(db_session, test_seller):
    """Create multiple test products"""
    from Models.Product import Product
    
    products = []
    for i in range(5):
        product = Product(
            seller_id=test_seller["id"],
            name=f"Test Product {i+1}",
            description=f"Description for product {i+1}",
            price_cents=(i+1) * 10000,  # $100, $200, $300, etc.
            currency="USD",
            quantity=10,
            is_active=True
        )
        db_session.add(product)
        products.append(product)
    
    await db_session.commit()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "price_cents": p.price_cents,
            "quantity": p.quantity
        }
        for p in products
    ]


@pytest.fixture
async def test_shipment(db_session, test_user, delivered_order):
    """Create a test shipment"""
    from Models.Shipment import Shipment
    
    shipment = Shipment(
        order_id=delivered_order["id"],
        tracking_number="TRACK123456",
        carrier="UPS",
        status="pending"
    )
    
    db_session.add(shipment)
    await db_session.commit()
    await db_session.refresh(shipment)
    
    return {
        "id": shipment.id,
        "order_id": shipment.order_id,
        "tracking_number": shipment.tracking_number,
        "status": shipment.status
    }


@pytest.fixture
def admin_headers(test_admin_user):
    """Create authorization headers for admin user"""
    from Utilities.auth import create_access_token
    
    token = create_access_token(
        data={"sub": test_admin_user["email"], "role": "admin"}
    )
    
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
async def test_admin_user(db_session):
    """Create a test admin user"""
    from Models.User import User, UserRole
    from Utilities.auth import get_password_hash
    
    admin = User(
        email="admin@test.com",
        first_name="Admin",
        last_name="User",
        hashed_password=get_password_hash("AdminPassword123!"),
        role=UserRole.ADMIN,
        is_active=True
    )
    
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    
    return {
        "id": admin.id,
        "email": admin.email,
        "role": admin.role
    }
