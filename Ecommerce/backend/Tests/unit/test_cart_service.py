"""
Unit tests for CartService
Tests cart operations, item management, and price calculations
"""
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal

from Services.CartService import CartService
from Classes.Cart import Cart
from Classes.CartItem import CartItem
from Classes.ProductVariant import ProductVariant


class TestCartServiceUnit:
    """Unit tests for CartService"""
    
    @pytest.fixture
    def mock_repos(self):
        """Create mock repositories"""
        return {
            'cart_repo': MagicMock(),
            'cart_item_repo': MagicMock(),
            'variant_repo': MagicMock(),
            'audit_repo': MagicMock()
        }
    
    @pytest.fixture
    def cart_service(self, mock_repos):
        """Create CartService with mocked dependencies"""
        mock_db = MagicMock()
        service = CartService(mock_db)
        service.cart_repo = mock_repos['cart_repo']
        service.cart_item_repo = mock_repos['cart_item_repo']
        service.variant_repo = mock_repos['variant_repo']
        service.audit_repo = mock_repos['audit_repo']
        return service
    
    @pytest.mark.asyncio
    async def test_create_cart_success(self, cart_service, mock_repos):
        """Test creating a new cart"""
        # Arrange
        user_id = uuid4()
        cart_id = uuid4()
        mock_cart = Cart(id=cart_id, user_id=user_id)
        mock_repos['cart_repo'].create = AsyncMock(return_value=mock_cart)
        
        # Act
        result = await cart_service.create_cart(user_id)
        
        # Assert
        assert result.id == cart_id
        assert result.user_id == user_id
        mock_repos['cart_repo'].create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_item_to_cart_success(self, cart_service, mock_repos):
        """Test adding item to cart"""
        # Arrange
        cart_id = uuid4()
        variant_id = uuid4()
        
        mock_cart = Cart(id=cart_id)
        mock_repos['cart_repo'].get_by_id = AsyncMock(return_value=mock_cart)
        
        mock_variant = ProductVariant(
            id=variant_id,
            price_cents=1999,
            stock_quantity=10
        )
        mock_repos['variant_repo'].get_by_id = AsyncMock(return_value=mock_variant)
        
        mock_existing_item = None
        mock_repos['cart_item_repo'].get_by_cart_and_variant = AsyncMock(return_value=mock_existing_item)
        
        mock_cart_item = CartItem(
            id=uuid4(),
            cart_id=cart_id,
            variant_id=variant_id,
            quantity=2
        )
        mock_repos['cart_item_repo'].create = AsyncMock(return_value=mock_cart_item)
        
        # Act
        result = await cart_service.add_item_to_cart(cart_id, variant_id, quantity=2)
        
        # Assert
        assert result.cart_id == cart_id
        assert result.variant_id == variant_id
        assert result.quantity == 2
        mock_repos['cart_item_repo'].create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_item_cart_not_found(self, cart_service, mock_repos):
        """Test adding item to non-existent cart fails"""
        # Arrange
        cart_id = uuid4()
        variant_id = uuid4()
        mock_repos['cart_repo'].get_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cart not found"):
            await cart_service.add_item_to_cart(cart_id, variant_id, quantity=1)
    
    @pytest.mark.asyncio
    async def test_add_item_variant_not_found(self, cart_service, mock_repos):
        """Test adding non-existent variant to cart fails"""
        # Arrange
        cart_id = uuid4()
        variant_id = uuid4()
        
        mock_cart = Cart(id=cart_id)
        mock_repos['cart_repo'].get_by_id = AsyncMock(return_value=mock_cart)
        mock_repos['variant_repo'].get_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Product variant not found"):
            await cart_service.add_item_to_cart(cart_id, variant_id, quantity=1)
    
    @pytest.mark.asyncio
    async def test_add_item_insufficient_stock(self, cart_service, mock_repos):
        """Test adding more items than available stock fails"""
        # Arrange
        cart_id = uuid4()
        variant_id = uuid4()
        
        mock_cart = Cart(id=cart_id)
        mock_repos['cart_repo'].get_by_id = AsyncMock(return_value=mock_cart)
        
        mock_variant = ProductVariant(
            id=variant_id,
            price_cents=1999,
            stock_quantity=5
        )
        mock_repos['variant_repo'].get_by_id = AsyncMock(return_value=mock_variant)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Insufficient stock"):
            await cart_service.add_item_to_cart(cart_id, variant_id, quantity=10)
    
    @pytest.mark.asyncio
    async def test_add_item_update_existing(self, cart_service, mock_repos):
        """Test adding item that exists in cart updates quantity"""
        # Arrange
        cart_id = uuid4()
        variant_id = uuid4()
        
        mock_cart = Cart(id=cart_id)
        mock_repos['cart_repo'].get_by_id = AsyncMock(return_value=mock_cart)
        
        mock_variant = ProductVariant(
            id=variant_id,
            price_cents=1999,
            stock_quantity=10
        )
        mock_repos['variant_repo'].get_by_id = AsyncMock(return_value=mock_variant)
        
        mock_existing_item = CartItem(
            id=uuid4(),
            cart_id=cart_id,
            variant_id=variant_id,
            quantity=2
        )
        mock_repos['cart_item_repo'].get_by_cart_and_variant = AsyncMock(return_value=mock_existing_item)
        mock_repos['cart_item_repo'].update = AsyncMock(return_value=mock_existing_item)
        
        # Act
        result = await cart_service.add_item_to_cart(cart_id, variant_id, quantity=3)
        
        # Assert
        assert result.quantity == 5  # 2 + 3
        mock_repos['cart_item_repo'].update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_cart_item_quantity(self, cart_service, mock_repos):
        """Test updating cart item quantity"""
        # Arrange
        item_id = uuid4()
        mock_item = CartItem(id=item_id, quantity=2)
        mock_repos['cart_item_repo'].get_by_id = AsyncMock(return_value=mock_item)
        mock_repos['cart_item_repo'].update = AsyncMock(return_value=mock_item)
        
        # Act
        result = await cart_service.update_cart_item_quantity(item_id, quantity=5)
        
        # Assert
        assert result.quantity == 5
        mock_repos['cart_item_repo'].update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_cart_item_invalid_quantity(self, cart_service, mock_repos):
        """Test updating cart item with invalid quantity fails"""
        # Arrange
        item_id = uuid4()
        mock_item = CartItem(id=item_id, quantity=2)
        mock_repos['cart_item_repo'].get_by_id = AsyncMock(return_value=mock_item)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Quantity must be positive"):
            await cart_service.update_cart_item_quantity(item_id, quantity=0)
    
    @pytest.mark.asyncio
    async def test_remove_cart_item(self, cart_service, mock_repos):
        """Test removing item from cart"""
        # Arrange
        item_id = uuid4()
        mock_item = CartItem(id=item_id)
        mock_repos['cart_item_repo'].get_by_id = AsyncMock(return_value=mock_item)
        mock_repos['cart_item_repo'].delete = AsyncMock()
        
        # Act
        await cart_service.remove_cart_item(item_id)
        
        # Assert
        mock_repos['cart_item_repo'].delete.assert_called_once_with(item_id)
    
    @pytest.mark.asyncio
    async def test_calculate_cart_total(self, cart_service, mock_repos):
        """Test calculating cart total"""
        # Arrange
        cart_id = uuid4()
        mock_items = [
            CartItem(id=uuid4(), cart_id=cart_id, quantity=2, price_cents=1999),
            CartItem(id=uuid4(), cart_id=cart_id, quantity=1, price_cents=4999),
            CartItem(id=uuid4(), cart_id=cart_id, quantity=3, price_cents=999)
        ]
        mock_repos['cart_item_repo'].get_by_cart = AsyncMock(return_value=mock_items)
        
        # Act
        total = await cart_service.calculate_cart_total(cart_id)
        
        # Assert
        # (2 * 1999) + (1 * 4999) + (3 * 999) = 3998 + 4999 + 2997 = 11994
        assert total == 11994
    
    @pytest.mark.asyncio
    async def test_clear_cart(self, cart_service, mock_repos):
        """Test clearing all items from cart"""
        # Arrange
        cart_id = uuid4()
        mock_items = [
            CartItem(id=uuid4(), cart_id=cart_id),
            CartItem(id=uuid4(), cart_id=cart_id),
            CartItem(id=uuid4(), cart_id=cart_id)
        ]
        mock_repos['cart_item_repo'].get_by_cart = AsyncMock(return_value=mock_items)
        mock_repos['cart_item_repo'].delete = AsyncMock()
        
        # Act
        await cart_service.clear_cart(cart_id)
        
        # Assert
        assert mock_repos['cart_item_repo'].delete.call_count == 3
    
    @pytest.mark.asyncio
    async def test_get_cart_items(self, cart_service, mock_repos):
        """Test retrieving all cart items"""
        # Arrange
        cart_id = uuid4()
        mock_items = [
            CartItem(id=uuid4(), cart_id=cart_id, quantity=2),
            CartItem(id=uuid4(), cart_id=cart_id, quantity=1)
        ]
        mock_repos['cart_item_repo'].get_by_cart = AsyncMock(return_value=mock_items)
        
        # Act
        result = await cart_service.get_cart_items(cart_id)
        
        # Assert
        assert len(result) == 2
        assert all(item.cart_id == cart_id for item in result)
