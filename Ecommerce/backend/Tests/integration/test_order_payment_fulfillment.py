"""
Integration tests for Order, Payment, and Fulfillment endpoints
Tests full API request/response cycles with authentication and database
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from datetime import datetime
from decimal import Decimal

pytestmark = pytest.mark.asyncio


class TestOrderEndpointsIntegration:
    """Integration tests for order management endpoints"""
    
    @pytest_asyncio.fixture
    async def authenticated_customer(self, async_client: AsyncClient):
        """Create and authenticate a customer user"""
        # Register customer
        register_data = {
            "email": "customer@test.com",
            "password": "TestPass123!",
            "first_name": "John",
            "last_name": "Customer",
            "role": "CUSTOMER"
        }
        await async_client.post("/api/auth/register", json=register_data)
        
        # Login
        login_response = await async_client.post(
            "/api/auth/login",
            data={"username": "customer@test.com", "password": "TestPass123!"}
        )
        token = login_response.json()["access_token"]
        return {"token": token, "email": "customer@test.com"}
    
    @pytest_asyncio.fixture
    async def test_order(self, async_client: AsyncClient, authenticated_customer):
        """Create a test order"""
        headers = {"Authorization": f"Bearer {authenticated_customer['token']}"}
        
        # Create product first
        seller_data = {
            "email": "seller@test.com",
            "password": "TestPass123!",
            "first_name": "Jane",
            "last_name": "Seller",
            "role": "SELLER"
        }
        await async_client.post("/api/auth/register", json=seller_data)
        seller_login = await async_client.post(
            "/api/auth/login",
            data={"username": "seller@test.com", "password": "TestPass123!"}
        )
        seller_token = seller_login.json()["access_token"]
        
        product_data = {
            "name": "Test Product",
            "description": "Test Description",
            "price_cents": 5000,
            "category_id": "test-category",
            "stock_quantity": 10
        }
        product_response = await async_client.post(
            "/api/products",
            json=product_data,
            headers={"Authorization": f"Bearer {seller_token}"}
        )
        product = product_response.json()
        
        # Add to cart
        cart_data = {"product_id": product["id"], "quantity": 2}
        await async_client.post("/api/cart/items", json=cart_data, headers=headers)
        
        # Create order
        order_data = {
            "shipping_address": {
                "line1": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "postal_code": "12345",
                "country": "US"
            },
            "billing_address": {
                "line1": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "postal_code": "12345",
                "country": "US"
            }
        }
        order_response = await async_client.post(
            "/api/orders",
            json=order_data,
            headers=headers
        )
        
        return {
            "order": order_response.json(),
            "customer_token": authenticated_customer["token"],
            "seller_token": seller_token
        }
    
    async def test_create_order_success(self, async_client: AsyncClient, authenticated_customer):
        """Test successful order creation"""
        headers = {"Authorization": f"Bearer {authenticated_customer['token']}"}
        
        order_data = {
            "shipping_address": {
                "line1": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "postal_code": "12345",
                "country": "US"
            },
            "billing_address": {
                "line1": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "postal_code": "12345",
                "country": "US"
            }
        }
        
        response = await async_client.post(
            "/api/orders",
            json=order_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "PENDING"
        assert "id" in data
        assert "total_cents" in data
    
    async def test_list_orders(self, async_client: AsyncClient, test_order):
        """Test listing user's orders"""
        headers = {"Authorization": f"Bearer {test_order['customer_token']}"}
        
        response = await async_client.get("/api/orders", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["orders"]) > 0
        assert any(order["id"] == test_order["order"]["id"] for order in data["orders"])
    
    async def test_get_order_by_id(self, async_client: AsyncClient, test_order):
        """Test retrieving specific order"""
        headers = {"Authorization": f"Bearer {test_order['customer_token']}"}
        order_id = test_order["order"]["id"]
        
        response = await async_client.get(
            f"/api/orders/{order_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id
    
    async def test_get_order_unauthorized(self, async_client: AsyncClient, test_order):
        """Test accessing order without proper authorization"""
        # Create different user
        other_user = {
            "email": "other@test.com",
            "password": "TestPass123!",
            "first_name": "Other",
            "last_name": "User",
            "role": "CUSTOMER"
        }
        await async_client.post("/api/auth/register", json=other_user)
        login_response = await async_client.post(
            "/api/auth/login",
            data={"username": "other@test.com", "password": "TestPass123!"}
        )
        other_token = login_response.json()["access_token"]
        
        order_id = test_order["order"]["id"]
        response = await async_client.get(
            f"/api/orders/{order_id}",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        
        assert response.status_code == 403
    
    async def test_update_order_status(self, async_client: AsyncClient, test_order):
        """Test updating order status (seller/admin)"""
        headers = {"Authorization": f"Bearer {test_order['seller_token']}"}
        order_id = test_order["order"]["id"]
        
        response = await async_client.patch(
            f"/api/orders/{order_id}/status",
            json={"status": "PROCESSING"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PROCESSING"
    
    async def test_cancel_order(self, async_client: AsyncClient, test_order):
        """Test cancelling an order"""
        headers = {"Authorization": f"Bearer {test_order['customer_token']}"}
        order_id = test_order["order"]["id"]
        
        response = await async_client.post(
            f"/api/orders/{order_id}/cancel",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "CANCELLED"
    
    async def test_create_order_empty_cart_fails(self, async_client: AsyncClient, authenticated_customer):
        """Test that creating order with empty cart fails"""
        headers = {"Authorization": f"Bearer {authenticated_customer['token']}"}
        
        # Clear cart first
        await async_client.delete("/api/cart", headers=headers)
        
        order_data = {
            "shipping_address": {
                "line1": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "postal_code": "12345",
                "country": "US"
            }
        }
        
        response = await async_client.post(
            "/api/orders",
            json=order_data,
            headers=headers
        )
        
        assert response.status_code == 400
    
    async def test_create_order_missing_address_fails(self, async_client: AsyncClient, authenticated_customer):
        """Test validation for missing shipping address"""
        headers = {"Authorization": f"Bearer {authenticated_customer['token']}"}
        
        order_data = {
            "billing_address": {
                "line1": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "postal_code": "12345",
                "country": "US"
            }
        }
        
        response = await async_client.post(
            "/api/orders",
            json=order_data,
            headers=headers
        )
        
        assert response.status_code == 422


class TestPaymentEndpointsIntegration:
    """Integration tests for payment processing endpoints"""
    
    @pytest_asyncio.fixture
    async def test_order_for_payment(self, async_client: AsyncClient):
        """Create test order ready for payment"""
        # Register and login
        register_data = {
            "email": "payer@test.com",
            "password": "TestPass123!",
            "first_name": "Pay",
            "last_name": "Er",
            "role": "CUSTOMER"
        }
        await async_client.post("/api/auth/register", json=register_data)
        login_response = await async_client.post(
            "/api/auth/login",
            data={"username": "payer@test.com", "password": "TestPass123!"}
        )
        token = login_response.json()["access_token"]
        
        # Create order (simplified)
        order_data = {
            "total_cents": 10000,
            "shipping_address": {"line1": "123 Test St", "city": "Test City", "state": "TS", "postal_code": "12345", "country": "US"}
        }
        order_response = await async_client.post(
            "/api/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        return {
            "order": order_response.json(),
            "token": token
        }
    
    async def test_initiate_payment(self, async_client: AsyncClient, test_order_for_payment):
        """Test initiating payment for an order"""
        headers = {"Authorization": f"Bearer {test_order_for_payment['token']}"}
        order_id = test_order_for_payment["order"]["id"]
        
        payment_data = {
            "order_id": order_id,
            "payment_method": "CREDIT_CARD",
            "amount_cents": 10000
        }
        
        response = await async_client.post(
            "/api/payments",
            json=payment_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "PENDING"
        assert "payment_intent_id" in data
    
    async def test_confirm_payment(self, async_client: AsyncClient, test_order_for_payment):
        """Test confirming a payment"""
        headers = {"Authorization": f"Bearer {test_order_for_payment['token']}"}
        order_id = test_order_for_payment["order"]["id"]
        
        # Initiate payment first
        payment_data = {
            "order_id": order_id,
            "payment_method": "CREDIT_CARD",
            "amount_cents": 10000
        }
        payment_response = await async_client.post(
            "/api/payments",
            json=payment_data,
            headers=headers
        )
        payment_id = payment_response.json()["id"]
        
        # Confirm payment
        confirm_data = {
            "payment_intent_id": "pi_test_123",
            "status": "COMPLETED"
        }
        
        response = await async_client.post(
            f"/api/payments/{payment_id}/confirm",
            json=confirm_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"
    
    async def test_refund_payment(self, async_client: AsyncClient, test_order_for_payment):
        """Test refunding a completed payment"""
        headers = {"Authorization": f"Bearer {test_order_for_payment['token']}"}
        order_id = test_order_for_payment["order"]["id"]
        
        # Create and complete payment
        payment_data = {
            "order_id": order_id,
            "payment_method": "CREDIT_CARD",
            "amount_cents": 10000
        }
        payment_response = await async_client.post(
            "/api/payments",
            json=payment_data,
            headers=headers
        )
        payment_id = payment_response.json()["id"]
        
        # Initiate refund
        refund_data = {
            "amount_cents": 10000,
            "reason": "Customer request"
        }
        
        response = await async_client.post(
            f"/api/payments/{payment_id}/refund",
            json=refund_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["amount_cents"] == 10000
        assert data["status"] == "REFUNDED"
    
    async def test_payment_validation_errors(self, async_client: AsyncClient, test_order_for_payment):
        """Test payment validation with invalid data"""
        headers = {"Authorization": f"Bearer {test_order_for_payment['token']}"}
        
        # Missing order_id
        payment_data = {
            "payment_method": "CREDIT_CARD",
            "amount_cents": 10000
        }
        
        response = await async_client.post(
            "/api/payments",
            json=payment_data,
            headers=headers
        )
        
        assert response.status_code == 422


class TestFulfillmentEndpointsIntegration:
    """Integration tests for order fulfillment and shipment endpoints"""
    
    @pytest_asyncio.fixture
    async def completed_order(self, async_client: AsyncClient):
        """Create paid order ready for fulfillment"""
        # Register seller
        seller_data = {
            "email": "fulfiller@test.com",
            "password": "TestPass123!",
            "first_name": "Fulfill",
            "last_name": "Er",
            "role": "SELLER"
        }
        await async_client.post("/api/auth/register", json=seller_data)
        login_response = await async_client.post(
            "/api/auth/login",
            data={"username": "fulfiller@test.com", "password": "TestPass123!"}
        )
        token = login_response.json()["access_token"]
        
        # Create paid order (simplified)
        order_data = {
            "total_cents": 5000,
            "status": "PAID",
            "shipping_address": {"line1": "123 Test St", "city": "Test City", "state": "TS", "postal_code": "12345", "country": "US"}
        }
        order_response = await async_client.post(
            "/api/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        return {
            "order": order_response.json(),
            "token": token
        }
    
    async def test_create_shipment(self, async_client: AsyncClient, completed_order):
        """Test creating shipment for an order"""
        headers = {"Authorization": f"Bearer {completed_order['token']}"}
        order_id = completed_order["order"]["id"]
        
        shipment_data = {
            "order_id": order_id,
            "carrier": "USPS",
            "tracking_number": "TRACK123456",
            "estimated_delivery": "2024-12-31"
        }
        
        response = await async_client.post(
            "/api/shipments",
            json=shipment_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["carrier"] == "USPS"
        assert data["tracking_number"] == "TRACK123456"
        assert data["status"] == "PENDING"
    
    async def test_update_tracking_info(self, async_client: AsyncClient, completed_order):
        """Test updating shipment tracking information"""
        headers = {"Authorization": f"Bearer {completed_order['token']}"}
        order_id = completed_order["order"]["id"]
        
        # Create shipment first
        shipment_data = {
            "order_id": order_id,
            "carrier": "USPS",
            "tracking_number": "TRACK123456"
        }
        shipment_response = await async_client.post(
            "/api/shipments",
            json=shipment_data,
            headers=headers
        )
        shipment_id = shipment_response.json()["id"]
        
        # Update tracking
        update_data = {
            "status": "IN_TRANSIT",
            "location": "Distribution Center"
        }
        
        response = await async_client.patch(
            f"/api/shipments/{shipment_id}/tracking",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "IN_TRANSIT"
    
    async def test_mark_delivered(self, async_client: AsyncClient, completed_order):
        """Test marking shipment as delivered"""
        headers = {"Authorization": f"Bearer {completed_order['token']}"}
        order_id = completed_order["order"]["id"]
        
        # Create shipment
        shipment_data = {
            "order_id": order_id,
            "carrier": "USPS",
            "tracking_number": "TRACK123456"
        }
        shipment_response = await async_client.post(
            "/api/shipments",
            json=shipment_data,
            headers=headers
        )
        shipment_id = shipment_response.json()["id"]
        
        # Mark as delivered
        response = await async_client.post(
            f"/api/shipments/{shipment_id}/delivered",
            json={"delivered_at": "2024-01-15T10:00:00Z"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "DELIVERED"
        assert "delivered_at" in data
    
    async def test_get_shipment_by_tracking(self, async_client: AsyncClient, completed_order):
        """Test retrieving shipment by tracking number"""
        headers = {"Authorization": f"Bearer {completed_order['token']}"}
        order_id = completed_order["order"]["id"]
        
        # Create shipment
        shipment_data = {
            "order_id": order_id,
            "carrier": "USPS",
            "tracking_number": "TRACK999"
        }
        await async_client.post(
            "/api/shipments",
            json=shipment_data,
            headers=headers
        )
        
        # Get by tracking number
        response = await async_client.get(
            f"/api/shipments/track/TRACK999"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["tracking_number"] == "TRACK999"
    
    async def test_shipment_validation(self, async_client: AsyncClient, completed_order):
        """Test shipment creation validation"""
        headers = {"Authorization": f"Bearer {completed_order['token']}"}
        
        # Missing carrier
        shipment_data = {
            "order_id": completed_order["order"]["id"],
            "tracking_number": "TRACK123"
        }
        
        response = await async_client.post(
            "/api/shipments",
            json=shipment_data,
            headers=headers
        )
        
        assert response.status_code == 422
