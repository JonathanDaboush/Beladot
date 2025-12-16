"""
Comprehensive edge case and error handling tests
Tests boundary conditions, validation, and error scenarios
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

pytestmark = pytest.mark.asyncio


class TestValidationEdgeCases:
    """Test validation and boundary conditions"""
    
    async def test_product_price_validation(self, async_client: AsyncClient):
        """Test price validation edge cases"""
        # Register seller
        seller_data = {
            "email": "seller@test.com",
            "password": "TestPass123!",
            "role": "SELLER"
        }
        await async_client.post("/api/auth/register", json=seller_data)
        login = await async_client.post(
            "/api/auth/login",
            data={"username": "seller@test.com", "password": "TestPass123!"}
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Zero price should fail
        product_data = {
            "name": "Test Product",
            "description": "Test",
            "price_cents": 0,
            "category_id": "test-cat"
        }
        response = await async_client.post("/api/products", json=product_data, headers=headers)
        assert response.status_code == 422
        
        # Negative price should fail
        product_data["price_cents"] = -100
        response = await async_client.post("/api/products", json=product_data, headers=headers)
        assert response.status_code == 422
        
        # Maximum price boundary
        product_data["price_cents"] = 99999999  # Should succeed
        response = await async_client.post("/api/products", json=product_data, headers=headers)
        assert response.status_code in [200, 201]
    
    async def test_product_name_length_validation(self, async_client: AsyncClient):
        """Test product name length boundaries"""
        seller_data = {
            "email": "seller2@test.com",
            "password": "TestPass123!",
            "role": "SELLER"
        }
        await async_client.post("/api/auth/register", json=seller_data)
        login = await async_client.post(
            "/api/auth/login",
            data={"username": "seller2@test.com", "password": "TestPass123!"}
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Empty name should fail
        product_data = {
            "name": "",
            "description": "Test",
            "price_cents": 1000,
            "category_id": "test-cat"
        }
        response = await async_client.post("/api/products", json=product_data, headers=headers)
        assert response.status_code == 422
        
        # Very long name (>255 chars) should fail
        product_data["name"] = "A" * 300
        response = await async_client.post("/api/products", json=product_data, headers=headers)
        assert response.status_code == 422
        
        # Maximum allowed length should succeed
        product_data["name"] = "A" * 255
        response = await async_client.post("/api/products", json=product_data, headers=headers)
        assert response.status_code in [200, 201]
    
    async def test_email_validation(self, async_client: AsyncClient):
        """Test email format validation"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user@.com",
            "user name@example.com",
            "user@example",
        ]
        
        for email in invalid_emails:
            register_data = {
                "email": email,
                "password": "TestPass123!",
                "first_name": "Test",
                "last_name": "User",
                "role": "CUSTOMER"
            }
            response = await async_client.post("/api/auth/register", json=register_data)
            assert response.status_code == 422, f"Email {email} should be invalid"
    
    async def test_password_strength_validation(self, async_client: AsyncClient):
        """Test password strength requirements"""
        weak_passwords = [
            "short",  # Too short
            "alllowercase123",  # No uppercase
            "ALLUPPERCASE123",  # No lowercase
            "NoNumbers",  # No numbers
            "NoSpecial123",  # No special chars (if required)
        ]
        
        for password in weak_passwords:
            register_data = {
                "email": f"test{password}@example.com",
                "password": password,
                "first_name": "Test",
                "last_name": "User",
                "role": "CUSTOMER"
            }
            response = await async_client.post("/api/auth/register", json=register_data)
            assert response.status_code == 422, f"Password '{password}' should be rejected"
    
    async def test_cart_quantity_boundaries(self, async_client: AsyncClient):
        """Test cart item quantity validation"""
        # Register and login
        register_data = {
            "email": "cart@test.com",
            "password": "TestPass123!",
            "role": "CUSTOMER"
        }
        await async_client.post("/api/auth/register", json=register_data)
        login = await async_client.post(
            "/api/auth/login",
            data={"username": "cart@test.com", "password": "TestPass123!"}
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Zero quantity should fail
        cart_data = {"product_id": "test-prod-id", "quantity": 0}
        response = await async_client.post("/api/cart/items", json=cart_data, headers=headers)
        assert response.status_code == 422
        
        # Negative quantity should fail
        cart_data["quantity"] = -5
        response = await async_client.post("/api/cart/items", json=cart_data, headers=headers)
        assert response.status_code == 422
        
        # Excessive quantity (>stock) should fail
        cart_data["quantity"] = 99999
        response = await async_client.post("/api/cart/items", json=cart_data, headers=headers)
        assert response.status_code in [400, 422]


class TestConcurrencyAndRaceConditions:
    """Test concurrent operations and race conditions"""
    
    async def test_concurrent_stock_deduction(self, async_client: AsyncClient):
        """Test that concurrent purchases don't oversell inventory"""
        # This would require actual concurrent requests
        # Placeholder for demonstration
        pass
    
    async def test_double_payment_prevention(self, async_client: AsyncClient):
        """Test that same order can't be paid twice"""
        # Register and create order
        register_data = {
            "email": "payment@test.com",
            "password": "TestPass123!",
            "role": "CUSTOMER"
        }
        await async_client.post("/api/auth/register", json=register_data)
        login = await async_client.post(
            "/api/auth/login",
            data={"username": "payment@test.com", "password": "TestPass123!"}
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create order
        order_data = {
            "total_cents": 5000,
            "shipping_address": {"line1": "123 St", "city": "City", "state": "ST", "postal_code": "12345", "country": "US"}
        }
        order_response = await async_client.post("/api/orders", json=order_data, headers=headers)
        order_id = order_response.json()["id"]
        
        # First payment
        payment_data = {
            "order_id": order_id,
            "payment_method": "CREDIT_CARD",
            "amount_cents": 5000
        }
        first_payment = await async_client.post("/api/payments", json=payment_data, headers=headers)
        assert first_payment.status_code == 201
        
        # Second payment attempt should fail
        second_payment = await async_client.post("/api/payments", json=payment_data, headers=headers)
        assert second_payment.status_code in [400, 409]  # Already paid


class TestAuthorizationEdgeCases:
    """Test authorization and permission edge cases"""
    
    async def test_access_other_user_order(self, async_client: AsyncClient):
        """Test that users can't access other users' orders"""
        # Create two users
        user1_data = {"email": "user1@test.com", "password": "TestPass123!", "role": "CUSTOMER"}
        user2_data = {"email": "user2@test.com", "password": "TestPass123!", "role": "CUSTOMER"}
        
        await async_client.post("/api/auth/register", json=user1_data)
        await async_client.post("/api/auth/register", json=user2_data)
        
        # User 1 creates order
        login1 = await async_client.post(
            "/api/auth/login",
            data={"username": "user1@test.com", "password": "TestPass123!"}
        )
        token1 = login1.json()["access_token"]
        
        order_data = {
            "total_cents": 3000,
            "shipping_address": {"line1": "123 St", "city": "City", "state": "ST", "postal_code": "12345", "country": "US"}
        }
        order_response = await async_client.post(
            "/api/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        order_id = order_response.json()["id"]
        
        # User 2 tries to access User 1's order
        login2 = await async_client.post(
            "/api/auth/login",
            data={"username": "user2@test.com", "password": "TestPass123!"}
        )
        token2 = login2.json()["access_token"]
        
        response = await async_client.get(
            f"/api/orders/{order_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 403
    
    async def test_customer_cannot_update_product(self, async_client: AsyncClient):
        """Test that customers can't update products"""
        # Create seller and product
        seller_data = {"email": "seller@test.com", "password": "TestPass123!", "role": "SELLER"}
        await async_client.post("/api/auth/register", json=seller_data)
        seller_login = await async_client.post(
            "/api/auth/login",
            data={"username": "seller@test.com", "password": "TestPass123!"}
        )
        seller_token = seller_login.json()["access_token"]
        
        product_data = {
            "name": "Product",
            "description": "Test",
            "price_cents": 5000,
            "category_id": "test-cat"
        }
        product_response = await async_client.post(
            "/api/products",
            json=product_data,
            headers={"Authorization": f"Bearer {seller_token}"}
        )
        product_id = product_response.json()["id"]
        
        # Create customer
        customer_data = {"email": "customer@test.com", "password": "TestPass123!", "role": "CUSTOMER"}
        await async_client.post("/api/auth/register", json=customer_data)
        customer_login = await async_client.post(
            "/api/auth/login",
            data={"username": "customer@test.com", "password": "TestPass123!"}
        )
        customer_token = customer_login.json()["access_token"]
        
        # Customer tries to update product
        update_data = {"price_cents": 1000}
        response = await async_client.patch(
            f"/api/products/{product_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == 403
    
    async def test_expired_token(self, async_client: AsyncClient):
        """Test that expired tokens are rejected"""
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjowfQ.invalid"
        
        response = await async_client.get(
            "/api/orders",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401


class TestDatabaseConstraints:
    """Test database-level constraints and integrity"""
    
    async def test_duplicate_email_registration(self, async_client: AsyncClient):
        """Test that duplicate emails are rejected"""
        user_data = {
            "email": "duplicate@test.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User",
            "role": "CUSTOMER"
        }
        
        # First registration
        response1 = await async_client.post("/api/auth/register", json=user_data)
        assert response1.status_code in [200, 201]
        
        # Duplicate registration
        response2 = await async_client.post("/api/auth/register", json=user_data)
        assert response2.status_code == 409
    
    async def test_foreign_key_constraint(self, async_client: AsyncClient):
        """Test that invalid foreign keys are rejected"""
        # Register seller
        seller_data = {"email": "seller@test.com", "password": "TestPass123!", "role": "SELLER"}
        await async_client.post("/api/auth/register", json=seller_data)
        login = await async_client.post(
            "/api/auth/login",
            data={"username": "seller@test.com", "password": "TestPass123!"}
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to create product with non-existent category
        product_data = {
            "name": "Product",
            "description": "Test",
            "price_cents": 5000,
            "category_id": "non-existent-category-id"
        }
        response = await async_client.post("/api/products", json=product_data, headers=headers)
        assert response.status_code in [400, 404, 422]


class TestPaginationEdgeCases:
    """Test pagination boundary conditions"""
    
    async def test_pagination_first_page(self, async_client: AsyncClient):
        """Test first page of results"""
        response = await async_client.get("/api/products?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
    
    async def test_pagination_beyond_results(self, async_client: AsyncClient):
        """Test requesting page beyond available results"""
        response = await async_client.get("/api/products?page=9999&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0
    
    async def test_pagination_invalid_params(self, async_client: AsyncClient):
        """Test invalid pagination parameters"""
        # Negative page
        response = await async_client.get("/api/products?page=-1&limit=10")
        assert response.status_code == 422
        
        # Zero page
        response = await async_client.get("/api/products?page=0&limit=10")
        assert response.status_code == 422
        
        # Excessive limit
        response = await async_client.get("/api/products?page=1&limit=1000")
        assert response.status_code == 422


class TestErrorRecovery:
    """Test error handling and recovery scenarios"""
    
    @patch('Ecommerce.backend.Services.CatalogService.CatalogService.create_product')
    async def test_service_unavailable_recovery(self, mock_create_product, async_client: AsyncClient):
        """Test handling of temporary service failures"""
        mock_create_product.side_effect = Exception("Database connection lost")
        
        seller_data = {"email": "seller@test.com", "password": "TestPass123!", "role": "SELLER"}
        await async_client.post("/api/auth/register", json=seller_data)
        login = await async_client.post(
            "/api/auth/login",
            data={"username": "seller@test.com", "password": "TestPass123!"}
        )
        token = login.json()["access_token"]
        
        product_data = {
            "name": "Product",
            "description": "Test",
            "price_cents": 5000,
            "category_id": "test-cat"
        }
        
        response = await async_client.post(
            "/api/products",
            json=product_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 500
    
    async def test_malformed_json(self, async_client: AsyncClient):
        """Test handling of malformed JSON requests"""
        response = await async_client.post(
            "/api/auth/register",
            content="{'invalid': json}",  # Not valid JSON
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    async def test_missing_content_type(self, async_client: AsyncClient):
        """Test handling of missing Content-Type header"""
        response = await async_client.post(
            "/api/auth/register",
            content='{"email": "test@test.com"}',
            # No Content-Type header
        )
        
        # Should still work or return appropriate error
        assert response.status_code in [200, 201, 400, 415, 422]


class TestBusinessLogicEdgeCases:
    """Test complex business logic scenarios"""
    
    async def test_cart_persistence_across_sessions(self, async_client: AsyncClient):
        """Test that cart persists when user logs out and back in"""
        # Register and login
        register_data = {"email": "persist@test.com", "password": "TestPass123!", "role": "CUSTOMER"}
        await async_client.post("/api/auth/register", json=register_data)
        login1 = await async_client.post(
            "/api/auth/login",
            data={"username": "persist@test.com", "password": "TestPass123!"}
        )
        token1 = login1.json()["access_token"]
        
        # Add item to cart
        cart_data = {"product_id": "test-prod", "quantity": 3}
        await async_client.post(
            "/api/cart/items",
            json=cart_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        # Login again (new session)
        login2 = await async_client.post(
            "/api/auth/login",
            data={"username": "persist@test.com", "password": "TestPass123!"}
        )
        token2 = login2.json()["access_token"]
        
        # Check cart still has items
        response = await async_client.get(
            "/api/cart",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0
    
    async def test_order_status_transition_validation(self, async_client: AsyncClient):
        """Test that order status transitions follow business rules"""
        # Can't go from DELIVERED back to PENDING
        # Can't skip PROCESSING and go directly to SHIPPED
        # etc.
        pass
    
    async def test_refund_exceeds_payment_amount(self, async_client: AsyncClient):
        """Test that refund can't exceed original payment"""
        # Create paid order
        register_data = {"email": "refund@test.com", "password": "TestPass123!", "role": "CUSTOMER"}
        await async_client.post("/api/auth/register", json=register_data)
        login = await async_client.post(
            "/api/auth/login",
            data={"username": "refund@test.com", "password": "TestPass123!"}
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create order and payment
        order_data = {
            "total_cents": 5000,
            "shipping_address": {"line1": "123 St", "city": "City", "state": "ST", "postal_code": "12345", "country": "US"}
        }
        order_response = await async_client.post("/api/orders", json=order_data, headers=headers)
        order_id = order_response.json()["id"]
        
        payment_data = {
            "order_id": order_id,
            "payment_method": "CREDIT_CARD",
            "amount_cents": 5000
        }
        payment_response = await async_client.post("/api/payments", json=payment_data, headers=headers)
        payment_id = payment_response.json()["id"]
        
        # Try to refund more than paid
        refund_data = {
            "amount_cents": 10000,  # More than the 5000 paid
            "reason": "Test"
        }
        
        response = await async_client.post(
            f"/api/payments/{payment_id}/refund",
            json=refund_data,
            headers=headers
        )
        
        assert response.status_code == 400
