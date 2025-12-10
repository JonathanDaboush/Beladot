# Beladot E-Commerce Platform

A full-stack e-commerce platform with enterprise-grade features including product management, order processing, user authentication, payment integration, email notifications, and comprehensive business analytics.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- Git

### Option 1: Automated Setup (Recommended)

**Windows (PowerShell):**
```powershell
.\quick-start.ps1
```

**Linux/Mac (Bash):**
```bash
chmod +x quick-start.sh
./quick-start.sh
```

### Option 2: Docker Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for detailed Docker instructions.

### Option 3: Manual Setup

#### Backend Setup

```powershell
# Navigate to backend
cd Ecommerce\backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database and SMTP credentials

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```powershell
# Navigate to frontend
cd front-end

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env if needed (default: http://localhost:8000)

# Start development server
npm start
```

## 📱 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 🏗️ Architecture

### Tech Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- Alembic (Database migrations)
- JWT (Authentication)
- Pydantic (Validation)
- Pillow (Image processing)
- SMTP (Email service)

**Frontend:**
- React 18
- React Router (Navigation)
- Axios (HTTP client)
- Context API (State management)

### Project Structure

```
Beladot/
├── Ecommerce/backend/          # FastAPI backend
│   ├── routers/                # API endpoints (31 routers)
│   ├── Services/               # Business logic layer
│   ├── Repositories/           # Data access layer
│   ├── Models/                 # Database models
│   ├── Utilities/              # Helper functions
│   ├── Tests/                  # Test suite
│   └── app.py                  # Main application
│
├── front-end/                  # React frontend
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API client services
│   │   ├── contexts/           # React contexts
│   │   ├── hooks/              # Custom hooks
│   │   └── utils/              # Utility functions
│   └── public/                 # Static assets
│
├── docker-compose.yml          # Docker orchestration
├── quick-start.ps1             # Windows setup script
└── quick-start.sh              # Linux/Mac setup script
```

## ✨ Features

### Core E-Commerce
- **User Authentication**: Registration, login, JWT tokens, role-based access control
- **Product Catalog**: Categories, variants, options, inventory management
- **Shopping Cart**: Persistent carts, item management
- **Checkout**: Order placement, payment processing
- **Order Management**: Order tracking, status updates, history
- **Search & Filters**: Advanced product search with price, rating, category filters

### Advanced Features
- **Email Notifications**: Order confirmations, shipping updates, password reset
- **Product Images**: Upload with validation, thumbnail generation, bulk upload
- **Reviews & Ratings**: Verified purchase reviews, helpful votes, rating aggregation
- **Wishlist**: Save products, move to cart functionality
- **Password Reset**: Secure token-based password recovery
- **Multi-Role System**: Customer, Seller, Admin, CS, Finance, Employee, Manager, Analyst, Transfer

### Business Features
- **Seller Management**: Product listing, sales analytics, payout tracking
- **Employee Management**: Scheduling, time tracking, payroll, leave management
- **Inventory Tracking**: Stock levels, transaction logs, low-stock alerts
- **Coupons & Discounts**: Flexible coupon system with eligibility rules
- **Refunds & Returns**: Full refund processing workflow
- **Analytics Dashboard**: Sales metrics, user insights, product performance
- **Audit Logging**: Complete audit trail for compliance

### Security
- JWT authentication with refresh tokens
- Role-based authorization on all endpoints
- CSRF protection
- Rate limiting
- Input validation and sanitization
- Secure password hashing (bcrypt)
- SQL injection prevention (ORM)

## 🔧 Configuration

### Backend Configuration (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/beladot_db

# JWT
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000

# Email (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@beladot.com
SMTP_FROM_NAME=Beladot Marketplace

# Uploads
UPLOAD_DIR=./uploads

# Environment
ENVIRONMENT=development
```

### Frontend Configuration (.env)

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_BASE_URL=http://localhost:8000/api
```

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
cd Ecommerce/backend
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest Tests/test_new_features.py -v

# Run specific test
pytest Tests/test_auth.py::test_user_registration -v
```

### Test Coverage
- 47+ comprehensive tests
- Unit tests for all major features
- Integration tests for critical workflows
- Mock email testing
- Authentication & authorization tests

## 📚 API Documentation

### Automatic Documentation
Visit http://localhost:8000/docs for interactive API documentation with:
- All endpoints organized by category
- Request/response schemas
- Try-it-out functionality
- Authentication testing

### Key API Endpoints

**Authentication:**
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token

**Products:**
- `GET /api/products` - List products
- `GET /api/products/{id}` - Get product details
- `POST /api/products` - Create product (Seller/Admin)
- `GET /api/search` - Search with filters

**Cart:**
- `GET /api/cart` - Get cart
- `POST /api/cart/items` - Add item to cart
- `PUT /api/cart/items/{id}` - Update quantity
- `DELETE /api/cart/items/{id}` - Remove item

**Orders:**
- `POST /api/orders` - Place order
- `GET /api/orders` - List user orders
- `GET /api/orders/{id}` - Order details
- `PATCH /api/orders/{id}/status` - Update status (Admin)

**Reviews:**
- `POST /api/reviews` - Create review
- `GET /api/reviews/product/{id}` - Get product reviews
- `POST /api/reviews/{id}/helpful` - Mark review helpful

**Wishlist:**
- `GET /api/wishlist` - Get wishlist
- `POST /api/wishlist` - Add to wishlist
- `POST /api/wishlist/{id}/move-to-cart` - Move to cart
- `DELETE /api/wishlist/{id}` - Remove from wishlist

**Uploads:**
- `POST /api/upload/product-image` - Upload single image
- `POST /api/upload/product-images-bulk` - Upload multiple images

See [Ecommerce/backend/API_QUICK_REFERENCE.md](Ecommerce/backend/API_QUICK_REFERENCE.md) for complete API documentation.

## 🚀 Deployment

### Production Checklist

1. **Environment Variables**
   - Generate secure `SECRET_KEY`: `openssl rand -hex 32`
   - Set `ENVIRONMENT=production`
   - Configure production database URL
   - Set up production SMTP credentials
   - Update `ALLOWED_ORIGINS` with production frontend URL

2. **Database**
   - Run migrations: `alembic upgrade head`
   - Create database backups
   - Set up connection pooling

3. **Backend**
   - Use Gunicorn with multiple workers
   - Enable HTTPS
   - Set up monitoring and logging
   - Configure rate limiting

4. **Frontend**
   - Build production bundle: `npm run build`
   - Serve with Nginx or CDN
   - Enable gzip compression
   - Configure caching headers

5. **Security**
   - Enable HTTPS/TLS
   - Configure firewall rules
   - Regular security updates
   - Set up backup strategy

### Docker Production Deployment

See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for:
- Production Docker setup
- Nginx reverse proxy configuration
- SSL/TLS certificate setup
- Monitoring and logging
- Backup and restore procedures

## 📖 Additional Documentation

- [Backend README](Ecommerce/backend/README.md) - Detailed backend documentation
- [Frontend README](front-end/README.md) - Frontend development guide
- [API Reference](Ecommerce/backend/API_QUICK_REFERENCE.md) - Complete API documentation
- [Docker Guide](DOCKER_GUIDE.md) - Docker deployment guide
- [Security](Ecommerce/backend/SECURITY.md) - Security best practices
- [ERD](Ecommerce/backend/erd.md) - Database schema documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is proprietary and confidential.

## 🆘 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Contact the development team
- Check documentation in `/docs`

## 🎯 Roadmap

- [ ] Payment gateway integration (Stripe/PayPal)
- [ ] Real-time notifications (WebSocket)
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Multi-language support (i18n)
- [ ] Social authentication (Google, Facebook)
- [ ] Product recommendations (ML)
- [ ] Live chat support

---

**Built with ❤️ by the Beladot Team**
