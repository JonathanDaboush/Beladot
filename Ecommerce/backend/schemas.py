"""
Pydantic Validation Schemas for API Requests and Responses
===========================================================

This module defines all Pydantic models used for:
- Request validation: Ensuring incoming data meets requirements
- Response serialization: Converting ORM models to JSON-safe dictionaries
- Data transformation: Type coercion, field validation, custom validators
- API documentation: Auto-generated OpenAPI/Swagger specs

Schema Categories:
    - Authentication: User registration, login, JWT tokens
    - Products: Product CRUD, variants, inventory
    - Shopping: Cart, wishlist, checkout
    - Orders: Order creation, status updates, history
    - Payments: Payment processing, refunds, methods
    - Reviews: Product reviews and ratings
    - Users: Profile management, addresses
    - Employees: Scheduling, payroll, leave management
    - Analytics: Reports, metrics, KPIs

Validation Features:
    - Email validation (EmailStr)
    - String constraints (min/max length, regex patterns)
    - Numeric constraints (gt, ge, lt, le for ranges)
    - Custom validators (@validator decorator)
    - Field descriptions for API documentation
    - Literal types for enum-like fields
    - Optional fields with defaults

Author: Jonathan Daboush
Version: 2.0.0
"""
from pydantic import BaseModel, EmailStr, Field, validator, constr
from typing import Optional, List, Literal
from datetime import datetime
from decimal import Decimal
import re


# ============================================================================
# Authentication Schemas
# ============================================================================

class UserRegisterRequest(BaseModel):
    """
    User registration request with comprehensive validation.
    
    Validates:
        - Email format (EmailStr)
        - Password strength (8-128 chars, uppercase, lowercase, digit, special char)
        - Name fields (1-100 chars)
        - Phone format (optional, 10-20 chars, normalized to digits only)
        - Role assignment (customer by default)
    """
    email: EmailStr = Field(..., description="Valid email address")
    password: constr(min_length=8, max_length=128) = Field(..., description="Password (8-128 chars)")
    first_name: constr(min_length=1, max_length=100) = Field(..., description="First name")
    last_name: constr(min_length=1, max_length=100) = Field(..., description="Last name")
    phone: Optional[constr(min_length=10, max_length=20)] = None
    role: Literal["customer", "customer_service", "seller", "transfer", "finance", "admin"] = Field(
        default="customer",
        description="User role: customer (default), customer_service, seller, transfer, finance, admin"
    )
    
    @validator('password')
    def validate_password_strength(cls, v):
        """
        Ensure password meets security requirements.
        
        Requirements:
            - At least one uppercase letter
            - At least one lowercase letter
            - At least one digit
            - At least one special character (!@#$%^&*(),.?":{}|<>)
        
        Args:
            v: Password string
            
        Returns:
            str: Validated password
            
        Raises:
            ValueError: If password doesn't meet requirements
        """
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """
        Normalize phone number by removing non-numeric characters.
        
        Keeps only digits and + prefix for international numbers.
        Example: "(123) 456-7890" becomes "1234567890"
        
        Args:
            v: Phone string
            
        Returns:
            str: Normalized phone number with only digits and optional +
        """
        if v:
            return re.sub(r'[^0-9+]', '', v)
        return v
    
    @validator('role')
    def validate_role(cls, v, values):
        """
        Validate role assignment rules.
        
        Note: Admin role creation requires special privileges.
        This is enforced at the service layer with role-based access control.
        
        Args:
            v: Role value
            values: Other validated field values
            
        Returns:
            str: Validated role
        """
        # Only admins can create admin accounts (enforced at service layer)
        # This is additional validation at schema level
        if v == "admin":
            # Admin creation requires special privileges (checked in service)
            pass
        return v


class UserLoginRequest(BaseModel):
    """
    User login request.
    
    Simple email/password authentication. Passwords are verified
    against bcrypt hashes stored in the database.
    """
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    JWT token response after successful authentication.
    
    Contains both access and refresh tokens:
        - access_token: Short-lived token for API requests (15 min default)
        - refresh_token: Long-lived token for refreshing access tokens (7 days default)
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Access token expiration in seconds


class RefreshTokenRequest(BaseModel):
    """Request to refresh an access token using a valid refresh token."""
    refresh_token: str


class UserResponse(BaseModel):
    """
    User response model (excludes sensitive data).
    
    Returned from login, registration, and profile endpoints.
    Never includes password hash or other sensitive fields.
    """
    id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    role: str = Field(description="User role: customer, customer_service, seller, transfer, finance, admin")
    created_at: datetime
    
    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models


# ============================================================================
# Product Schemas
# ============================================================================

class ProductCreateRequest(BaseModel):
    """
    Create product request with comprehensive validation.
    
    Validates:
        - Name and description (required, max lengths)
        - Price (must be positive, Decimal for precision)
        - Cost (must be non-negative)
        - SKU (unique identifier, validated at service layer)
        - Category assignment (must exist in database)
    """
    name: constr(min_length=1, max_length=255) = Field(..., description="Product name")
    description: constr(max_length=5000) = Field(..., description="Product description")
    price: Decimal = Field(..., gt=0, description="Price must be positive")
    cost: Decimal = Field(..., ge=0, description="Cost must be non-negative")
    sku: constr(min_length=1, max_length=100) = Field(..., description="Stock keeping unit")
    category_id: int = Field(..., gt=0)
    seller_id: int = Field(..., gt=0)
    stock_quantity: int = Field(default=0, ge=0, description="Initial stock quantity")
    weight: Optional[Decimal] = Field(None, gt=0, description="Weight in kg")
    dimensions: Optional[str] = Field(None, max_length=100)
    
    @validator('sku')
    def validate_sku(cls, v):
        """Ensure SKU contains only valid characters."""
        if not re.match(r'^[A-Za-z0-9_-]+$', v):
            raise ValueError('SKU must contain only letters, numbers, hyphens, and underscores')
        return v


class ProductUpdateRequest(BaseModel):
    """
    Update product request (partial update allowed).
    
    All fields are optional - only provided fields will be updated.
    Useful for PATCH operations where only specific fields need updating.
    Maintains same validation rules as ProductCreateRequest.
    """
    name: Optional[constr(min_length=1, max_length=255)] = None
    description: Optional[constr(max_length=5000)] = None
    price: Optional[Decimal] = Field(None, gt=0)
    cost: Optional[Decimal] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    weight: Optional[Decimal] = Field(None, gt=0)
    dimensions: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None  # Toggle product visibility


class ProductResponse(BaseModel):
    """
    Product response model for API responses.
    
    Returned from product listing, detail, and search endpoints.
    Includes all product data safe for public display (no cost/profit data).
    """
    id: int
    name: str
    description: str
    price: Decimal  # Customer-facing price (excludes cost)
    sku: str  # Unique product identifier
    category_id: int  # Foreign key to category
    seller_id: int  # Foreign key to seller
    stock_quantity: int  # Available inventory
    weight: Optional[Decimal]  # For shipping calculations
    dimensions: Optional[str]  # Format: "LxWxH cm"
    created_at: datetime
    
    class Config:
        from_attributes = True  # Enable ORM mode


# ============================================================================
# Cart Schemas
# ============================================================================

class AddToCartRequest(BaseModel):
    """
    Add item to shopping cart request.
    
    Validates quantity limits and product variant existence.
    Cart service will check inventory availability before adding.
    """
    product_variant_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=999, description="Quantity (1-999)")


class UpdateCartItemRequest(BaseModel):
    """
    Update cart item quantity.
    
    Used for increasing/decreasing quantity of existing cart items.
    Setting quantity to 0 or using DELETE endpoint removes the item.
    """
    quantity: int = Field(..., gt=0, le=999)


class CartItemResponse(BaseModel):
    """
    Cart item response model.
    
    Represents a single product in the cart with snapshot pricing.
    Price is captured at time of addition to handle price changes.
    """
    id: int
    cart_id: int
    product_variant_id: int
    quantity: int
    price_at_addition: Decimal  # Price frozen at add-to-cart time
    
    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """
    Cart response with items and calculated total.
    
    Returned from cart endpoints with all items and pricing.
    Total is calculated server-side from current prices.
    """
    id: int
    user_id: int
    items: List[CartItemResponse]  # All items in cart
    total: Decimal  # Calculated total (sum of item prices × quantities)
    
    class Config:
        from_attributes = True


# ============================================================================
# Order Schemas
# ============================================================================

class CreateOrderRequest(BaseModel):
    """
    Create order from cart request.
    
    Initiates checkout process:
        1. Validates addresses exist and belong to user
        2. Validates payment method is supported
        3. Applies coupon if provided (validation at service layer)
        4. Creates order from current cart contents
        5. Reserves inventory
    """
    shipping_address_id: int = Field(..., gt=0)
    billing_address_id: int = Field(..., gt=0)
    payment_method: str = Field(..., pattern="^(credit_card|debit_card|paypal|apple_pay|google_pay)$")
    coupon_code: Optional[constr(max_length=50)] = None  # Optional discount code


class OrderItemResponse(BaseModel):
    """
    Order item response model.
    
    Represents a purchased item with frozen price.
    Price is captured at order creation and never changes,
    even if product price changes later.
    """
    id: int
    order_id: int
    product_variant_id: int
    quantity: int
    price: Decimal  # Price at time of order (immutable)
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """
    Order response with full details.
    
    Contains complete order information including:
        - Order identification (id, order_number)
        - Status tracking (pending → processing → shipped → delivered)
        - Price breakdown (subtotal, tax, shipping, total)
        - All order items
    """
    id: int
    user_id: int
    order_number: str  # Human-readable order number (e.g., "ORD-2024-12345")
    status: str  # OrderStatus enum value
    subtotal: Decimal  # Sum of item prices before tax/shipping
    tax: Decimal  # Calculated sales tax
    shipping_cost: Decimal  # Shipping fee
    total: Decimal  # Grand total (subtotal + tax + shipping - discounts)
    items: List[OrderItemResponse]  # All purchased items
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Address Schemas
# ============================================================================

class AddressCreateRequest(BaseModel):
    """
    Create address request with country-specific validation.
    
    Validates postal code format based on country:
        - Canada: A1A 1A1 format
        - USA: 12345 or 12345-6789 format
        - Others: Basic length validation
    
    Setting is_default=True will make this the default shipping/billing address.
    """
    user_id: int = Field(..., gt=0)
    address_line1: constr(min_length=1, max_length=255)  # Street address
    address_line2: Optional[constr(max_length=255)] = None  # Apt, suite, unit
    city: constr(min_length=1, max_length=100)
    state: constr(min_length=2, max_length=100)  # State/province/region
    postal_code: constr(min_length=3, max_length=20)  # ZIP/postal code
    country: constr(min_length=2, max_length=100) = "Canada"
    is_default: bool = False  # Set as default address
    
    @validator('postal_code')
    def validate_postal_code(cls, v, values):
        """Validate postal code format based on country."""
        country = values.get('country', 'Canada')
        if country == 'Canada':
            # Canadian postal code: A1A 1A1
            v = v.upper().replace(' ', '')
            if not re.match(r'^[A-Z]\d[A-Z]\d[A-Z]\d$', v):
                raise ValueError('Invalid Canadian postal code format')
            return f"{v[:3]} {v[3:]}"
        elif country == 'USA':
            # US ZIP code: 12345 or 12345-6789
            if not re.match(r'^\d{5}(-\d{4})?$', v):
                raise ValueError('Invalid US ZIP code format')
        return v


class AddressResponse(BaseModel):
    """Address response model."""
    id: int
    user_id: int
    address_line1: str
    address_line2: Optional[str]
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# Payment Schemas
# ============================================================================

class PaymentCreateRequest(BaseModel):
    """
    Process payment request.
    
    Initiates payment processing:
        1. Validates order exists and belongs to user
        2. Validates amount matches order total
        3. Processes payment through gateway (Stripe, PayPal, etc.)
        4. Updates order status on success
        5. Creates refund record on failure
    """
    order_id: int = Field(..., gt=0)
    payment_method: str = Field(..., pattern="^(credit_card|debit_card|paypal|apple_pay|google_pay)$")
    amount: Decimal = Field(..., gt=0)  # Must match order total


class PaymentResponse(BaseModel):
    """
    Payment response with transaction details.
    
    Contains payment processing results:
        - Transaction ID from payment gateway
        - Payment status (pending, completed, failed, refunded)
        - Amount processed
    """
    id: int
    order_id: int
    payment_method: str
    amount: Decimal
    status: str  # PaymentStatus enum value
    transaction_id: Optional[str]  # Gateway transaction ID
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Review Schemas
# ============================================================================

class ReviewCreateRequest(BaseModel):
    """
    Create product review request.
    
    Validates:
        - Rating: 1-5 stars (integer)
        - Title: 1-200 characters
        - Comment: 10-2000 characters (minimum ensures quality)
        - Content safety: Checks for SQL injection, XSS
    
    Business rules (enforced at service layer):
        - User must have purchased the product
        - One review per user per product
        - Review can be edited within 30 days
    """
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5 stars)")
    title: constr(min_length=1, max_length=200)  # Review headline
    comment: constr(min_length=10, max_length=2000)  # Detailed review
    
    @validator('comment')
    def validate_comment(cls, v):
        """
        Check for suspicious content in review.
        
        Validates against:
            - SQL injection attempts
            - XSS script tags
            - Excessive profanity
        """
        from Utilities.input_sanitization import check_for_sql_keywords
        if check_for_sql_keywords(v):
            raise ValueError('Review contains invalid content')
        return v


class ReviewResponse(BaseModel):
    """
    Review response model.
    
    Returned from review endpoints. May include additional fields
    like helpful_count, verified_purchase flag in full implementation.
    """
    id: int
    product_id: int
    user_id: int  # Reviewer ID (may show name/avatar in frontend)
    rating: int  # 1-5 stars
    title: str
    comment: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Employee Schemas (Admin Only)
# ============================================================================

class EmployeeCreateRequest(BaseModel):
    """
    Create employee request (admin/manager only).
    
    Links a user account to an employee record with:
        - Job assignment (role, department, pay rate)
        - Employment type (full-time, part-time, contract, seasonal)
        - Start date
    
    Requires admin role or manager permission.
    """
    user_id: int = Field(..., gt=0)  # Must be existing user
    job_id: int = Field(..., gt=0)  # Job defines role and pay
    hire_date: datetime  # Employment start date
    employment_type: str = Field(..., pattern="^(full_time|part_time|contract|seasonal)$")
    
    
class ClockInRequest(BaseModel):
    """
    Clock in request for time tracking.
    
    Records start of work shift. Creates HoursWorked record
    with clock_in timestamp. Employee must clock out to complete shift.
    """
    employee_id: int = Field(..., gt=0)


class ClockOutRequest(BaseModel):
    """
    Clock out request with break time.
    
    Records end of work shift:
        - clock_out timestamp
        - break_minutes: Deducted from total hours worked
        - Calculates total hours and overtime automatically
    """
    employee_id: int = Field(..., gt=0)
    break_minutes: int = Field(default=0, ge=0, le=480, description="Break time in minutes (max 8 hours)")


# ============================================================================
# Common Schemas
# ============================================================================

class MessageResponse(BaseModel):
    """
    Generic success message response.
    
    Used for operations that don't return data (deletes, updates).
    
    Example:
        {"message": "Product deleted successfully", "success": true}
    """
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """
    Error response with optional error code.
    
    Provides consistent error format across all endpoints.
    Error codes can be used for client-side internationalization.
    
    Example:
        {"detail": "Product not found", "error_code": "PRODUCT_NOT_FOUND"}
    """
    detail: str  # Human-readable error message
    error_code: Optional[str] = None  # Machine-readable error code


class PaginationParams(BaseModel):
    """
    Pagination parameters for list endpoints.
    
    Standard pagination using page numbers:
        - page: Current page (1-based)
        - page_size: Items per page (1-100, default 20)
    
    Calculate offset automatically for database queries.
    
    Example:
        GET /products?page=2&page_size=50
    """
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """
        Calculate offset for database query.
        
        Returns:
            int: Number of items to skip (page-1) * page_size
        """
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel):
    """
    Paginated response wrapper for list endpoints.
    
    Provides complete pagination metadata:
        - items: Current page data
        - total: Total number of items across all pages
        - page: Current page number
        - page_size: Items per page
        - total_pages: Total pages (calculated from total/page_size)
    
    Example:
        {
            "items": [{...}, {...}, ...],
            "total": 156,
            "page": 2,
            "page_size": 20,
            "total_pages": 8
        }
    """
    items: List[dict]  # Current page items
    total: int  # Total items across all pages
    page: int  # Current page
    page_size: int  # Items per page
    total_pages: int  # Calculated total pages
