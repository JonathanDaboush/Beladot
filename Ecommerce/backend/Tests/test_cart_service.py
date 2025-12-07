"""
Comprehensive tests for CartService.

Tests cover:
- Cart creation
- Item addition and removal
- Quantity updates
- Guest-to-user cart merging
- Cart total calculations
- Coupon application
- Edge cases and validation
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from Services.CartService import CartService


@pytest.mark.asyncio
class TestCartService:
    """Test suite for CartService."""
    
    async def test_create_cart_for_user(self, db_session, create_test_employee):
        """Test creating a cart for logged-in user."""
        from Repositories.UserRepository import UserRepository
        from Repositories.CartRepository import CartRepository
        from Services.PricingService import PricingService
        from Models.User import User
        
        user_repo = UserRepository(db_session)
        user = User(
            email="user@test.com",
            first_name="Test",
            last_name="User",
            hashed_password="hashed_password"
        )
        user = await user_repo.create(user)
        
        cart_repo = CartRepository(db_session)
        from unittest.mock import MagicMock
        pricing_service = PricingService(MagicMock(), MagicMock())
        
        service = CartService(cart_repo, pricing_service)
        cart = await service.get_cart(user_id=user.id, session_id=None)
        
        assert cart is not None
        assert cart.user_id == user.id
    
    async def test_add_item_to_cart(self, db_session, create_test_product):
        """Test adding a product to cart."""
        from Repositories.UserRepository import UserRepository
        from Repositories.CartRepository import CartRepository
        from Repositories.CartItemRepository import CartItemRepository
        from Services.PricingService import PricingService
        from Models.User import User
        
        user_repo = UserRepository(db_session)
        user = User(
            email="shopper@test.com",
            first_name="Shopper",
            last_name="Test",
            hashed_password="hashed_password"
        )
        user = await user_repo.create(user)
        
        product = await create_test_product(
            name="Test Product",
            sku="CART-001",
            price_cents=int(Decimal("29.99") * 100),
            stock_quantity=100
        )
        
        cart_repo = CartRepository(db_session)
        cart_item_repo = CartItemRepository(db_session)
        pricing_service = PricingService(None, None)
        
        service = CartService(cart_repo, pricing_service)
        cart = await service.get_cart(user_id=user.id, session_id=None)
        
        # Add item
        cart_item = await service.add_item(cart.id, product.id, quantity=2)

        assert cart_item is not None
        assert cart_item.product_id == product.id
        assert cart_item.quantity == 2
        assert cart_item.unit_price_cents == product.price_cents

    async def test_add_item_insufficient_stock(self, db_session, create_test_product):
        """Test adding more items than available stock."""
        from Repositories.UserRepository import UserRepository
        from Repositories.CartRepository import CartRepository
        from Services.PricingService import PricingService
        from Models.User import User
        
        user_repo = UserRepository(db_session)
        user = User(
            email="buyer@test.com",
            first_name="Buyer",
            last_name="Test",
            hashed_password="hashed_password"
        )
        user = await user_repo.create(user)
        
        product = await create_test_product(
            name="Limited Stock",
            sku="CART-002",
            price_cents=int(Decimal("49.99") * 100),
            stock_quantity=3
        )
        
        cart_repo = CartRepository(db_session)
        pricing_service = PricingService(None, None)
        
        service = CartService(cart_repo, pricing_service)
        cart = await service.get_cart(user_id=user.id, session_id=None)
        
        # Attempt to add more than available
        with pytest.raises(ValueError, match="Insufficient stock"):
            await service.add_item(cart.id, product.id, quantity=10)
    
    async def test_update_cart_item_quantity(self, db_session, create_test_product):
        """Test updating cart item quantity."""
        from Repositories.UserRepository import UserRepository
        from Repositories.CartRepository import CartRepository
        from Services.PricingService import PricingService
        from Models.User import User
        
        user_repo = UserRepository(db_session)
        user = User(
            email="customer@test.com",
            first_name="Customer",
            last_name="Test",
            hashed_password="hashed_password"
        )
        user = await user_repo.create(user)
        
        product = await create_test_product(
            name="Update Quantity Product",
            sku="CART-003",
            price_cents=int(Decimal("19.99") * 100),
            stock_quantity=50
        )
        
        cart_repo = CartRepository(db_session)
        pricing_service = PricingService(None, None)
        
        service = CartService(cart_repo, pricing_service)
        cart = await service.get_cart(user_id=user.id, session_id=None)
        
        # Add item
        cart_item = await service.add_item(cart.id, product.id, quantity=2)
        
        # Update quantity
        updated_item = await service.update_item_quantity(cart_item.id, quantity=5)
        
        assert updated_item.quantity == 5
    
    async def test_remove_item_from_cart(self, db_session, create_test_product):
        """Test removing an item from cart."""
        from Repositories.UserRepository import UserRepository
        from Repositories.CartRepository import CartRepository
        from Services.PricingService import PricingService
        from Models.User import User
        
        user_repo = UserRepository(db_session)
        user = User(
            email="remove@test.com",
            first_name="Remove",
            last_name="Test",
            hashed_password="hashed_password"
        )
        user = await user_repo.create(user)
        
        product = await create_test_product(
            name="Remove Product",
            sku="CART-004",
            price_cents=int(Decimal("39.99") * 100),
            stock_quantity=20
        )
        
        cart_repo = CartRepository(db_session)
        pricing_service = PricingService(None, None)
        
        service = CartService(cart_repo, pricing_service)
        cart = await service.get_cart(user_id=user.id, session_id=None)
        
        # Add and remove item
        cart_item = await service.add_item(cart.id, product.id, quantity=3)
        success = await service.remove_item(cart.id, product.id)
        
        assert success is True
        
        # Verify item removed
        from Repositories.CartItemRepository import CartItemRepository
        cart_item_repo = CartItemRepository(db_session)
        removed_item = await cart_item_repo.get_by_id(cart_item.id)
        assert removed_item is None
    
    async def test_calculate_cart_total(self, db_session, create_test_product):
        """Test calculating cart total."""
        from Repositories.UserRepository import UserRepository
        from Repositories.CartRepository import CartRepository
        from Services.PricingService import PricingService
        from Models.User import User
        
        user_repo = UserRepository(db_session)
        user = User(
            email="total@test.com",
            first_name="Total",
            last_name="Test",
            hashed_password="hashed_password"
        )
        user = await user_repo.create(user)
        
        # Create multiple products
        product1 = await create_test_product(
            name="Product 1",
            sku="TOTAL-001",
            price_cents=int(Decimal("10.00") * 100),
            stock_quantity=100
        )
        
        product2 = await create_test_product(
            name="Product 2",
            sku="TOTAL-002",
            price_cents=int(Decimal("25.00") * 100),
            stock_quantity=100
        )
        
        cart_repo = CartRepository(db_session)
        pricing_service = PricingService(None, None)
        
        service = CartService(cart_repo, pricing_service)
        cart = await service.get_cart(user_id=user.id, session_id=None)
        
        # Add items
        await service.add_item(cart.id, product1.id, quantity=2)  # $20
        await service.add_item(cart.id, product2.id, quantity=3)  # $75
        
        # Calculate total
        total = await service.calculate_total(cart.id)
        
        assert total["subtotal"] == Decimal("95.00")
        assert total["total"] >= Decimal("95.00")
    
    async def test_clear_cart(self, db_session, create_test_product):
        """Test clearing all items from cart."""
        from Repositories.UserRepository import UserRepository
        from Repositories.CartRepository import CartRepository
        from Services.PricingService import PricingService
        from Models.User import User
        
        user_repo = UserRepository(db_session)
        user = User(
            email="clear@test.com",
            first_name="Clear",
            last_name="Test",
            hashed_password="hashed_password"
        )
        user = await user_repo.create(user)
        
        product = await create_test_product(
            name="Clear Product",
            sku="CLEAR-001",
            price_cents=int(Decimal("15.00") * 100),
            stock_quantity=100
        )
        
        cart_repo = CartRepository(db_session)
        pricing_service = PricingService(None, None)
        
        service = CartService(cart_repo, pricing_service)
        cart = await service.get_cart(user_id=user.id, session_id=None)
        
        # Add items
        await service.add_item(cart.id, product.id, quantity=5)
        
        # Clear cart
        success = await service.clear_cart(cart.id)
        
        assert success is True
        
        # Verify cart empty
        cart_items = await cart_repo.get_cart_items(cart.id)
        assert len(cart_items) == 0
    
    async def test_merge_guest_cart_to_user_cart(self, db_session, create_test_product):
        """Test merging guest cart into user cart on login."""
        from Repositories.UserRepository import UserRepository
        from Repositories.SessionRepository import SessionRepository
        from Repositories.CartRepository import CartRepository
        from Services.PricingService import PricingService
        from Models.User import User
        from Models.Session import Session
        
        user_repo = UserRepository(db_session)
        session_repo = SessionRepository(db_session)
        
        user = User(
            email="merge@test.com",
            first_name="Merge",
            last_name="Test",
            hashed_password="hashed_password"
        )
        user = await user_repo.create(user)
        
        # Create guest session
        from datetime import datetime, timedelta
        session = Session(
            session_token="guest_session_123",
            user_id=None,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        session = await session_repo.create(session)
        
        product1 = await create_test_product(
            name="Guest Product",
            sku="MERGE-001",
            price_cents=int(Decimal("20.00") * 100),
            stock_quantity=100
        )
        
        product2 = await create_test_product(
            name="User Product",
            sku="MERGE-002",
            price_cents=int(Decimal("30.00") * 100),
            stock_quantity=100
        )
        
        cart_repo = CartRepository(db_session)
        pricing_service = PricingService(None, None)
        
        service = CartService(cart_repo, pricing_service)
        
        # Create guest cart
        guest_cart = await service.get_cart(user_id=None, session_id=session.id)
        await service.add_item(guest_cart.id, product1.id, quantity=2)
        
        # Create user cart
        user_cart = await service.get_cart(user_id=user.id, session_id=None)
        await service.add_item(user_cart.id, product2.id, quantity=1)
        
        # Merge carts
        merged_cart = await service.merge_carts(guest_cart.id, user_cart.id)
        
        # Verify merged cart has items from both
        cart_items = await cart_repo.get_cart_items(merged_cart.id)
        assert len(cart_items) == 2
    
    async def test_apply_coupon_to_cart(self, db_session, create_test_product):
        """Test applying a coupon code to cart."""
        from Repositories.UserRepository import UserRepository
        from Repositories.CartRepository import CartRepository
        from Repositories.CouponRepository import CouponRepository
        from Services.PricingService import PricingService
        from Models.User import User
        from Models.Coupon import Coupon
        from datetime import date, timedelta
        
        user_repo = UserRepository(db_session)
        coupon_repo = CouponRepository(db_session)
        
        user = User(
            email="coupon@test.com",
            first_name="Coupon",
            last_name="Test",
            hashed_password="hashed_password"
        )
        user = await user_repo.create(user)
        
        # Create coupon
        coupon = Coupon(
            code="SAVE10",
            discount_type="percentage",
            discount_value_cents=int(Decimal("10.00") * 100),
            starts_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=30),
            usage_limit=100,
            usage_count=0
        )
        coupon = await coupon_repo.create(coupon)
        
        product = await create_test_product(
            name="Coupon Product",
            sku="COUPON-001",
            price_cents=int(Decimal("100.00") * 100),
            stock_quantity=50
        )
        
        cart_repo = CartRepository(db_session)
        pricing_service = PricingService(None, None)
        
        service = CartService(cart_repo, pricing_service)
        cart = await service.get_cart(user_id=user.id, session_id=None)
        
        # Add item and apply coupon
        await service.add_item(cart.id, product.id, quantity=1)
        updated_cart = await service.apply_coupon(cart.id, "SAVE10")

        assert updated_cart is not None
        assert updated_cart.id == cart.id        # Verify discount applied
        total = await service.calculate_total(cart.id)
        assert total["discount"] == Decimal("10.00")
        assert total["total"] == Decimal("90.00")
    
    async def test_get_cart_item_count(self, db_session, create_test_product):
        """Test getting total item count in cart."""
        from Repositories.UserRepository import UserRepository
        from Repositories.CartRepository import CartRepository
        from Services.PricingService import PricingService
        from Models.User import User
        
        user_repo = UserRepository(db_session)
        user = User(
            email="count@test.com",
            first_name="Count",
            last_name="Test",
            hashed_password="hashed_password"
        )
        user = await user_repo.create(user)
        
        product = await create_test_product(
            name="Count Product",
            sku="COUNT-001",
            price_cents=int(Decimal("5.00") * 100),
            stock_quantity=200
        )
        
        cart_repo = CartRepository(db_session)
        pricing_service = PricingService(None, None)
        
        service = CartService(cart_repo, pricing_service)
        cart = await service.get_cart(user_id=user.id, session_id=None)
        
        # Add items
        await service.add_item(cart.id, product.id, quantity=10)
        
        # Get count
        count = await service.get_item_count(cart.id)
        
        assert count == 10







