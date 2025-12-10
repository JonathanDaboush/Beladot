# Beladot E-Commerce Backend API

Enterprise-grade e-commerce backend built with FastAPI, featuring comprehensive business logic, role-based access control, email notifications, image uploads, and complete order fulfillment workflows.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Database Setup](#-database-setup)
- [Running the Application](#-running-the-application)
- [Testing](#-testing)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)

## 🚀 Quick Start

```powershell
# Navigate to backend directory
cd Ecommerce\backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database and SMTP credentials

# Run migrations
alembic upgrade head

# Start server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Access the API at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## ✨ Features

### Core E-Commerce
- **User Management**: Registration, authentication, JWT tokens, role-based access control
- **Product Catalog**: Categories, variants, options, inventory tracking
- **Shopping Cart**: Persistent carts with real-time pricing
- **Checkout & Orders**: Secure order placement, payment processing
- **Order Management**: Status tracking, fulfillment, shipment creation
- **Search & Filters**: Advanced product search by category, price, rating, stock status

### Advanced Features  
- **Email Notifications**: 
  - Order confirmations
  - Shipping updates
  - Password reset emails
- **Image Management**:
  - Product image uploads (single/bulk)
  - Automatic thumbnail generation
  - Format validation (5MB max)
- **Reviews & Ratings**:
  - Verified purchase reviews
  - Rating aggregation
  - Helpful votes
- **Wishlist**: Save products, move to cart
- **Password Reset**: Secure token-based recovery

### Business Features
- **Seller Portal**: Product management, sales analytics, payout tracking
- **Employee Management**: Scheduling, time tracking, payroll, leave management
- **Inventory Tracking**: Stock levels, transaction logs, low-stock alerts
- **Coupons & Discounts**: Flexible coupon system with eligibility rules
- **Refunds & Returns**: Complete refund processing workflow
- **Analytics Dashboard**: Sales metrics, user insights, product performance
- **Audit Logging**: Complete audit trail for compliance

### Security & Performance
- JWT authentication with refresh tokens
- Role-based authorization (9 roles)
- Rate limiting and CSRF protection
- Input validation with Pydantic
- SQL injection prevention
- Async/await for high performance
- Database connection pooling

## 🏗️ Architecture

### Clean Architecture Pattern

```
Backend/
├── app.py                    # FastAPI application & middleware
├── config.py                 # Configuration management
├── database.py               # Database connection & session handling
├── schemas.py                # Pydantic request/response models
│
├── routers/                  # HTTP endpoint handlers (33 routers)
│   ├── auth.py              # Authentication & password reset
│   ├── search.py            # Product search with filters
│   ├── upload.py            # Image upload endpoints
│   ├── reviews.py           # Review CRUD operations
│   ├── wishlist.py          # Wishlist management
│   ├── catalog.py           # Product catalog management
│   ├── checkout.py          # Order checkout
│   └── ...
│
├── Services/                 # Business logic layer
│   ├── UserService.py       # User operations
│   ├── CatalogService.py    # Product management
│   ├── CheckoutService.py   # Order processing
│   └── ...
│
├── Repositories/             # Data access layer
│   └── *Repository.py       # Database CRUD operations
│
├── Models/                   # SQLAlchemy ORM models
│   ├── User.py              # User accounts
│   ├── Product.py           # Products & variants
│   ├── Order.py             # Orders & items
│   ├── Review.py            # Product reviews
│   ├── Wishlist.py          # User wishlists
│   ├── PasswordResetToken.py # Password reset tokens
│   └── ...
│
├── Utilities/               # Helper functions
│   ├── auth.py              # JWT token handling
│   ├── email_service.py     # Email sending (SMTP)
│   └── ...
│
└── Tests/                   # Comprehensive test suite
    ├── test_new_features.py # Feature tests (47 tests)
    ├── fixtures_new_features.py # Test fixtures
    └── ...
```

### Request Flow
```
Client Request
    ↓
FastAPI App (app.py)
    ↓
Middleware (Auth, CORS, Rate Limiting)
    ↓
Router (routers/*.py) - Input validation, authorization
    ↓
Service (Services/*.py) - Business logic
    ↓
Repository (Repositories/*.py) - Database operations
    ↓
Model (Models/*.py) - ORM mapping
    ↓
PostgreSQL Database
```

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **PostgreSQL**: 13 or higher
- **Git**: For version control

### Optional
- **Docker**: For containerized deployment
- **SMTP Account**: Gmail or other email service (for notifications)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/JonathanDaboush/Beladot.git
cd Beladot/Ecommerce/backend
```

### 2. Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
python -c "import fastapi; import sqlalchemy; print('✓ All dependencies installed')"
```

## ⚙️ Configuration

### 1. Environment File Setup

Create a `.env` file in the backend directory:

```bash
# Copy the example file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` with your settings:

```env
# Database
DATABASE_URL=postgresql://beladot_user:your_password@localhost:5432/beladot_db

# JWT Security
SECRET_KEY=your-secret-key-min-32-chars-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Email Configuration (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM_EMAIL=noreply@beladot.com
SMTP_FROM_NAME=Beladot Marketplace

# File Uploads
UPLOAD_DIR=./uploads

# Environment
ENVIRONMENT=development
```

**Important Settings:**

1. **Database**: Update with your PostgreSQL credentials
2. **SECRET_KEY**: Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
3. **SMTP**: Use Gmail app-specific password (not your regular password)
   - Enable 2FA in Google Account
   - Generate app password at: https://myaccount.google.com/apppasswords

### 3. Generate Secret Key

```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
```

Copy the generated key to your `.env` file.

## 💾 Database Setup

### 1. Install PostgreSQL

**Windows:**
- Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- Install with default settings
- Remember the password you set for the `postgres` user

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

### 2. Create Database

```bash
# Access PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ecommerce;

# Create test database (for running tests)
CREATE DATABASE ecommerce_test;

# Exit psql
\q
```

### 3. Run Database Migrations

```bash
# Run all migrations to create tables
alembic upgrade head
```

This creates all required tables:
- users, products, orders, carts, reviews, wishlists
- payments, shipments, inventory
- password_reset_tokens, product_images
- and 30+ more tables

### 4. Verify Database Setup

```bash
# Check tables were created
psql -U beladot_user -d beladot_db -c "\dt"

# You should see 40+ tables
```

## 🏃 Running the Application

### Development Mode

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Run with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Production Mode

```bash
# Run with Gunicorn (Linux/macOS)
gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or use uvicorn directly
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

```bash
# Build image
docker build -t ecommerce-backend .

# Run container
docker run -d -p 8000:8000 --env-file .env ecommerce-backend
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest Tests/test_new_features.py -v

# Run specific test category
pytest Tests/test_new_features.py::TestPasswordReset -v

# Run with verbose output
pytest -v
```

### Test Coverage

The test suite includes **47 comprehensive tests** covering:
- ✅ Password reset flow (4 tests)
- ✅ Image uploads (5 tests)
- ✅ Product reviews (9 tests)
- ✅ Wishlist operations (7 tests)
- ✅ Search filters (7 tests)
- ✅ Email notifications (3 tests)
- ✅ Integration workflows (2 tests)

View coverage report:
```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# Open in browser (Windows)
start htmlcov/index.html

# Open in browser (Linux/macOS)
open htmlcov/index.html
```

## 📚 API Documentation

### Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Quick Reference

See `API_QUICK_REFERENCE.md` for common API patterns and examples.

### Key API Endpoints

**Authentication:**
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token

**Products:**
- `GET /api/products` - List products
- `GET /api/products/{id}` - Product details
- `POST /api/products` - Create product (Seller/Admin)
- `GET /api/search` - Search with filters

**Reviews:**
- `POST /api/reviews` - Create review (verified purchase)
- `GET /api/reviews/product/{id}` - Get product reviews
- `POST /api/reviews/{id}/helpful` - Mark helpful

**Wishlist:**
- `GET /api/wishlist` - Get wishlist
- `POST /api/wishlist` - Add to wishlist
- `POST /api/wishlist/{id}/move-to-cart` - Move to cart

**Image Uploads:**
- `POST /api/upload/product-image` - Upload single image
- `POST /api/upload/product-images-bulk` - Upload multiple

**Cart & Orders:**
- `GET /api/cart` - Get cart
- `POST /api/cart/items` - Add to cart
- `POST /api/orders` - Place order
- `GET /api/orders` - Order history

### Authentication Example

```bash
# 1. Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!", "first_name": "John", "last_name": "Doe"}'

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'

# 3. Use token
curl -X GET http://localhost:8000/api/products \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📁 Project Structure

### Routers (33 API Endpoint Groups)

**Core:**
- `auth.py` - Authentication, registration, password reset
- `search.py` - Product search with filters
- `catalog.py` - Product catalog management
- `checkout.py` - Order checkout
- `cart.py` - Shopping cart operations

**New Features:**
- `upload.py` - Image uploads with thumbnails
- `reviews.py` - Product reviews & ratings
- `wishlist.py` - Wishlist management

**Business:**
- `fulfillment.py` - Shipment tracking
- `transfer.py` - Order transfers
- `seller.py` - Seller operations
- `employee.py` - Employee management
- `analytics.py` - Business metrics
- `manager.py` - Manager operations
- And 20+ more...

### Services (Business Logic Layer)

- **UserService** - User authentication, profiles
- **CatalogService** - Product management
- **CheckoutService** - Order processing
- **CartService** - Cart operations
- **FulfillmentService** - Shipping
- **InventoryService** - Stock management
- **PaymentService** - Payment processing
- **AnalyticsService** - Business intelligence
- **SchedulingService** - Employee scheduling
- **PayrollService** - Payroll calculations

### Models (40+ Database Tables)

**Core:**
- `User` - User accounts with 9 role types
- `Product` - Products with variants
- `Order` - Orders with items
- `Cart` - Shopping carts
- `Payment` - Payment records

**New Tables:**
- `Review` - Product reviews & ratings
- `Wishlist` / `WishlistItem` - User wishlists
- `PasswordResetToken` - Password reset tokens
- `ProductImage` - Product images with thumbnails

**Business:**
- `Seller` / `SellerFinance` - Seller accounts
- `Employee` / `EmployeeSchedule` - Employee management
- `Shipment` / `ShipmentItem` - Shipping
- `Coupon` / `CouponEligibility` - Discounts
- `Refund` / `Return` - Returns processing
- And 25+ more...

## 🔐 Security Features

### Authentication & Authorization
- JWT token-based authentication
- Role-based access control (RBAC)
- Department-scoped authorization for managers
- Refresh token rotation

### Input Validation
- Pydantic models for request validation
- SQL injection prevention (SQLAlchemy parameterized queries)
- XSS protection

### Rate Limiting
- Per-endpoint rate limits
- IP-based throttling
- Burst protection

### Security Headers
- HSTS (HTTP Strict Transport Security)
- Content Security Policy
- X-Frame-Options
- X-Content-Type-Options

## 🚀 Deployment

### Production Checklist

**Security:**
- [ ] Generate strong `SECRET_KEY` (32+ chars)
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure SMTP with app-specific password
- [ ] Update `ALLOWED_ORIGINS` with production domain
- [ ] Enable HTTPS/TLS certificates
- [ ] Set up firewall rules

**Database:**
- [ ] Use production PostgreSQL server
- [ ] Run migrations: `alembic upgrade head`
- [ ] Set up automated backups
- [ ] Configure connection pooling

**Application:**
- [ ] Use Gunicorn with multiple workers
- [ ] Set up reverse proxy (Nginx)
- [ ] Configure monitoring (logs, metrics)
- [ ] Set up error tracking (Sentry)
- [ ] Create uploads directory with proper permissions

**Email:**
- [ ] Configure production SMTP credentials
- [ ] Test all email templates
- [ ] Set up email delivery monitoring

### Production Server

**Using Gunicorn:**
```bash
gunicorn app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

**Using Docker:**
```bash
docker-compose up -d
```

See the main [DOCKER_GUIDE.md](../../DOCKER_GUIDE.md) for complete Docker deployment instructions.

### Database Migrations

**Create new migration:**
```bash
alembic revision --autogenerate -m "Add new feature"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback migration:**
```bash
alembic downgrade -1
```

## 📊 Monitoring & Logs

### Application Logs
```bash
# View logs in development
tail -f logs/app.log

# Or check console output
```

### Performance Monitoring
- Monitor `/health` endpoint
- Track API response times
- Monitor database connection pool
- Watch upload directory size

## 🤝 Contributing

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Keep business logic in Services
- Keep data access in Repositories
- Routers only for validation & auth

### Running Quality Checks
```bash
# Run tests
pytest

# Check code style
flake8 .

# Type checking
mypy .
```

## 📝 Related Documentation

- [Main Project README](../../README.md) - Overall project guide
- [API Quick Reference](API_QUICK_REFERENCE.md) - API endpoint examples
- [Security Guide](SECURITY.md) - Security best practices
- [ERD](erd.md) - Database schema diagram
- [Docker Guide](../../DOCKER_GUIDE.md) - Docker deployment

## 📞 Support

For issues or questions:
- Check the [main README](../../README.md)
- Review [API documentation](http://localhost:8000/docs)
- Open an issue on GitHub

## 🛠️ Built With

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Python ORM
- **PostgreSQL** - Database
- **Pydantic** - Data validation
- **Alembic** - Database migrations
- **Pillow** - Image processing
- **pytest** - Testing framework

---

**Version**: 2.0.0  
**Last Updated**: December 9, 2025  
**License**: Proprietary
