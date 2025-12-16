"""
Integration tests for Product Catalog API endpoints
Tests full request/response cycle with database
"""
import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime

from database import Base
from app import app


class TestCatalogEndpointsIntegration:
    """Integration tests for catalog endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_product_full_flow(self, db_session, test_engine):
        """Test complete product creation flow"""
        # Arrange
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create test user/seller
            seller_payload = {
                "email": "seller@test.com",
                "password": "Test123!",
                "full_name": "Test Seller",
                "role": "SELLER"
            }
            
            # Register seller
            register_response = await client.post("/api/auth/register", json=seller_payload)
            assert register_response.status_code == 201
            
            # Login to get token
            login_response = await client.post(
                "/api/auth/login",
                data={"username": "seller@test.com", "password": "Test123!"}
            )
            assert login_response.status_code == 200
            token = login_response.json()["access_token"]
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create category first
            category_payload = {
                "name": "Electronics",
                "slug": "electronics",
                "description": "Electronic items"
            }
            category_response = await client.post(
                "/api/admin/categories",
                json=category_payload,
                headers=headers
            )
            # May need admin role, so create category separately in fixture
            
            # Create product
            product_payload = {
                "name": "Wireless Headphones",
                "description": "High quality wireless headphones",
                "price_cents": 7999,
                "category_id": str(uuid4()),  # Would use real category_id
                "seller_id": register_response.json()["id"],
                "sku": "WH-001",
                "stock_quantity": 50
            }
            
            # Act
            product_response = await client.post(
                "/api/products",
                json=product_payload,
                headers=headers
            )
            
            # Assert
            assert product_response.status_code in [200, 201]
            product_data = product_response.json()
            assert product_data["name"] == "Wireless Headphones"
            assert product_data["price_cents"] == 7999
            assert "id" in product_data
    
    @pytest.mark.asyncio
    async def test_list_products_pagination(self, db_session):
        """Test product listing with pagination"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.get("/api/products?page=1&per_page=10")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "products" in data
            assert isinstance(data["products"], list)
    
    @pytest.mark.asyncio
    async def test_get_product_by_id(self, db_session, create_test_product):
        """Test retrieving product by ID"""
        # Arrange
        product = create_test_product
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.get(f"/api/products/{product.id}")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == str(product.id)
            assert data["name"] == product.name
    
    @pytest.mark.asyncio
    async def test_get_product_not_found(self, db_session):
        """Test retrieving non-existent product returns 404"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.get(f"/api/products/{uuid4()}")
            
            # Assert
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_product_authorized(self, db_session, create_test_product, auth_token_seller):
        """Test product update by owner"""
        # Arrange
        product = create_test_product
        headers = {"Authorization": f"Bearer {auth_token_seller}"}
        
        update_payload = {
            "name": "Updated Product Name",
            "price_cents": 8999
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.patch(
                f"/api/products/{product.id}",
                json=update_payload,
                headers=headers
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Updated Product Name"
            assert data["price_cents"] == 8999
    
    @pytest.mark.asyncio
    async def test_update_product_unauthorized(self, db_session, create_test_product):
        """Test product update by non-owner fails"""
        # Arrange
        product = create_test_product
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act - no auth token
            response = await client.patch(
                f"/api/products/{product.id}",
                json={"name": "Hacked Name"}
            )
            
            # Assert
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_delete_product(self, db_session, create_test_product, auth_token_admin):
        """Test product deletion by admin"""
        # Arrange
        product = create_test_product
        headers = {"Authorization": f"Bearer {auth_token_admin}"}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.delete(
                f"/api/products/{product.id}",
                headers=headers
            )
            
            # Assert
            assert response.status_code == 200
            
            # Verify product is deleted
            get_response = await client.get(f"/api/products/{product.id}")
            assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_search_products(self, db_session):
        """Test product search functionality"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.get("/api/products/search?q=wireless")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "products" in data
    
    @pytest.mark.asyncio
    async def test_filter_products_by_category(self, db_session, create_test_category):
        """Test filtering products by category"""
        # Arrange
        category = create_test_category
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.get(f"/api/products?category_id={category.id}")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "products" in data
    
    @pytest.mark.asyncio
    async def test_filter_products_by_price_range(self, db_session):
        """Test filtering products by price range"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.get("/api/products?min_price=1000&max_price=5000")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "products" in data
            # Verify all products are within price range
            for product in data["products"]:
                assert 1000 <= product["price_cents"] <= 5000
    
    @pytest.mark.asyncio
    async def test_create_product_validation_errors(self, db_session, auth_token_seller):
        """Test product creation with invalid data"""
        # Arrange
        headers = {"Authorization": f"Bearer {auth_token_seller}"}
        
        invalid_payloads = [
            {},  # Empty payload
            {"name": ""},  # Empty name
            {"name": "Test", "price_cents": -100},  # Negative price
            {"name": "Test", "price_cents": "invalid"},  # Invalid price type
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for payload in invalid_payloads:
                # Act
                response = await client.post(
                    "/api/products",
                    json=payload,
                    headers=headers
                )
                
                # Assert
                assert response.status_code == 422  # Validation error


class TestCartEndpointsIntegration:
    """Integration tests for cart endpoints"""
    
    @pytest.mark.asyncio
    async def test_add_to_cart_flow(self, db_session, create_test_product, auth_token_customer):
        """Test complete add to cart flow"""
        # Arrange
        product = create_test_product
        headers = {"Authorization": f"Bearer {auth_token_customer}"}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act - Add item to cart
            response = await client.post(
                "/api/cart/items",
                json={
                    "product_id": str(product.id),
                    "quantity": 2
                },
                headers=headers
            )
            
            # Assert
            assert response.status_code in [200, 201]
            data = response.json()
            assert data["quantity"] == 2
    
    @pytest.mark.asyncio
    async def test_get_cart_items(self, db_session, auth_token_customer):
        """Test retrieving cart items"""
        # Arrange
        headers = {"Authorization": f"Bearer {auth_token_customer}"}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.get("/api/cart", headers=headers)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert isinstance(data["items"], list)
    
    @pytest.mark.asyncio
    async def test_update_cart_item_quantity(self, db_session, create_cart_item, auth_token_customer):
        """Test updating cart item quantity"""
        # Arrange
        cart_item = create_cart_item
        headers = {"Authorization": f"Bearer {auth_token_customer}"}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.patch(
                f"/api/cart/items/{cart_item.id}",
                json={"quantity": 5},
                headers=headers
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["quantity"] == 5
    
    @pytest.mark.asyncio
    async def test_remove_from_cart(self, db_session, create_cart_item, auth_token_customer):
        """Test removing item from cart"""
        # Arrange
        cart_item = create_cart_item
        headers = {"Authorization": f"Bearer {auth_token_customer}"}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.delete(
                f"/api/cart/items/{cart_item.id}",
                headers=headers
            )
            
            # Assert
            assert response.status_code == 200
            
            # Verify item is removed
            get_response = await client.get("/api/cart", headers=headers)
            items = get_response.json()["items"]
            assert not any(item["id"] == str(cart_item.id) for item in items)
    
    @pytest.mark.asyncio
    async def test_clear_cart(self, db_session, auth_token_customer):
        """Test clearing entire cart"""
        # Arrange
        headers = {"Authorization": f"Bearer {auth_token_customer}"}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.delete("/api/cart", headers=headers)
            
            # Assert
            assert response.status_code == 200
            
            # Verify cart is empty
            get_response = await client.get("/api/cart", headers=headers)
            assert len(get_response.json()["items"]) == 0


class TestCheckoutEndpointsIntegration:
    """Integration tests for checkout process"""
    
    @pytest.mark.asyncio
    async def test_checkout_flow_success(self, db_session, create_cart_with_items, auth_token_customer):
        """Test successful checkout flow"""
        # Arrange
        cart = create_cart_with_items
        headers = {"Authorization": f"Bearer {auth_token_customer}"}
        
        checkout_payload = {
            "shipping_address_id": str(uuid4()),
            "billing_address_id": str(uuid4()),
            "payment_method": "CREDIT_CARD"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.post(
                "/api/checkout",
                json=checkout_payload,
                headers=headers
            )
            
            # Assert
            assert response.status_code in [200, 201]
            data = response.json()
            assert "order_id" in data
            assert data["status"] == "PENDING" or data["status"] == "CONFIRMED"
    
    @pytest.mark.asyncio
    async def test_checkout_empty_cart_fails(self, db_session, auth_token_customer):
        """Test checkout with empty cart fails"""
        # Arrange
        headers = {"Authorization": f"Bearer {auth_token_customer}"}
        
        checkout_payload = {
            "shipping_address_id": str(uuid4()),
            "payment_method": "CREDIT_CARD"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.post(
                "/api/checkout",
                json=checkout_payload,
                headers=headers
            )
            
            # Assert
            assert response.status_code == 400
            assert "empty cart" in response.json()["detail"].lower()
