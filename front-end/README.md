# Beladot E-Commerce Frontend

Modern React-based e-commerce frontend with comprehensive product browsing, shopping cart, user authentication, reviews, wishlist, and order management.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Features](#-features)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Building](#-building)
- [Testing](#-testing)
- [Deployment](#-deployment)

## 🚀 Quick Start

```bash
# Navigate to frontend directory
cd front-end

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start development server
npm start
```

Access the app at http://localhost:3000

## ✨ Features

### User Features
- **Authentication**: Registration, login, logout, JWT token management
- **Product Browsing**: View products with images, descriptions, pricing
- **Advanced Search**: Filter by category, price range, rating, stock status
- **Shopping Cart**: Add/remove items, update quantities, persistent cart
- **Checkout**: Place orders with shipping information
- **Order History**: View past orders with status tracking
- **Product Reviews**: Write reviews, rate products (1-5 stars), mark helpful
- **Wishlist**: Save favorite products, move to cart
- **Password Reset**: Forgot password flow with email verification
- **Image Upload**: Sellers can upload product images with drag-drop

### Admin/Seller Features
- **Product Management**: Create, edit, delete products
- **Order Management**: View and update order status
- **Analytics Dashboard**: Sales metrics and insights
- **Image Management**: Upload multiple product images
- **Inventory Tracking**: Monitor stock levels

### Technical Features
- **React 18**: Modern React with hooks
- **Context API**: Global state management (Auth, Cart, Theme)
- **React Router**: Client-side routing
- **Axios**: HTTP client with interceptors
- **Responsive Design**: Mobile-first approach
- **Form Validation**: Client-side validation
- **Error Handling**: Graceful error messages
- **Loading States**: User feedback during API calls

## 🔧 Installation

### Prerequisites
- Node.js 16+ and npm
- Backend API running (see backend README)

### Steps

1. **Navigate to frontend directory:**
```bash
cd front-end
```

2. **Install dependencies:**
```bash
npm install
```

3. **Configure environment:**
```bash
cp .env.example .env
```

Edit `.env`:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_BASE_URL=http://localhost:8000/api
```

4. **Start development server:**
```bash
npm start
```

## 📁 Project Structure

```
front-end/
├── public/
│   ├── index.html              # HTML template
│   ├── manifest.json           # PWA manifest
│   └── robots.txt              # SEO robots file
│
├── src/
│   ├── App.js                  # Main app component
│   ├── index.js                # Entry point
│   │
│   ├── components/             # Reusable UI components
│   │   ├── Header.js           # Navigation header
│   │   ├── ProductCard.js      # Product display card
│   │   └── ImageUpload.js      # Drag-drop image uploader
│   │
│   ├── pages/                  # Page components
│   │   ├── Home.js             # Homepage
│   │   ├── ProductList.js      # Product listing with filters
│   │   ├── ProductDetail.js    # Single product view
│   │   ├── Cart.js             # Shopping cart
│   │   ├── Checkout.js         # Checkout flow
│   │   ├── Login.js            # Login page
│   │   ├── Register.js         # Registration page
│   │   ├── ForgotPassword.js   # Password reset request
│   │   ├── ResetPassword.js    # Password reset completion
│   │   ├── OrderHistory.js     # Past orders
│   │   └── AdminConsole.js     # Admin dashboard
│   │
│   ├── services/               # API client services (17 services)
│   │   ├── authService.js      # Authentication API
│   │   ├── productService.js   # Product API
│   │   ├── cartService.js      # Cart API
│   │   ├── orderService.js     # Order API
│   │   ├── reviewService.js    # Review API
│   │   ├── wishlistService.js  # Wishlist API
│   │   └── ...                 # 11 more services
│   │
│   ├── contexts/               # React contexts
│   │   ├── AuthContext.js      # User authentication state
│   │   ├── CartContext.js      # Shopping cart state
│   │   └── ThemeContext.js     # UI theme state
│   │
│   ├── hooks/                  # Custom React hooks
│   │   ├── useAuth.js          # Authentication hook
│   │   ├── useCart.js          # Cart operations hook
│   │   └── useApi.js           # API call hook
│   │
│   └── utils/                  # Utility functions
│       ├── validators.js       # Form validation
│       ├── formatters.js       # Data formatting
│       └── constants.js        # App constants
│
├── package.json                # Dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

## 🛠️ Development

### Available Scripts

**Start Development Server:**
```bash
npm start
```
- Opens http://localhost:3000
- Hot module replacement enabled
- Shows lint errors in console

**Run Tests:**
```bash
npm test
```
- Launches test runner in watch mode
- Interactive test interface

**Build for Production:**
```bash
npm run build
```
- Creates optimized production build in `build/`
- Minified and optimized
- Includes hash in filenames for caching

**Eject Configuration:**
```bash
npm run eject
```
⚠️ **Warning**: One-way operation! Only use if you need full control over webpack config.

### Development Tips

1. **Enable React DevTools**: Install React Developer Tools browser extension

2. **API Proxy**: Development server proxies API requests to avoid CORS issues

3. **Hot Reload**: Changes auto-refresh the browser

4. **Environment Variables**: Must start with `REACT_APP_`

5. **Debug Mode**: Open browser DevTools for console logs and network inspection

## 🧪 Testing

### Run All Tests
```bash
npm test
```

### Test Coverage
```bash
npm test -- --coverage
```

### Component Testing
Tests are co-located with components:
```
ProductCard.js
ProductCard.test.js
```

## 📦 Building for Production

### Create Production Build
```bash
npm run build
```

This creates:
- Optimized JavaScript bundles
- Minified CSS
- Compressed assets
- Source maps (for debugging)

### Build Output
```
build/
├── static/
│   ├── css/
│   ├── js/
│   └── media/
├── index.html
└── asset-manifest.json
```

### Serve Production Build Locally
```bash
# Install serve
npm install -g serve

# Serve build folder
serve -s build -l 3000
```

## 🚀 Deployment

### Environment Configuration

**Production `.env`:**
```env
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_API_BASE_URL=https://api.yourdomain.com/api
```

### Deployment Options

#### 1. Static Hosting (Netlify, Vercel)
```bash
# Build
npm run build

# Deploy build/ folder
# These platforms auto-detect React apps
```

#### 2. Nginx
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/beladot/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Enable gzip
    gzip on;
    gzip_types text/css application/javascript application/json;
}
```

#### 3. Docker
```dockerfile
FROM nginx:alpine
COPY build/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

See main [DOCKER_GUIDE.md](../DOCKER_GUIDE.md) for full Docker setup.

### Production Checklist

- [ ] Update `.env` with production API URL
- [ ] Build: `npm run build`
- [ ] Test production build locally: `serve -s build`
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS on backend for production domain
- [ ] Set up CDN for static assets (optional)
- [ ] Enable gzip/brotli compression
- [ ] Set caching headers
- [ ] Monitor performance (Lighthouse, Web Vitals)

## 🎨 Key Components

### Authentication
- `Login.js` - User login form
- `Register.js` - New user registration
- `ForgotPassword.js` - Password reset request
- `ResetPassword.js` - Password reset with token

### Products
- `ProductList.js` - Product grid with filters
- `ProductDetail.js` - Detailed product view
- `ProductCard.js` - Reusable product card
- `ImageUpload.js` - Image upload component

### Shopping
- `Cart.js` - Shopping cart page
- `Checkout.js` - Checkout form
- `OrderHistory.js` - Past orders

### Admin
- `AdminConsole.js` - Admin dashboard
- Product management
- Order management

## 🔌 API Integration

### Service Pattern
All API calls use service modules:

```javascript
// Example: Using product service
import { getProducts, getProductById } from './services/productService';

// Get all products
const products = await getProducts();

// Get single product
const product = await getProductById(123);
```

### Available Services
- `authService.js` - Authentication
- `productService.js` - Products
- `cartService.js` - Shopping cart
- `orderService.js` - Orders
- `reviewService.js` - Reviews
- `wishlistService.js` - Wishlist
- `uploadService.js` - File uploads
- And 10+ more services

### Authentication Flow
```javascript
// 1. Login
const response = await authService.login(email, password);
localStorage.setItem('token', response.access_token);

// 2. Auto-attach token to requests (via Axios interceptor)
// 3. Redirect on 401 (token expired)
```

## 🎨 Styling

- CSS modules for component-specific styles
- Global styles in `index.css`
- Responsive design with media queries
- Mobile-first approach

## 🔐 Security

- JWT tokens stored in localStorage
- Auto-logout on token expiration
- CSRF token handling
- XSS prevention (React auto-escapes)
- Input validation
- Secure password requirements

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature-name`
2. Make changes and test
3. Build: `npm run build`
4. Run tests: `npm test`
5. Commit: `git commit -am 'Add feature'`
6. Push: `git push origin feature-name`
7. Submit pull request

## 📝 Related Documentation

- [Main Project README](../README.md) - Overall project guide
- [Backend README](../Ecommerce/backend/README.md) - Backend API docs
- [Docker Guide](../DOCKER_GUIDE.md) - Docker deployment

## 📞 Support

For issues or questions:
- Check [API documentation](http://localhost:8000/docs)
- Review backend logs
- Open an issue on GitHub

## 🛠️ Built With

- **React** 18 - UI library
- **React Router** - Routing
- **Axios** - HTTP client
- **Create React App** - Build tooling

## 📚 Learn More

- [React Documentation](https://reactjs.org/)
- [Create React App Docs](https://create-react-app.dev/)
- [React Router Docs](https://reactrouter.com/)

---

**Version**: 2.0.0  
**Last Updated**: December 9, 2025  
**License**: Proprietary

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
