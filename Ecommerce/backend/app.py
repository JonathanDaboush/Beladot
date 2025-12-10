"""
FastAPI E-Commerce Backend Application

Production-ready e-commerce API with clean architecture and comprehensive
business logic separation. All business rules are implemented in the Service
layer, with routers handling HTTP concerns only.

Architecture:
    Request → Middleware → Router → Service → Repository → Model → Database

Key Features:
    - JWT Authentication & Authorization
    - Role-Based Access Control (9 user roles)
    - Department-Scoped Authorization for managers
    - Input Validation (Pydantic schemas)
    - Rate Limiting (per-endpoint)
    - CSRF Protection
    - Security Headers (HSTS, CSP, etc.)
    - CORS Configuration
    - Async/Await throughout
    - Comprehensive audit logging

Security Features:
    - JWT tokens with refresh token rotation
    - Password hashing with bcrypt
    - SQL injection prevention (parameterized queries)
    - XSS protection (input sanitization)
    - Rate limiting to prevent abuse
    - CSRF token validation
    - Secure session management
    - HTTPS enforcement in production

Business Domains:
    - Authentication & User Management
    - Product Catalog & Inventory
    - Shopping Cart & Checkout
    - Order Management & Fulfillment
    - Payment Processing
    - Seller Portal
    - Employee Management (scheduling, payroll, time tracking)
    - Analytics & Reporting
    - Customer Service Tools

Routers (31 total):
    Authentication, Cart, Catalog, Checkout, Orders, Payments, Shipping,
    Fulfillment, Products, Search, Seller, Transfer, Finance, Payroll,
    Scheduling, Leave, Analytics, Customer Service, Admin, Manager, Employee

Services (20 total):
    User, Cart, Catalog, Checkout, Order, Payment, Fulfillment, Inventory,
    Pricing, Shipping, Search, Seller, Analytics, Payroll, Scheduling,
    TimeTracking, LeaveManagement, Notification, CurrencyConversion,
    SimpleInventory

Author: Jonathan Daboush
Version: 2.0.0
Last Updated: December 7, 2025
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import uuid
import os

from config import Settings
from database import async_engine

# ============================================================================
# ROUTER IMPORTS
# ============================================================================
# Import all routers for endpoint registration
from routers import (
    auth, cart, products, orders, customer_service, seller, transfer, finance, admin,
    checkout, payments, payroll, scheduling, leave, shipping, search, analytics, payment_methods, analyst,
    manager, employee, manager_approvals, cart_extended, checkout_extended, payments_extended,
    scheduling_extended, payroll_extended, seller_extended, catalog, fulfillment, upload, reviews, wishlist
)

# ============================================================================
# UTILITY IMPORTS
# ============================================================================
# Import utilities for middleware and cleanup
from Utilities.rate_limiting import cleanup_rate_limit_store
from Utilities.csrf_protection import cleanup_expired_tokens

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================
settings = Settings()

# Create FastAPI application instance
app = FastAPI(
    title="E-Commerce API",
    description="Production-ready e-commerce backend with comprehensive security",
    version="2.0.0",
    docs_url="/docs" if settings.environment == "development" else None,  # Disable docs in production
    redoc_url="/redoc" if settings.environment == "development" else None  # Disable ReDoc in production
)

# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================
# Middleware is executed in the order it's added (top to bottom for requests)

# CORS Middleware - Allow cross-origin requests from configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # Allowed origins from .env
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # Allowed HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["X-Request-ID", "X-CSRF-Token"]  # Headers visible to client
)

# Trusted Host Middleware - Prevent Host header attacks (production only)
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts  # Only allow requests to these hosts
    )


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Add security headers to all responses.
    
    Headers added:
        - Strict-Transport-Security: Enforce HTTPS
        - Content-Security-Policy: Prevent XSS attacks
        - X-Frame-Options: Prevent clickjacking
        - X-Content-Type-Options: Prevent MIME sniffing
        - X-XSS-Protection: Enable browser XSS protection
        - Referrer-Policy: Control referrer information
        - Permissions-Policy: Restrict browser features
    
    Args:
        request: Incoming HTTP request
        call_next: Next middleware/route handler
        
    Returns:
        Response with added security headers
    """
    response = await call_next(request)
    
    # Strict-Transport-Security (HSTS) - Force HTTPS for 1 year including subdomains
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Content Security Policy - Prevent XSS attacks by restricting resource loading
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "  # Only load resources from same origin by default
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # Allow scripts (unsafe-eval needed for some frameworks)
        "style-src 'self' 'unsafe-inline'; "  # Allow styles from same origin + inline
        "img-src 'self' data: https:; "  # Allow images from same origin, data URIs, and HTTPS
        "font-src 'self' data:; "  # Allow fonts from same origin and data URIs
        "connect-src 'self'"  # API calls only to same origin
    )
    
    # X-Frame-Options (Clickjacking protection) - Prevent page from being embedded in iframe
    response.headers["X-Frame-Options"] = "DENY"
    
    # X-Content-Type-Options - Prevent MIME sniffing attacks
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # X-XSS-Protection - Enable browser XSS protection filter
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Referrer-Policy - Control referrer information sent in requests
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Permissions-Policy - Restrict browser features for security
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=(), payment=(self)"
    )
    
    return response


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """
    Add unique request ID to each request for tracing and debugging.
    
    The request ID:
        - Is generated as a UUID4 for global uniqueness
        - Is stored in request.state for access in route handlers
        - Is added to response headers for client-side tracing
        - Should be included in all log messages for this request
    
    Args:
        request: Incoming HTTP request
        call_next: Next middleware/route handler
        
    Returns:
        Response with X-Request-ID header
    """
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response


# ============================================================================
# LIFECYCLE EVENTS
# ============================================================================
# Startup and shutdown events for resource initialization and cleanup

@app.on_event("startup")
async def startup_event():
    """
    Initialize resources on application startup.
    
    Performs:
        - Logs application start with environment info
        - Logs database connection info (masked for security)
        - Can be extended for cache warming, DB connection testing, etc.
    """
    logger.info("🚀 Starting E-Commerce API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'configured'}")
    logger.info("✅ Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup resources on application shutdown.
    
    Performs:
        - Clears rate limiting store
        - Removes expired CSRF tokens
        - Closes database connection pool
        - Logs shutdown completion
    """
    logger.info("🛑 Shutting down E-Commerce API...")
    
    # Cleanup rate limiting store (in-memory tracking)
    cleanup_rate_limit_store()
    
    # Cleanup CSRF tokens (remove expired tokens)
    cleanup_expired_tokens()
    
    # Close database connections (graceful pool shutdown)
    await async_engine.dispose()
    
    logger.info("✅ Application shutdown complete")


# ============================================================================
# BASIC ROUTES
# ============================================================================
# Health check and root endpoint

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring tools.
    
    Returns:
        dict: Status information including environment
        
    Example:
        GET /health
        Response: {"status": "healthy", "environment": "production"}
    """
    return {"status": "healthy", "environment": settings.environment}


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information and documentation links.
    
    Returns:
        dict: API metadata including name, version, status, and docs URL
        
    Example:
        GET /
        Response: {
            "name": "E-Commerce API",
            "version": "2.0.0",
            "status": "running",
            "docs": "/docs"
        }
    """
    return {
        "name": "E-Commerce API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs" if settings.environment == "development" else "disabled"
    }


# ============================================================================
# ROUTER REGISTRATION
# ============================================================================
# All business domain routers are registered here
# Each router handles a specific domain (auth, products, orders, etc.)

# Authentication & Authorization
app.include_router(auth.router)  # Login, registration, password reset, JWT token management

# Shopping Experience
app.include_router(cart.router)  # Shopping cart: add items, update quantities, clear cart
app.include_router(cart_extended.router)  # Cart analytics, saved carts, cart recovery
app.include_router(products.router)  # Product CRUD, variants, inventory management
app.include_router(catalog.router)  # Product listing, filtering, search, categories
app.include_router(search.router)  # Advanced search, filters, sorting

# Order Management
app.include_router(orders.router)  # Order CRUD, status updates, order history
app.include_router(checkout.router)  # Checkout process, payment, order creation
app.include_router(checkout_extended.router)  # Guest checkout, express checkout, order summary

# Payments & Financial
app.include_router(payments.router)  # Payment processing, refunds, payment status
app.include_router(payments_extended.router)  # Payment methods, tokenization, installments
app.include_router(payment_methods.router)  # Saved payment methods, wallet management

# Fulfillment & Shipping
app.include_router(shipping.router)  # Shipping rates, carriers, tracking
app.include_router(fulfillment.router)  # Order fulfillment, shipping labels, returns

# File Upload
app.include_router(upload.router)  # Product images, file uploads

# Customer Support
app.include_router(customer_service.router)  # Tickets, reviews, wishlists, returns
app.include_router(reviews.router)  # Product reviews and ratings
app.include_router(wishlist.router)  # User wishlist management

# Seller Portal
app.include_router(seller.router)  # Seller registration, products, orders, payouts
app.include_router(seller_extended.router)  # Seller analytics, performance metrics, settlements

# Financial Management
app.include_router(transfer.router)  # Fund transfers, withdrawals, deposits
app.include_router(finance.router)  # Financial reports, revenue, profit analysis

# Employee Management
app.include_router(payroll.router)  # Payroll processing, salary calculations, pay stubs
app.include_router(payroll_extended.router)  # Tax documents, bonuses, deductions
app.include_router(scheduling.router)  # Employee scheduling, shifts, availability
app.include_router(scheduling_extended.router)  # Shift swaps, time-off requests, overtime
app.include_router(leave.router)  # PTO, sick leave, leave requests, approvals

# Analytics & Reporting
app.include_router(analytics.router)  # Business analytics, KPIs, dashboards
app.include_router(analyst.router)  # Advanced analytics, data exports, custom reports
app.include_router(admin.router)
# Management & Admin
app.include_router(manager.router)  # Manager operations, team management, approvals
app.include_router(manager_approvals.router)  # Time-off approvals, shift change approvals
app.include_router(employee.router)  # Employee portal, profile, schedules, payroll

# Static file serving for uploads
UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')
if os.path.exists(UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
else:
    logger.warning(f"Upload directory {UPLOAD_DIR} does not exist. Creating it...")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# ============================================================================
# ERROR HANDLERS
# ============================================================================
# Custom error handlers for common HTTP status codes

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """
    Handle 404 Not Found errors.
    
    Returns a JSON response instead of default HTML error page.
    
    Args:
        request: The request that caused the error
        exc: The exception raised
        
    Returns:
        JSONResponse with 404 status and error detail
    """
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """
    Handle 500 Internal Server Error.
    
    Logs the error for debugging and returns a generic error message
    to avoid exposing internal details to clients.
    
    Args:
        request: The request that caused the error
        exc: The exception raised
        
    Returns:
        JSONResponse with 500 status and generic error message
    """
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================
# Direct execution support for development and testing

if __name__ == "__main__":
    import uvicorn
    
    # Run the application with uvicorn
    # - Development: Auto-reload enabled for code changes
    # - Production: Use gunicorn with multiple workers (see README.md)
    uvicorn.run(
        "app:app",  # Application import string
        host="0.0.0.0",  # Listen on all interfaces
        port=8000,  # Default port (override with --port)
        reload=settings.environment == "development"  # Auto-reload in dev mode
    )
