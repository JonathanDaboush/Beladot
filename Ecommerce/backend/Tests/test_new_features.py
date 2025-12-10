"""
Test Suite for New Features
Tests for: Email notifications, Image uploads, Reviews, Wishlist, Password Reset, Search Filters
"""
import pytest
from httpx import AsyncClient
from fastapi import status
import os
from pathlib import Path
import io
from PIL import Image

# Base URL for testing
BASE_URL = "http://localhost:8000"


# ============================================================================
# PASSWORD RESET TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_forgot_password_flow(async_client: AsyncClient, test_user):
    """Test forgot password request"""
    response = await async_client.post(
        "/api/auth/forgot-password",
        params={"email": test_user["email"]}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_forgot_password_nonexistent_email(async_client: AsyncClient):
    """Test forgot password with non-existent email (should not reveal if email exists)"""
    response = await async_client.post(
        "/api/auth/forgot-password",
        params={"email": "nonexistent@example.com"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_reset_password_with_valid_token(async_client: AsyncClient, test_user, password_reset_token):
    """Test password reset with valid token"""
    response = await async_client.post(
        "/api/auth/reset-password",
        params={
            "reset_token": password_reset_token,
            "new_password": "NewSecurePassword123!"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Password reset successfully"


@pytest.mark.asyncio
async def test_reset_password_with_invalid_token(async_client: AsyncClient):
    """Test password reset with invalid token"""
    response = await async_client.post(
        "/api/auth/reset-password",
        params={
            "reset_token": "invalid_token_12345",
            "new_password": "NewPassword123!"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# IMAGE UPLOAD TESTS
# ============================================================================

def create_test_image():
    """Create a test image in memory"""
    img = Image.new('RGB', (800, 600), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


@pytest.mark.asyncio
async def test_upload_product_image(async_client: AsyncClient, auth_headers, test_product):
    """Test uploading a single product image"""
    img_bytes = create_test_image()
    
    response = await async_client.post(
        "/api/upload/product-image",
        data={"product_id": test_product["id"]},
        files={"file": ("test_image.jpg", img_bytes, "image/jpeg")},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "image_url" in data
    assert "thumbnail_url" in data
    assert data["message"] == "Image uploaded successfully"


@pytest.mark.asyncio
async def test_upload_multiple_product_images(async_client: AsyncClient, auth_headers, test_product):
    """Test uploading multiple product images"""
    files = [
        ("files", ("image1.jpg", create_test_image(), "image/jpeg")),
        ("files", ("image2.jpg", create_test_image(), "image/jpeg")),
        ("files", ("image3.jpg", create_test_image(), "image/jpeg"))
    ]
    
    response = await async_client.post(
        "/api/upload/product-images-bulk",
        data={"product_id": test_product["id"]},
        files=files,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["uploaded_count"] == 3
    assert len(data["images"]) == 3


@pytest.mark.asyncio
async def test_upload_image_invalid_format(async_client: AsyncClient, auth_headers, test_product):
    """Test uploading invalid file format"""
    text_file = io.BytesIO(b"This is not an image")
    
    response = await async_client.post(
        "/api/upload/product-image",
        data={"product_id": test_product["id"]},
        files={"file": ("test.txt", text_file, "text/plain")},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_upload_image_too_large(async_client: AsyncClient, auth_headers, test_product):
    """Test uploading image exceeding size limit"""
    # Create image larger than 5MB
    large_img = Image.new('RGB', (10000, 10000), color='blue')
    img_bytes = io.BytesIO()
    large_img.save(img_bytes, format='JPEG', quality=100)
    img_bytes.seek(0)
    
    response = await async_client.post(
        "/api/upload/product-image",
        data={"product_id": test_product["id"]},
        files={"file": ("large_image.jpg", img_bytes, "image/jpeg")},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_delete_product_image(async_client: AsyncClient, auth_headers, test_product_image):
    """Test deleting a product image"""
    response = await async_client.delete(
        f"/api/upload/product-image/{test_product_image['id']}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Image deleted successfully"


# ============================================================================
# REVIEWS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_review(async_client: AsyncClient, auth_headers, test_product, delivered_order):
    """Test creating a product review"""
    review_data = {
        "product_id": test_product["id"],
        "rating": 5,
        "title": "Excellent product!",
        "comment": "This product exceeded my expectations. Highly recommend!"
    }
    
    response = await async_client.post(
        "/api/reviews",
        json=review_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["rating"] == 5
    assert data["title"] == "Excellent product!"


@pytest.mark.asyncio
async def test_create_review_without_purchase(async_client: AsyncClient, auth_headers, test_product):
    """Test creating review for product not purchased"""
    review_data = {
        "product_id": test_product["id"],
        "rating": 5,
        "title": "Great!",
        "comment": "Amazing product"
    }
    
    response = await async_client.post(
        "/api/reviews",
        json=review_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_create_review_invalid_rating(async_client: AsyncClient, auth_headers, test_product):
    """Test creating review with invalid rating"""
    review_data = {
        "product_id": test_product["id"],
        "rating": 6,  # Invalid: must be 1-5
        "title": "Test",
        "comment": "Test comment"
    }
    
    response = await async_client.post(
        "/api/reviews",
        json=review_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_get_product_reviews(async_client: AsyncClient, test_product):
    """Test fetching reviews for a product"""
    response = await async_client.get(f"/api/reviews/product/{test_product['id']}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "reviews" in data
    assert "summary" in data
    assert "total_reviews" in data["summary"]
    assert "average_rating" in data["summary"]


@pytest.mark.asyncio
async def test_get_product_reviews_with_filters(async_client: AsyncClient, test_product):
    """Test fetching reviews with filters"""
    response = await async_client.get(
        f"/api/reviews/product/{test_product['id']}",
        params={"min_rating": 4, "sort_by": "helpful", "limit": 10}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "reviews" in data


@pytest.mark.asyncio
async def test_update_review(async_client: AsyncClient, auth_headers, test_review):
    """Test updating own review"""
    update_data = {
        "rating": 4,
        "title": "Updated title",
        "comment": "Updated comment"
    }
    
    response = await async_client.put(
        f"/api/reviews/{test_review['id']}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["rating"] == 4
    assert data["title"] == "Updated title"


@pytest.mark.asyncio
async def test_delete_review(async_client: AsyncClient, auth_headers, test_review):
    """Test deleting own review"""
    response = await async_client.delete(
        f"/api/reviews/{test_review['id']}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_mark_review_helpful(async_client: AsyncClient, auth_headers, test_review):
    """Test marking a review as helpful"""
    response = await async_client.post(
        f"/api/reviews/{test_review['id']}/helpful",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "helpful_count" in data


# ============================================================================
# WISHLIST TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_get_empty_wishlist(async_client: AsyncClient, auth_headers):
    """Test getting empty wishlist"""
    response = await async_client.get("/api/wishlist", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_items"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_add_to_wishlist(async_client: AsyncClient, auth_headers, test_product):
    """Test adding product to wishlist"""
    response = await async_client.post(
        "/api/wishlist",
        json={"product_id": test_product["id"]},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "item_id" in data
    assert data["message"] == "Product added to wishlist"


@pytest.mark.asyncio
async def test_add_to_wishlist_duplicate(async_client: AsyncClient, auth_headers, test_product):
    """Test adding same product twice to wishlist"""
    # Add first time
    await async_client.post(
        "/api/wishlist",
        json={"product_id": test_product["id"]},
        headers=auth_headers
    )
    
    # Add second time
    response = await async_client.post(
        "/api/wishlist",
        json={"product_id": test_product["id"]},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert "already in wishlist" in response.json()["message"]


@pytest.mark.asyncio
async def test_get_wishlist_with_items(async_client: AsyncClient, auth_headers, wishlist_with_items):
    """Test getting wishlist with items"""
    response = await async_client.get("/api/wishlist", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_items"] > 0
    assert len(data["items"]) > 0
    assert "product" in data["items"][0]


@pytest.mark.asyncio
async def test_remove_from_wishlist(async_client: AsyncClient, auth_headers, wishlist_item):
    """Test removing item from wishlist"""
    response = await async_client.delete(
        f"/api/wishlist/{wishlist_item['id']}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Product removed from wishlist"


@pytest.mark.asyncio
async def test_move_wishlist_item_to_cart(async_client: AsyncClient, auth_headers, wishlist_item):
    """Test moving wishlist item to cart"""
    response = await async_client.post(
        f"/api/wishlist/{wishlist_item['id']}/move-to-cart",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Product moved to cart"
    assert "cart_item_id" in data


@pytest.mark.asyncio
async def test_clear_wishlist(async_client: AsyncClient, auth_headers, wishlist_with_items):
    """Test clearing entire wishlist"""
    response = await async_client.delete("/api/wishlist", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Wishlist cleared successfully"


# ============================================================================
# SEARCH FILTERS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_search_products_basic(async_client: AsyncClient):
    """Test basic product search"""
    response = await async_client.get(
        "/api/search/products",
        params={"query": "laptop"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "results" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_search_products_with_price_filter(async_client: AsyncClient):
    """Test search with price range filter"""
    response = await async_client.get(
        "/api/search/products",
        params={
            "query": "laptop",
            "min_price": 50000,  # $500
            "max_price": 150000  # $1500
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "results" in data


@pytest.mark.asyncio
async def test_search_products_with_rating_filter(async_client: AsyncClient):
    """Test search with minimum rating filter"""
    response = await async_client.get(
        "/api/search/products",
        params={
            "query": "laptop",
            "min_rating": 4.0
        }
    )
    
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_search_products_in_stock_only(async_client: AsyncClient):
    """Test search with in-stock filter"""
    response = await async_client.get(
        "/api/search/products",
        params={
            "query": "laptop",
            "in_stock_only": True
        }
    )
    
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_search_products_with_category(async_client: AsyncClient):
    """Test search filtered by category"""
    response = await async_client.get(
        "/api/search/products",
        params={
            "query": "laptop",
            "category": "Electronics"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_search_products_sorting(async_client: AsyncClient):
    """Test search with different sorting options"""
    sort_options = ["relevance", "price_asc", "price_desc", "rating", "newest"]
    
    for sort_by in sort_options:
        response = await async_client.get(
            "/api/search/products",
            params={
                "query": "laptop",
                "sort_by": sort_by
            }
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_search_products_pagination(async_client: AsyncClient):
    """Test search with pagination"""
    response = await async_client.get(
        "/api/search/products",
        params={
            "query": "laptop",
            "limit": 10,
            "offset": 0
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["limit"] == 10
    assert data["offset"] == 0


# ============================================================================
# EMAIL NOTIFICATION TESTS (Mock)
# ============================================================================

@pytest.mark.asyncio
async def test_order_confirmation_email_sent(async_client: AsyncClient, auth_headers, mocker):
    """Test that order confirmation email is sent"""
    mock_send_email = mocker.patch('Utilities.email_service.send_order_confirmation')
    
    # Create order
    order_data = {
        "shipping_address_id": "test_address_id",
        "payment_method": "credit_card"
    }
    
    response = await async_client.post(
        "/api/orders",
        json=order_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    # Verify email function was called
    mock_send_email.assert_called_once()


@pytest.mark.asyncio
async def test_shipping_update_email_sent(async_client: AsyncClient, admin_headers, test_shipment, mocker):
    """Test that shipping update email is sent"""
    mock_send_email = mocker.patch('Utilities.email_service.send_shipping_update')
    
    # Update shipment status
    response = await async_client.put(
        f"/api/transfer/shipments/{test_shipment['id']}/status",
        params={"status": "shipped"},
        headers=admin_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    # Verify email function was called
    mock_send_email.assert_called_once()


@pytest.mark.asyncio
async def test_password_reset_email_sent(async_client: AsyncClient, test_user, mocker):
    """Test that password reset email is sent"""
    mock_send_email = mocker.patch('Utilities.email_service.send_password_reset')
    
    response = await async_client.post(
        "/api/auth/forgot-password",
        params={"email": test_user["email"]}
    )
    
    assert response.status_code == status.HTTP_200_OK
    # Verify email function was called
    mock_send_email.assert_called_once()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_full_wishlist_to_cart_flow(async_client: AsyncClient, auth_headers, test_product):
    """Test complete flow: add to wishlist -> move to cart -> checkout"""
    # 1. Add to wishlist
    response = await async_client.post(
        "/api/wishlist",
        json={"product_id": test_product["id"]},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    item_id = response.json()["item_id"]
    
    # 2. Move to cart
    response = await async_client.post(
        f"/api/wishlist/{item_id}/move-to-cart",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    # 3. Verify in cart
    response = await async_client.get("/api/cart", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    cart_data = response.json()
    assert len(cart_data["items"]) > 0


@pytest.mark.asyncio
async def test_full_review_workflow(async_client: AsyncClient, auth_headers, test_product, delivered_order):
    """Test complete review workflow: create -> update -> mark helpful -> delete"""
    # 1. Create review
    review_data = {
        "product_id": test_product["id"],
        "rating": 5,
        "title": "Great product",
        "comment": "Very satisfied"
    }
    response = await async_client.post("/api/reviews", json=review_data, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    review_id = response.json()["id"]
    
    # 2. Update review
    response = await async_client.put(
        f"/api/reviews/{review_id}",
        json={"rating": 4, "title": "Updated title"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    # 3. Mark as helpful
    response = await async_client.post(f"/api/reviews/{review_id}/helpful", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # 4. Delete review
    response = await async_client.delete(f"/api/reviews/{review_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
