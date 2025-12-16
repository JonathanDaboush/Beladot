"""
Unit tests for CatalogService
Tests all CRUD operations, validation, and error handling
"""
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from Services.CatalogService import CatalogService
from Classes.Product import Product
from Classes.ProductVariant import ProductVariant
from Classes.ProductImage import ProductImage
from Classes.Category import Category


class TestCatalogServiceUnit:
    """Unit tests for CatalogService - isolated from database"""
    
    @pytest.fixture
    def mock_repos(self):
        """Create mock repositories"""
        return {
            'product_repo': MagicMock(),
            'variant_repo': MagicMock(),
            'image_repo': MagicMock(),
            'category_repo': MagicMock(),
            'audit_repo': MagicMock()
        }
    
    @pytest.fixture
    def catalog_service(self, mock_repos):
        """Create CatalogService with mocked dependencies"""
        mock_db = MagicMock()
        service = CatalogService(mock_db)
        service.product_repo = mock_repos['product_repo']
        service.variant_repo = mock_repos['variant_repo']
        service.image_repo = mock_repos['image_repo']
        service.category_repo = mock_repos['category_repo']
        service.audit_repo = mock_repos['audit_repo']
        return service
    
    @pytest.mark.asyncio
    async def test_create_product_success(self, catalog_service, mock_repos):
        """Test successful product creation with valid data"""
        # Arrange
        category_id = uuid4()
        seller_id = uuid4()
        product_id = uuid4()
        
        mock_category = Category(
            id=category_id,
            name="Electronics",
            slug="electronics"
        )
        mock_repos['category_repo'].get_by_id = AsyncMock(return_value=mock_category)
        
        mock_product = Product(
            id=product_id,
            name="Test Product",
            category_id=category_id,
            seller_id=seller_id,
            sku="TEST-001",
            price_cents=9999
        )
        mock_repos['product_repo'].create = AsyncMock(return_value=mock_product)
        
        mock_variant = ProductVariant(
            id=uuid4(),
            product_id=product_id,
            sku="TEST-001",
            name="Test Product",
            price_cents=9999
        )
        mock_repos['variant_repo'].create = AsyncMock(return_value=mock_variant)
        mock_repos['audit_repo'].create = AsyncMock()
        
        payload = {
            'name': 'Test Product',
            'category_id': category_id,
            'seller_id': seller_id,
            'sku': 'TEST-001',
            'price_cents': 9999
        }
        
        # Act
        result = await catalog_service.create_product(payload, actor_id=seller_id)
        
        # Assert
        assert result.id == product_id
        assert result.name == "Test Product"
        mock_repos['category_repo'].get_by_id.assert_called_once_with(category_id)
        mock_repos['product_repo'].create.assert_called_once()
        mock_repos['variant_repo'].create.assert_called_once()
        mock_repos['audit_repo'].create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_product_invalid_category(self, catalog_service, mock_repos):
        """Test product creation fails with invalid category"""
        # Arrange
        mock_repos['category_repo'].get_by_id = AsyncMock(return_value=None)
        
        payload = {
            'name': 'Test Product',
            'category_id': uuid4(),
            'seller_id': uuid4(),
            'sku': 'TEST-001',
            'price_cents': 9999
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Category does not exist"):
            await catalog_service.create_product(payload)
    
    @pytest.mark.asyncio
    async def test_create_product_missing_seller_id(self, catalog_service, mock_repos):
        """Test product creation fails without seller_id"""
        # Arrange
        category_id = uuid4()
        mock_category = Category(id=category_id, name="Electronics", slug="electronics")
        mock_repos['category_repo'].get_by_id = AsyncMock(return_value=mock_category)
        
        payload = {
            'name': 'Test Product',
            'category_id': category_id,
            'sku': 'TEST-001',
            'price_cents': 9999
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="seller_id is required"):
            await catalog_service.create_product(payload)
    
    @pytest.mark.asyncio
    async def test_create_product_with_variants(self, catalog_service, mock_repos):
        """Test product creation with custom variants"""
        # Arrange
        category_id = uuid4()
        seller_id = uuid4()
        product_id = uuid4()
        
        mock_category = Category(id=category_id, name="Clothing", slug="clothing")
        mock_repos['category_repo'].get_by_id = AsyncMock(return_value=mock_category)
        
        mock_product = Product(
            id=product_id,
            name="T-Shirt",
            category_id=category_id,
            seller_id=seller_id
        )
        mock_repos['product_repo'].create = AsyncMock(return_value=mock_product)
        mock_repos['variant_repo'].create = AsyncMock(side_effect=[
            ProductVariant(id=uuid4(), product_id=product_id, name="Small"),
            ProductVariant(id=uuid4(), product_id=product_id, name="Medium"),
            ProductVariant(id=uuid4(), product_id=product_id, name="Large")
        ])
        mock_repos['audit_repo'].create = AsyncMock()
        
        payload = {
            'name': 'T-Shirt',
            'category_id': category_id,
            'seller_id': seller_id,
            'variants': [
                {'name': 'Small', 'sku': 'TSHIRT-S', 'price_cents': 1999},
                {'name': 'Medium', 'sku': 'TSHIRT-M', 'price_cents': 1999},
                {'name': 'Large', 'sku': 'TSHIRT-L', 'price_cents': 1999}
            ]
        }
        
        # Act
        result = await catalog_service.create_product(payload)
        
        # Assert
        assert result.id == product_id
        assert mock_repos['variant_repo'].create.call_count == 3
    
    @pytest.mark.asyncio
    async def test_create_product_with_images(self, catalog_service, mock_repos):
        """Test product creation with images"""
        # Arrange
        category_id = uuid4()
        seller_id = uuid4()
        product_id = uuid4()
        
        mock_category = Category(id=category_id, name="Electronics", slug="electronics")
        mock_repos['category_repo'].get_by_id = AsyncMock(return_value=mock_category)
        
        mock_product = Product(id=product_id, name="Camera", category_id=category_id, seller_id=seller_id)
        mock_repos['product_repo'].create = AsyncMock(return_value=mock_product)
        mock_repos['variant_repo'].create = AsyncMock(return_value=ProductVariant(id=uuid4(), product_id=product_id))
        mock_repos['image_repo'].create = AsyncMock(side_effect=[
            ProductImage(id=uuid4(), product_id=product_id, blob_id="image1.jpg"),
            ProductImage(id=uuid4(), product_id=product_id, blob_id="image2.jpg")
        ])
        mock_repos['audit_repo'].create = AsyncMock()
        
        payload = {
            'name': 'Camera',
            'category_id': category_id,
            'seller_id': seller_id,
            'images': [
                {'blob_id': 'image1.jpg', 'alt_text': 'Front view'},
                {'blob_id': 'image2.jpg', 'alt_text': 'Side view'}
            ]
        }
        
        # Act
        result = await catalog_service.create_product(payload)
        
        # Assert
        assert result.id == product_id
        assert mock_repos['image_repo'].create.call_count == 2
    
    @pytest.mark.asyncio
    async def test_get_product_by_id_success(self, catalog_service, mock_repos):
        """Test retrieving product by ID"""
        # Arrange
        product_id = uuid4()
        mock_product = Product(id=product_id, name="Test Product")
        mock_repos['product_repo'].get_by_id = AsyncMock(return_value=mock_product)
        
        # Act
        result = await catalog_service.get_product_by_id(product_id)
        
        # Assert
        assert result.id == product_id
        mock_repos['product_repo'].get_by_id.assert_called_once_with(product_id)
    
    @pytest.mark.asyncio
    async def test_get_product_by_id_not_found(self, catalog_service, mock_repos):
        """Test retrieving non-existent product"""
        # Arrange
        product_id = uuid4()
        mock_repos['product_repo'].get_by_id = AsyncMock(return_value=None)
        
        # Act
        result = await catalog_service.get_product_by_id(product_id)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_product_success(self, catalog_service, mock_repos):
        """Test successful product update"""
        # Arrange
        product_id = uuid4()
        mock_product = Product(
            id=product_id,
            name="Old Name",
            description="Old Description"
        )
        mock_repos['product_repo'].get_by_id = AsyncMock(return_value=mock_product)
        mock_repos['product_repo'].update = AsyncMock(return_value=mock_product)
        mock_repos['audit_repo'].create = AsyncMock()
        
        patch_data = {
            'name': 'New Name',
            'description': 'New Description'
        }
        
        # Act
        result = await catalog_service.update_product(product_id, patch_data, actor_id=uuid4())
        
        # Assert
        assert result.name == "New Name"
        assert result.description == "New Description"
        mock_repos['product_repo'].update.assert_called_once()
        mock_repos['audit_repo'].create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_product_not_found(self, catalog_service, mock_repos):
        """Test updating non-existent product fails"""
        # Arrange
        product_id = uuid4()
        mock_repos['product_repo'].get_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Product not found"):
            await catalog_service.update_product(product_id, {'name': 'New Name'})
    
    @pytest.mark.asyncio
    async def test_list_products_with_pagination(self, catalog_service, mock_repos):
        """Test listing products with pagination"""
        # Arrange
        mock_products = [
            Product(id=uuid4(), name=f"Product {i}")
            for i in range(5)
        ]
        mock_repos['product_repo'].get_all = AsyncMock(return_value=mock_products)
        mock_repos['audit_repo'].create = AsyncMock()
        
        # Act
        result = await catalog_service.list_products(
            filters={},
            page=1,
            per_page=10
        )
        
        # Assert
        assert len(result['products']) == 5
        mock_repos['product_repo'].get_all.assert_called_once_with(limit=10, offset=0)
    
    @pytest.mark.asyncio
    async def test_create_variant_success(self, catalog_service, mock_repos):
        """Test creating product variant"""
        # Arrange
        product_id = uuid4()
        variant_id = uuid4()
        mock_variant = ProductVariant(
            id=variant_id,
            product_id=product_id,
            name="Blue - Large",
            sku="PROD-BL-L"
        )
        mock_repos['variant_repo'].create = AsyncMock(return_value=mock_variant)
        mock_repos['audit_repo'].create = AsyncMock()
        
        variant_payload = {
            'name': 'Blue - Large',
            'sku': 'PROD-BL-L',
            'price_cents': 2999
        }
        
        # Act
        result = await catalog_service.create_variant(product_id, variant_payload)
        
        # Assert
        assert result.id == variant_id
        assert result.product_id == product_id
        mock_repos['variant_repo'].create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_variant_success(self, catalog_service, mock_repos):
        """Test updating product variant"""
        # Arrange
        variant_id = uuid4()
        mock_variant = ProductVariant(
            id=variant_id,
            name="Old Name",
            price_cents=1999
        )
        mock_repos['variant_repo'].get_by_id = AsyncMock(return_value=mock_variant)
        mock_repos['variant_repo'].update = AsyncMock(return_value=mock_variant)
        mock_repos['audit_repo'].create = AsyncMock()
        
        patch_data = {'price_cents': 2499}
        
        # Act
        result = await catalog_service.update_variant(variant_id, patch_data)
        
        # Assert
        assert result.price_cents == 2499
        mock_repos['variant_repo'].update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_variant_not_found(self, catalog_service, mock_repos):
        """Test updating non-existent variant fails"""
        # Arrange
        variant_id = uuid4()
        mock_repos['variant_repo'].get_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Variant not found"):
            await catalog_service.update_variant(variant_id, {'price_cents': 2499})
    
    @pytest.mark.asyncio
    async def test_upload_image_success(self, catalog_service, mock_repos):
        """Test uploading product image"""
        # Arrange
        product_id = uuid4()
        image_id = uuid4()
        mock_image = ProductImage(
            id=image_id,
            product_id=product_id,
            blob_id="test-image.jpg"
        )
        mock_repos['image_repo'].create = AsyncMock(return_value=mock_image)
        mock_repos['audit_repo'].create = AsyncMock()
        
        mock_file_stream = MagicMock()
        
        # Act
        result = await catalog_service.upload_image(
            product_id,
            None,
            mock_file_stream,
            "test-image.jpg"
        )
        
        # Assert
        assert result.id == image_id
        assert result.product_id == product_id
        mock_repos['image_repo'].create.assert_called_once()
