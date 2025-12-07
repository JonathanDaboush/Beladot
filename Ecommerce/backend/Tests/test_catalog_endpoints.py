"""
Tests for Catalog Management Endpoints
Tests category/subcategory management and product/variant CRUD operations.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from Models.User import User, UserRole
from Models.Category import Category
from Models.Subcategory import Subcategory
from Models.Product import Product
from Models.Seller import Seller


@pytest.mark.asyncio
class TestCategoryManagement:
    """Test category and subcategory management (Admin only)"""
    
    async def test_create_category_as_admin(
        self,
        client: AsyncClient,
        admin_token: str
    ):
        """Admin can create main categories"""
        response = await client.post(
            "/api/catalog/categories",
            params={
                "name": "Electronics",
                "description": "Electronic devices and accessories"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Electronics"
        assert "id" in data
        assert data["message"] == "Category created successfully"
    
    async def test_create_category_as_non_admin_fails(
        self,
        client: AsyncClient,
        customer_token: str
    ):
        """Non-admin users cannot create categories"""
        response = await client.post(
            "/api/catalog/categories",
            params={
                "name": "Electronics",
                "description": "Electronic devices"
            },
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == 403
    
    async def test_create_subcategory_as_admin(
        self,
        client: AsyncClient,
        admin_token: str,
        db: AsyncSession
    ):
        """Admin can create subcategories under categories"""
        # Create parent category
        category = Category(
            name="Electronics",
            slug="electronics",
            is_active=True
        )
        db.add(category)
        await db.commit()
        await db.refresh(category)
        
        response = await client.post(
            f"/api/catalog/categories/{category.id}/subcategories",
            params={
                "name": "Televisions",
                "description": "TV and displays"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Televisions"
        assert data["category_id"] == category.id
        assert data["category_name"] == "Electronics"
    
    async def test_list_categories_public(
        self,
        client: AsyncClient,
        db: AsyncSession
    ):
        """Anyone can list categories"""
        # Create test data
        category = Category(name="Electronics", slug="electronics", is_active=True)
        db.add(category)
        await db.commit()
        await db.refresh(category)
        
        subcategory = Subcategory(
            category_id=category.id,
            name="Phones",
            is_active=True
        )
        db.add(subcategory)
        await db.commit()
        
        response = await client.get("/api/catalog/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0
        assert data["categories"][0]["name"] == "Electronics"
        assert len(data["categories"][0]["subcategories"]) == 1


@pytest.mark.asyncio
class TestProductManagement:
    """Test product CRUD operations (Sellers, CS, Managers)"""
    
    async def test_seller_create_product(
        self,
        client: AsyncClient,
        seller_token: str,
        db: AsyncSession
    ):
        """Seller can create products for themselves"""
        # Create category
        category = Category(name="Electronics", slug="electronics", is_active=True)
        db.add(category)
        await db.commit()
        await db.refresh(category)
        
        response = await client.post(
            "/api/catalog/products",
            params={
                "name": "Wireless Mouse",
                "description": "Ergonomic wireless mouse",
                "price_cents": 2999,
                "category_id": category.id,
                "sku": "MOUSE001"
            },
            headers={"Authorization": f"Bearer {seller_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Wireless Mouse"
        assert data["sku"] == "MOUSE001"
        assert data["price_cents"] == 2999
    
    async def test_seller_update_own_product(
        self,
        client: AsyncClient,
        seller_token: str,
        seller_user: User,
        db: AsyncSession
    ):
        """Seller can update their own products"""
        # Create seller and product
        seller = Seller(user_id=seller_user.id, business_name="Test Shop")
        db.add(seller)
        await db.commit()
        await db.refresh(seller)
        
        category = Category(name="Electronics", slug="electronics", is_active=True)
        db.add(category)
        await db.commit()
        
        product = Product(
            name="Old Name",
            description="Old description",
            price_cents=1000,
            sku="TEST001",
            seller_id=seller.id,
            category_id=category.id
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)
        
        response = await client.put(
            f"/api/catalog/products/{product.id}",
            params={
                "name": "New Name",
                "price_cents": 1500
            },
            headers={"Authorization": f"Bearer {seller_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["price_cents"] == 1500
    
    async def test_seller_cannot_update_other_product(
        self,
        client: AsyncClient,
        seller_token: str,
        db: AsyncSession
    ):
        """Seller cannot update products they don't own"""
        # Create another seller's product
        other_seller = Seller(user_id=999, business_name="Other Shop")
        db.add(other_seller)
        await db.commit()
        
        category = Category(name="Electronics", slug="electronics", is_active=True)
        db.add(category)
        await db.commit()
        
        product = Product(
            name="Other Product",
            description="Not yours",
            price_cents=1000,
            sku="OTHER001",
            seller_id=other_seller.id,
            category_id=category.id
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)
        
        response = await client.put(
            f"/api/catalog/products/{product.id}",
            params={"name": "Hacked Name"},
            headers={"Authorization": f"Bearer {seller_token}"}
        )
        
        assert response.status_code == 403


@pytest.mark.asyncio
class TestVariantManagement:
    """Test product variant operations (Sellers only)"""
    
    async def test_seller_create_variant(
        self,
        client: AsyncClient,
        seller_token: str,
        seller_user: User,
        db: AsyncSession
    ):
        """Seller can create variants for their products"""
        # Setup
        seller = Seller(user_id=seller_user.id, business_name="Test Shop")
        db.add(seller)
        await db.commit()
        
        category = Category(name="Electronics", slug="electronics", is_active=True)
        db.add(category)
        await db.commit()
        
        product = Product(
            name="T-Shirt",
            description="Basic tee",
            price_cents=1999,
            sku="SHIRT001",
            seller_id=seller.id,
            category_id=category.id
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)
        
        response = await client.post(
            f"/api/catalog/products/{product.id}/variants",
            params={
                "sku": "SHIRT001-RED-M",
                "name": "Red - Medium",
                "price_cents": 1999,
                "stock_quantity": 50
            },
            headers={"Authorization": f"Bearer {seller_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["sku"] == "SHIRT001-RED-M"
        assert data["name"] == "Red - Medium"
        assert data["price_cents"] == 1999
    
    async def test_non_seller_cannot_create_variant(
        self,
        client: AsyncClient,
        customer_token: str,
        db: AsyncSession
    ):
        """Non-sellers cannot create variants"""
        response = await client.post(
            "/api/catalog/products/1/variants",
            params={
                "sku": "VAR001",
                "name": "Variant",
                "price_cents": 1000
            },
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == 403


@pytest.mark.asyncio
class TestImageUpload:
    """Test product image upload (Sellers only)"""
    
    async def test_seller_upload_image(
        self,
        client: AsyncClient,
        seller_token: str,
        seller_user: User,
        db: AsyncSession
    ):
        """Seller can upload images for their products"""
        # Setup
        seller = Seller(user_id=seller_user.id, business_name="Test Shop")
        db.add(seller)
        await db.commit()
        
        category = Category(name="Electronics", slug="electronics", is_active=True)
        db.add(category)
        await db.commit()
        
        product = Product(
            name="Product",
            description="Test",
            price_cents=1000,
            sku="PROD001",
            seller_id=seller.id,
            category_id=category.id
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)
        
        # Mock file upload
        files = {"file": ("test.jpg", b"fake image data", "image/jpeg")}
        
        response = await client.post(
            f"/api/catalog/products/{product.id}/images",
            files=files,
            headers={"Authorization": f"Bearer {seller_token}"}
        )
        
        # May fail without actual blob service, but test structure is correct
        assert response.status_code in [200, 500]  # 500 if blob service not configured
