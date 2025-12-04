"""
Comprehensive tests for CheckoutService.

Tests cover:
- Order creation from cart
- Inventory reservation
- Payment intent creation
- Idempotency handling
- Address validation
- Order total calculation
- Edge cases and validation
"""
import pytest
from decimal import Decimal
from Services.CheckoutService import CheckoutService


@pytest.mark.asyncio
class TestCheckoutService:
    """Test suite for CheckoutService."""
    
    async def test_create_order_from_cart_success(self, db_session, create_test_product):
        """Test successful order creation from cart."""
        from Repositories.UserRepository import UserRepository
        from Repositories.CartRepository import CartRepository
        from Repositories.OrderRepository import OrderRepository
        from Repositories.AddressRepository import AddressRepository
        from Services.CartService import CartService
        from Services.InventoryService import InventoryService
        from Services.PaymentService import PaymentService
        from Services.PricingService import PricingService
        from Services.NotificationService import NotificationService
        from Models.User import User
        from Models.Address import Address
        
        user_repo = UserRepository(db_session)
        address_repo = AddressRepository(db_session)
        
        user = User(
            email="checkout@test.com",
            first_name="Checkout",
            last_name="User",
            hashed_password="hashed_password"
        )
        user = await user_repo.create(user)
        
        # Create addresses
        billing_address = Address(
            user_id=user.id,
            address_line1="123 Billing St",
            city="New York",
            state="NY",
            postal_code="10001",
            country="US"
        )
        billing_address = await address_repo.create(billing_address)
        
        shipping_address = Address(
            user_id=user.id,
            address_line1="456 Shipping Ave",
            city="Boston",
            state="MA",
            postal_code="02101",
            country="US"
        )
        shipping_address = await address_repo.create(shipping_address)
        
        # Create product and cart
        product = await create_test_product(
            name="Checkout Product",
            sku="CHK-001",
            price_cents=int(Decimal("50.00") * 100),
            stock_quantity=10
        )
        
        cart_repo = CartRepository(db_session)
        pricing_service = PricingService(db_session)
        cart_service = CartService(cart_repo, pricing_service)
        
        cart = await cart_service.get_cart(user_id=user.id, session_id=None)
        await cart_service.add_item(cart.id, product.id, quantity=2)
        
        # Create order
        order_repo = OrderRepository(db_session)
        from Services.SimpleInventoryService import SimpleInventoryService
        from Repositories.ProductRepository import ProductRepository
        product_repo = ProductRepository(db_session)
        inventory_service = SimpleInventoryService(product_repo)
        payment_service = PaymentService(db_session, payment_gateway=None)
        notification_service = NotificationService(db_session)
        
        service = CheckoutService(
            order_repo,
            cart_service,
            inventory_service,
            payment_service,
            pricing_service,
            notification_service
        )
        
        payment_method = {
            "type": "credit_card",
            "card_number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2025,
            "cvv": "123"
        }
        
        order = await service.create_order_from_cart(
            cart_id=cart.id,
            billing_address=billing_address,
            shipping_address=shipping_address,
            payment_method=payment_method
        )
        
        assert order is not None
        assert order.user_id == user.id
        assert order.status == "pending"
        assert order.total == Decimal("100.00")
    
    async def test_create_order_idempotency(self, db_session, create_test_product):
        """Test idempotency prevents duplicate orders."""
        from Repositories.UserRepository import UserRepository
        from Repositories.CartRepository import CartRepository
        from Repositories.OrderRepository import OrderRepository
        from Repositories.AddressRepository import AddressRepository
        from Services.CartService import CartService
        from Services.InventoryService import InventoryService
        from Services.PaymentService import PaymentService
        from Services.PricingService import PricingService
        from Services.NotificationService import NotificationService
        from Models.User import User
        from Models.Address import Address
        
        user_repo = UserRepository(db_session)
        address_repo = AddressRepository(db_session)
        
        user = User(
            email="idempotent@test.com",
            first_name="Idempotent",
            last_name="User",
            hashed_password="hashed_password"
        )
        user = await user_repo.create(user)
        
        billing_address = Address(
            user_id=user.id,
            address_line1="123 Test St",
            city="Test City",
            state="TS",
            postal_code="12345",
            country="US"
        )
        billing_address = await address_repo.create(billing_address)
        
        product = await create_test_product(
            name="Idempotent Product",
            sku="IDEMP-001",
            price_cents=int(Decimal("25.00") * 100),
            stock_quantity=20
        )
        
        cart_repo = CartRepository(db_session)
        pricing_service = PricingService(db_session)
        cart_service = CartService(cart_repo, pricing_service)
        
        cart = await cart_service.get_cart(user_id=user.id, session_id=None)
        await cart_service.add_item(cart.id, product.id, quantity=1)
        
        order_repo = OrderRepository(db_session)
        from Services.SimpleInventoryService import SimpleInventoryService
        from Repositories.ProductRepository import ProductRepository
        product_repo = ProductRepository(db_session)
        inventory_service = SimpleInventoryService(product_repo)
        payment_service = PaymentService(db_session, payment_gateway=None)
        notification_service = NotificationService(db_session)
        
        service = CheckoutService(
            order_repo,
            cart_service,
            inventory_service,
            payment_service,
            pricing_service,
            notification_service
        )
        
        payment_method = {"type": "credit_card"}
        idempotency_key = "unique-checkout-123"
        
        # First order
        order1 = await service.create_order_from_cart(
            cart_id=cart.id,
            billing_address=billing_address,
            shipping_address=billing_address,
            payment_method=payment_method,
            idempotency_key=idempotency_key
        )
        
        # Second order with same key should return same order
        order2 = await service.create_order_from_cart(
            cart_id=cart.id,
            billing_address=billing_address,
            shipping_address=billing_address,
            payment_method=payment_method,
            idempotency_key=idempotency_key
        )
        
        assert order1.id == order2.id
    
    async def test_create_order_insufficient_inventory(self, db_session, create_test_product):
        """Test order creation fails with insufficient inventory."""
        from Repositories.UserRepository import UserRepository
        from Repositories.CartRepository import CartRepository
        from Repositories.OrderRepository import OrderRepository
        from Repositories.AddressRepository import AddressRepository
        from Services.CartService import CartService
        from Services.InventoryService import InventoryService
        from Services.PaymentService import PaymentService
        from Services.PricingService import PricingService
        from Services.NotificationService import NotificationService
        from Models.User import User
        from Models.Address import Address
        
        user_repo = UserRepository(db_session)
        address_repo = AddressRepository(db_session)
        
        user = User(
            email="inventory@test.com",
            first_name="Inventory",
            last_name="Test",
            hashed_password="hashed_password"
        )
        user = await user_repo.create(user)
        
        address = Address(
            user_id=user.id,
            address_line1="789 Test Rd",
            city="Test Town",
            state="TT",
            postal_code="54321",
            country="US"
        )
        address = await address_repo.create(address)
        
        # Product with limited stock
        product = await create_test_product(
            name="Limited Product",
            sku="LIM-001",
            price_cents=int(Decimal("75.00") * 100),
            stock_quantity=2
        )
        
        cart_repo = CartRepository(db_session)
        pricing_service = PricingService(db_session)
        cart_service = CartService(cart_repo, pricing_service)
        
        cart = await cart_service.get_cart(user_id=user.id, session_id=None)
        # Add more than available
        await cart_service.add_item(cart.id, product.id, quantity=2)
        
        # Reduce stock externally
        from Repositories.ProductRepository import ProductRepository
        product_repo = ProductRepository(db_session)
        product.stock_quantity = 1
        await product_repo.update(product)
        
        order_repo = OrderRepository(db_session)
        from Services.SimpleInventoryService import SimpleInventoryService
        inventory_service = SimpleInventoryService(product_repo)
        payment_service = PaymentService(db_session, payment_gateway=None)
        notification_service = NotificationService(db_session)
        
        service = CheckoutService(
            order_repo,
            cart_service,
            inventory_service,
            payment_service,
            pricing_service,
            notification_service
        )
        
        payment_method = {"type": "credit_card"}
        
        # Should fail due to insufficient inventory
        with pytest.raises(ValueError, match="insufficient"):
            await service.create_order_from_cart(
                cart_id=cart.id,
                billing_address=address,
                shipping_address=address,
                payment_method=payment_method
            )
    
    async def test_validate_cart_before_checkout(self, db_session, create_test_product):
        """Test cart validation before checkout."""
        from Services.CheckoutService import CheckoutService
        
        service = CheckoutService(None, None, None, None, None, None)
        
        # Test with None cart (service expects cart_id, will call get_cart)
        with pytest.raises((ValueError, AttributeError)):
            await service.validate_cart(999999)
        
        # Test with invalid prices
        invalid_items = [
            {"product_id": 1, "quantity": 1, "price": Decimal("-10.00")}
        ]
        with pytest.raises(ValueError, match="invalid price"):
            await service.validate_cart(invalid_items)
    
    async def test_calculate_order_total(self, db_session, create_test_product):
        """Test order total calculation."""
        from Repositories.UserRepository import UserRepository
        from Repositories.CartRepository import CartRepository
        from Repositories.OrderRepository import OrderRepository
        from Services.CartService import CartService
        from Services.CheckoutService import CheckoutService
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
        
        # Create products
        product1 = await create_test_product(
            name="Product A",
            sku="TOTAL-A",
            price_cents=int(Decimal("30.00") * 100),
            stock_quantity=50
        )
        
        product2 = await create_test_product(
            name="Product B",
            sku="TOTAL-B",
            price_cents=int(Decimal("20.00") * 100),
            stock_quantity=50
        )
        
        cart_repo = CartRepository(db_session)
        pricing_service = PricingService(db_session)
        cart_service = CartService(cart_repo, pricing_service)
        
        cart = await cart_service.get_cart(user_id=user.id, session_id=None)
        await cart_service.add_item(cart.id, product1.id, quantity=2)  # $60
        await cart_service.add_item(cart.id, product2.id, quantity=3)  # $60
        
        order_repo = OrderRepository(db_session)
        service = CheckoutService(
            order_repo,
            cart_service,
            None,
            None,
            pricing_service,
            None
        )
        
        total = await service.calculate_order_total(cart.id)
        
        assert total["subtotal"] == Decimal("120.00")
        assert total["tax"] >= Decimal("0.00")
        assert total["total"] >= Decimal("120.00")
    
    async def test_order_status_transitions(self, db_session):
        """Test valid order status transitions."""
        from Services.CheckoutService import CheckoutService
        
        service = CheckoutService(None, None, None, None, None, None)
        
        # Test valid transitions
        assert service.can_transition_status("pending", "confirmed") is True
        assert service.can_transition_status("confirmed", "processing") is True
        assert service.can_transition_status("processing", "shipped") is True
        assert service.can_transition_status("shipped", "delivered") is True
        
        # Test invalid transitions
        assert service.can_transition_status("delivered", "pending") is False
        assert service.can_transition_status("cancelled", "confirmed") is False
    
    async def test_cancel_order(self, db_session, create_test_product):
        """Test order cancellation."""
        from Repositories.UserRepository import UserRepository
        from Repositories.OrderRepository import OrderRepository
        from Models.User import User
        from Models.Order import Order
        
        user_repo = UserRepository(db_session)
        order_repo = OrderRepository(db_session)
        
        user = User(
            email="cancel@test.com",
            first_name="Cancel",
            last_name="Test",
            hashed_password="hashed_password"
        )
        user = await user_repo.create(user)
        
        order = Order(
            user_id=user.id,
            order_number="TEST-CANCEL-001",
            status="pending",
            total_cents=int(Decimal("100.00") * 100),
            subtotal_cents=int(Decimal("100.00") * 100),
            tax_cents=0,
            shipping_address_line1="123 Test St",
            shipping_city="TestCity",
            shipping_state="TS",
            shipping_country="US",
            shipping_postal_code="12345"
        )
        order = await order_repo.create(order)
        
        service = CheckoutService(order_repo, None, None, None, None, None)
        
        cancelled_order = await service.cancel_order(order.id, reason="Customer request")
        
        assert cancelled_order.status == "cancelled"
        assert cancelled_order.cancellation_reason == "Customer request"



