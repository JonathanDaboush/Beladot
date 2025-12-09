# AI Frontend Generation Prompt - E-Commerce Platform

## Project Overview
Create a comprehensive React frontend application compatible with our Flask/FastAPI backend controller layer. The application serves multiple user roles with distinct interfaces optimized for their workflows.

---

## Architecture Requirements

### Backend Integration
- **Framework**: React (already initialized with create-react-app)
- **Backend API**: FastAPI REST API (see `Ecommerce/backend/app.py` for all endpoints)
- **Base URL**: `http://localhost:8000/api`
- **Authentication**: JWT tokens (Bearer authentication)
- **API Documentation**: Available at `/docs` (Swagger UI)

### Core Routes from Backend Controller
Based on `app.py`, integrate these 31 routers:
1. **Auth**: `/api/auth` - Login, signup, token refresh, password reset
2. **Cart**: `/api/cart`, `/api/cart-extended` - Shopping cart operations
3. **Products**: `/api/products` - Product CRUD, listing, search
4. **Catalog**: `/api/catalog` - Product browsing, categories
5. **Search**: `/api/search` - Advanced product search with filters
6. **Checkout**: `/api/checkout`, `/api/checkout-extended` - Order creation, payment
7. **Orders**: `/api/orders` - Order management, history, status updates
8. **Payments**: `/api/payments`, `/api/payments-extended`, `/api/payment-methods` - Payment processing
9. **Shipping**: `/api/shipping` - Shipping rates, carriers
10. **Fulfillment**: `/api/fulfillment` - Order fulfillment, shipment tracking
11. **Customer Service**: `/api/customer-service` - Reviews, returns, wishlists
12. **Seller**: `/api/seller`, `/api/seller-extended` - Seller portal, products, payouts
13. **Transfer**: `/api/transfer` - Fund transfers (finance role)
14. **Finance**: `/api/finance` - Financial reports, revenue analysis
15. **Payroll**: `/api/payroll`, `/api/payroll-extended` - Payroll processing, tax documents
16. **Scheduling**: `/api/scheduling`, `/api/scheduling-extended` - Employee scheduling, shift management
17. **Leave**: `/api/leave` - PTO, sick leave requests
18. **Employee**: `/api/employee` - Employee portal, profile
19. **Manager**: `/api/manager`, `/api/manager-approvals` - Team management, approvals
20. **Analytics**: `/api/analytics` - Business metrics, KPIs
21. **Analyst**: `/api/analyst` - Advanced analytics, data exports
22. **Admin**: `/api/admin` - System administration

---

## User Roles & Views

### Role-Based Access Control (STRICT SEPARATION)

#### 1. USER (Buyer/Customer)
**Allowed Backend Routes:**
- `/api/auth` - Login, logout, password reset, delete account
- `/api/cart`, `/api/cart-extended` - Shopping cart operations
- `/api/products` (GET only), `/api/catalog`, `/api/search` - Browse products
- `/api/checkout`, `/api/checkout-extended` - Purchase items
- `/api/orders` (GET own orders only) - View purchase history, delivery status
- `/api/customer-service` (POST only) - Submit refund/return requests

**Capabilities:**
- Edit personal profile (payment details, addresses, contact info)
- Purchase items
- View own order history and delivery status
- Request refunds/returns (system evaluates based on rules)

**Restrictions:**
- Cannot modify anything outside own data
- No seller, employee, or admin functions

---

#### 2. SELLER
**Allowed Backend Routes:**
- All USER routes (sellers can also shop)
- `/api/seller`, `/api/seller-extended` - Seller portal, CRUD own products
- `/api/products` (POST/PUT/DELETE own products only) - Product management
- `/api/orders` (GET orders containing their products only) - View sales
- `/api/analytics` (own sales data only) - View profits and analytics

**Capabilities:**
- Everything a USER can do
- CRUD their own products (price, quantity, description, images)
- View orders involving their products (no customer payment info)
- View own sales analytics and profits

**Restrictions:**
- Cannot see other sellers' products/data
- Cannot access customer payment information
- Cannot modify system-level settings
- Not an employee unless explicitly granted employee role

**System Impact:**
- Updating product quantity immediately affects marketplace inventory
- Deleting/disabling product prevents further purchases

---

#### 3. EMPLOYEE (Base - All Employee Types)
**Shared Backend Routes for ALL Employees:**
- `/api/employee` - Employee portal, profile, clock in/out
- `/api/scheduling` - View own schedule
- `/api/leave` - Request sick leave/PTO

**Shared Capabilities:**
- Clock in / clock out
- Request sick leave / PTO
- Edit own employee profile (separate from user profile)
- View only their division console (no cross-division visibility)

**Restrictions:**
- Cannot access other divisions' consoles
- Cannot approve own leave requests
- Cannot modify payroll or system settings

---

#### 4. CUSTOMER SERVICE (Employee Division)
**Allowed Backend Routes:**
- All EMPLOYEE routes
- All USER routes (for problem resolution ONLY, must log all actions)
- All SELLER routes (for support ONLY, must log all actions)
- `/api/customer-service` - Full access (tickets, disputes, reviews, returns, wishlists)
- `/api/orders` (ALL orders, read/update status only) - Order lookup and management

**Capabilities:**
- Everything a USER can do (for problem resolution, NOT personal use)
- Everything a SELLER can do (for support, NOT operational rights)
- View customer and seller histories, tickets, disputes
- Approve/refuse refunds and returns based on business rules
- MANDATORY: Create audit log for every action taken on behalf of user/seller

**Restrictions:**
- Cannot modify stock directly (must go through proper channels)
- Cannot modify payroll or payment information
- Cannot access Transport or Finance division consoles
- Cannot modify system-level settings
- All actions MUST be logged with reason/ticket reference

**System Impact:**
- Every action creates support log entry with actor_id, target, reason
- Refund approval triggers payment refund workflow
- Return approval triggers transport workflow

---

#### 5. FINANCE (Employee Division)
**Allowed Backend Routes:**
- All EMPLOYEE routes
- `/api/finance` - Financial reports, revenue analysis
- `/api/payroll`, `/api/payroll-extended` - Payroll processing, tax documents
- `/api/transfer` - Fund transfers, seller payouts

**Capabilities:**
- Edit employee payment information
- Create and process payroll for employees
- View financial summaries (payroll-related only)
- Produce invoices, payment records, deductions
- Manage seller payouts

**Restrictions:**
- NO product-related actions (cannot CRUD products)
- NO transport actions (cannot update delivery status)
- NO customer-service-style operations (cannot handle tickets/refunds)
- Cannot access Customer Service or Transport consoles
- Cannot impersonate users or sellers

**System Impact:**
- Payroll creation affects employee financial records
- Payout approvals trigger bank transfers

---

#### 6. TRANSPORT (Employee Division)
**Allowed Backend Routes:**
- All EMPLOYEE routes
- `/api/shipping` - Shipping rates, carriers
- `/api/fulfillment` - Order fulfillment, shipment tracking, delivery status
- `/api/orders` (GET orders for delivery, UPDATE status only) - Delivery management

**Capabilities:**
- Manage delivery states for orders (picked, in transit, delivered, delayed)
- Update shipping status
- Handle returns:
  - If item returned → update quantity or mark as disposed
  - Cancel delivery if refund/return approved
- Generate shipping labels

**Restrictions:**
- NO payment modifications (cannot process refunds/payouts)
- Cannot access user/seller data beyond assigned orders
- Cannot access Customer Service or Finance consoles
- Cannot modify product details or prices

**System Impact:**
- Delivery status updates trigger customer notifications
- Return processing updates inventory quantities

---

#### 7. MANAGER (Department-Specific)
**Types:** FINANCE_MANAGER, TRANSPORT_MANAGER, CUSTOMER_SERVICE_MANAGER

**Allowed Backend Routes (Department-Specific):**
- All routes for their managed department (Finance/Transport/Customer Service)
- `/api/manager`, `/api/manager-approvals` - Team management, approvals
- `/api/employee` (CRUD employees in their department only)
- `/api/scheduling` (all employees in their department), `/api/scheduling-extended`
- `/api/leave` (approve/deny requests for their department)
- `/api/payroll` (Finance Managers only)
- `/api/fulfillment` (Transport Managers only)
- `/api/customer-service` (Customer Service Managers only)

**Capabilities:**
- CRUD employee accounts within their department ONLY
- Approve or deny:
  - Sick days
  - PTO requests
  - Schedule changes
  - Shift swaps
- Override certain employee-level actions in their department
- Enter performance logs about supervised employees
- View department analytics and reports

**Department-Specific Access:**
- **Finance Manager**: Access Finance console + employee management
- **Transport Manager**: Access Transport console + employee management
- **Customer Service Manager**: Access Customer Service console + employee management

**Restrictions:**
- ZERO cross-department management (Finance Manager cannot manage Transport employees)
- Cannot access consoles outside their department
- Cannot perform marketplace actions (unless also SELLER role)
- Cannot perform system-wide admin functions

**System Impact:**
- Leave approvals update employee schedules
- Schedule changes trigger notification workflows
- Performance logs affect employee records

---

#### 8. ANALYST
**Allowed Backend Routes:**
- `/api/analytics` - Business metrics, KPIs, dashboards
- `/api/analyst` - Advanced analytics, data exports, custom reports
- `/api/orders` (GET, read-only, aggregate data only) - Order analytics
- `/api/products` (GET, read-only) - Product analytics

**Capabilities:**
- View business analytics and KPIs
- Generate custom reports
- Export data to CSV/Excel
- Create data visualizations
- Read-only access to aggregate business data

**Restrictions:**
- ZERO write access (cannot modify any data)
- Cannot access PII (personally identifiable information)
- Cannot see individual customer/employee details
- Only aggregate/anonymized data
- Cannot access admin functions

---

#### 9. ADMIN (Top-Level - Full System Access)
**Allowed Backend Routes:**
- **ALL ROUTES** - Complete system access
- `/api/admin` - System administration, configuration

**Capabilities:**
- **Role Switching**: Can switch into ANY role view (USER, SELLER, any employee division)
- Access all consoles (Customer, Seller, Finance, Transport, Customer Service, Manager)
- Override all permissions
- Perform system-wide CRUD on:
  - Users, sellers, employees
  - Products (all sellers)
  - Payments, refunds, payouts
  - Orders, shipments
  - System settings
- User management (create, edit, deactivate, password reset, role assignment)
- System configuration (tax rates, shipping rates, payment gateways)
- Feature flags (enable/disable features)
- API key management
- Audit logs (view full system activity)
- Database maintenance

**System Impact:**
- Admins can perform ANY action
- All admin actions must be logged in audit trail
- Critical actions (delete user, modify payments) require additional confirmation

---

### View Switching Mechanism (Role-Based)

#### Navigation Rules:
1. **Single Role Users**:
   - USER → Customer shopping interface (default and only view)
   - SELLER → Customer view with seller portal accessible via profile menu
   - CUSTOMER_SERVICE → Customer Service console (default), can switch to customer view for testing
   - FINANCE → Finance console (default)
   - TRANSPORT → Transport console (default)
   - ANALYST → Analytics dashboard (default)

2. **Managers**:
   - See their department console + manager features
   - **Finance Manager** → Finance console with manager controls
   - **Transport Manager** → Transport console with manager controls
   - **Customer Service Manager** → CS console with manager controls

3. **Multi-Role Users** (e.g., SELLER + CUSTOMER_SERVICE):
   - User profile icon shows role badge with dropdown
   - Dropdown lists all available views based on assigned roles
   - Can switch between views dynamically
   - Each view respects that role's permissions strictly

4. **ADMIN Users**:
   - Profile dropdown shows "Switch Role" option
   - Can select ANY role to impersonate
   - Header shows "Admin Mode: Viewing as [ROLE]" when impersonating
   - "Exit Admin Mode" button to return to admin console
   - All actions in impersonation mode are logged with note "admin_impersonating_[role]"

#### Implementation:
```javascript
// Role-based view mapping
const VIEW_MAP = {
  'customer': '/customer',
  'seller': '/seller',
  'customer_service': '/cs-console',
  'finance': '/finance-console',
  'transport': '/transport-console',
  'manager': '/manager-console', // with department context
  'analyst': '/analytics',
  'admin': '/admin'
};

// Get available views for user
const getAvailableViews = (user) => {
  const views = [];
  
  // Base views
  if (user.role === 'customer' || user.roles.includes('customer')) {
    views.push({ label: 'Shop', value: 'customer' });
  }
  
  if (user.role === 'seller' || user.roles.includes('seller')) {
    views.push({ label: 'Seller Portal', value: 'seller' });
  }
  
  // Employee divisions (mutually exclusive in single view)
  if (user.role === 'customer_service') {
    views.push({ label: 'Customer Service Console', value: 'customer_service' });
  }
  
  if (user.role === 'finance') {
    views.push({ label: 'Finance Console', value: 'finance' });
  }
  
  if (user.role === 'transport') {
    views.push({ label: 'Transport Console', value: 'transport' });
  }
  
  // Managers
  if (user.role.includes('manager')) {
    views.push({ 
      label: `${user.department} Manager Console`, 
      value: 'manager',
      department: user.department 
    });
  }
  
  // Analyst
  if (user.role === 'analyst') {
    views.push({ label: 'Analytics', value: 'analyst' });
  }
  
  // Admin can access everything
  if (user.role === 'admin') {
    views.push({ label: 'Admin Console', value: 'admin' });
    views.push({ label: '--- Switch Role ---', value: 'divider', disabled: true });
    views.push({ label: 'View as Customer', value: 'customer' });
    views.push({ label: 'View as Seller', value: 'seller' });
    views.push({ label: 'View as Customer Service', value: 'customer_service' });
    views.push({ label: 'View as Finance', value: 'finance' });
    views.push({ label: 'View as Transport', value: 'transport' });
    views.push({ label: 'View as Manager', value: 'manager' });
    views.push({ label: 'View as Analyst', value: 'analyst' });
  }
  
  return views;
};
```

#### State Persistence:
- Current view stored in: `localStorage.setItem('currentView', 'customer')`
- Admin impersonation: `localStorage.setItem('adminImpersonating', 'seller')`
- On app load, restore last active view if still valid for user's roles

---

## Interface Design Patterns

### 1. Customer/Seller View (B2C E-Commerce UX)
**Design Philosophy**: Amazon/eBay shopping experience

#### Key Features:
- **Top Navigation Bar**:
  - Logo (left) - links to home
  - Category mega-menu (Electronics, Toys, Clothing, Home & Garden, Sports, etc.)
  - Search bar (center) - prominent, with autocomplete
  - Cart icon with item count badge
  - User profile icon with role switcher dropdown
  - Wishlist icon

- **Search Functionality**:
  - Real-time autocomplete suggestions
  - Search filters sidebar (price range, brand, rating, availability)
  - Sort options (relevance, price low-to-high, price high-to-low, newest)
  - Pagination with "Load More" or page numbers
  - Breadcrumb navigation

- **Product Listing**:
  - Grid layout (4 columns desktop, 2 tablet, 1 mobile)
  - Product cards with image, title, price, rating stars, prime badge
  - Quick view modal on hover
  - "Add to Cart" button with quantity selector
  - Compare checkbox for multi-product comparison

- **Product Detail Page**:
  - Image gallery with zoom and thumbnails
  - Price, stock availability, seller information
  - Variant selector (size, color, etc.)
  - Add to cart with quantity
  - Product description tabs (Description, Specifications, Reviews)
  - Related products carousel
  - Q&A section

- **Shopping Cart**:
  - Sidebar drawer (slide from right)
  - Item cards with image, title, price, quantity controls
  - Remove button
  - Subtotal with "Proceed to Checkout" button
  - "Continue Shopping" link
  - Recommendations: "Customers also bought"

- **Checkout Flow**:
  - Multi-step wizard (Shipping → Payment → Review → Confirmation)
  - Progress indicator
  - Shipping address selection/creation
  - Payment method selection
  - Order review with edit options
  - Order confirmation with tracking info

#### Seller Portal (within Customer view style):
- **Dashboard** (Amazon Seller Central style):
  - Sales metrics cards (today, this week, this month)
  - Recent orders table
  - Low stock alerts
  - Pending actions

- **Product Management**:
  - Product list table with search/filter
  - Add product wizard (multi-step form)
  - Bulk actions (activate/deactivate, update prices)
  - Inventory management
  - Image upload with drag-drop

- **Orders**:
  - Order list with filters (pending, shipped, delivered)
  - Order detail view
  - Shipping label generation
  - Fulfillment workflow

- **Analytics**:
  - Charts: Sales over time, top products, traffic sources
  - Export to CSV

- **Payouts**:
  - Payout history table
  - Bank account management
  - Transaction details

---

### 2. Admin/Employee Views (B2B/Enterprise UX)
**Design Philosophy**: AWS Console, Stripe Dashboard, Salesforce Service Cloud

#### Design Principles:
- **Information Density**: Show more data, less whitespace
- **Speed & Efficiency**: Keyboard shortcuts, bulk actions, quick filters
- **Transparency**: Detailed logs, errors, system status
- **Power User Features**: Advanced search, saved filters, custom views
- **No Hand-Holding**: Assume trained users, show technical details

#### Key Features:

##### Navigation:
- **Sidebar Navigation** (always visible):
  - Collapsible sections (Dashboard, Users, Orders, Products, Analytics, System)
  - Active state highlighting
  - Icon + label
  - Search within nav (Cmd/Ctrl + K)

- **Top Bar**:
  - Breadcrumbs with full path
  - Global search (searches all entities)
  - Notifications bell icon
  - User menu with role switcher
  - Environment indicator (Production/Staging)

##### Dashboard:
- **Metrics Cards** (4 across):
  - Revenue (today, vs yesterday)
  - Orders (pending, processing, shipped)
  - Active users (current, vs last week)
  - System health (API response time, error rate)

- **Charts**:
  - Line chart: Revenue over time (daily/weekly/monthly toggle)
  - Bar chart: Orders by status
  - Donut chart: Revenue by category

- **Activity Feed**:
  - Recent orders (last 10)
  - Recent user signups
  - System events (deployments, errors)

##### Data Tables (Universal Pattern):
- **Header**:
  - Title + total count
  - Search input (filters all columns)
  - Filter button (opens filter drawer)
  - Export button (CSV/Excel)
  - Bulk action dropdown (if items selected)
  - "Add New" button (primary action)

- **Table**:
  - Checkbox column (for bulk selection)
  - Sortable columns (click header to sort)
  - Row actions menu (3-dot icon)
  - Pagination footer (10/25/50/100 per page)
  - Loading skeleton while fetching
  - Empty state with illustration + "Add First Item" CTA

- **Filters** (slide-out drawer):
  - Date range picker
  - Status checkboxes
  - Numeric range sliders (price, quantity)
  - Dropdown selects (category, seller, etc.)
  - "Apply Filters" + "Clear All"
  - Save filter preset option

##### Forms:
- **Layout**: Two-column grid for efficiency
- **Validation**: Real-time validation with error messages
- **Required Fields**: Asterisk indicator
- **Help Text**: Small gray text under inputs
- **Actions**: "Save" (primary), "Cancel", "Save & Add Another"

##### Specific Role Views:

**Customer Service Console**:
- Ticket list table (status, priority, customer, subject, assigned to)
- Ticket detail with conversation thread
- Order lookup (by order number, email, phone)
- Customer profile view (order history, tickets, account details)
- Return management (approve/reject, refund processing)
- Review moderation (approve/flag/delete)

**Finance Dashboard**:
- Revenue reports (daily, weekly, monthly, custom range)
- Transaction list table (all payments, refunds, payouts)
- Reconciliation tools
- Tax reports
- Payout management (approve seller payouts)
- Bank account verification

**Payroll Console**:
- Employee list with financial details
- Pay period selector
- Payroll run workflow (calculate → review → approve → process)
- Pay stub generation
- Tax document management (W-2, T4)
- Direct deposit management

**Scheduling Console**:
- Weekly calendar view (grid: employees × days)
- Drag-and-drop shift assignment
- Shift templates
- Time-off requests (approve/reject)
- Shift swap management
- Coverage alerts (understaffed warnings)

**Analytics Dashboard**:
- Custom report builder
- Chart types: line, bar, pie, table
- Metric selector (revenue, orders, users, etc.)
- Dimension selector (time, category, seller, etc.)
- Date range picker
- Export to PDF/Excel
- Scheduled reports (email digest)

**Admin Console** (System Configuration):
- User management (list, create, edit, deactivate, password reset)
- Role assignment with permission matrix
- System settings (tax rates, shipping rates, payment gateways)
- Email template editor
- Feature flags toggle (enable/disable features)
- API key management
- Audit logs (full system activity log)
- Database maintenance (vacuum, backup status)

---

## Technical Requirements

### Component Architecture

#### Modular Component Structure:
```
src/
├── components/
│   ├── common/
│   │   ├── Button.jsx (with PropTypes)
│   │   ├── Input.jsx
│   │   ├── Table.jsx
│   │   ├── Modal.jsx
│   │   ├── Drawer.jsx
│   │   ├── Card.jsx
│   │   ├── Badge.jsx
│   │   ├── Spinner.jsx
│   │   └── Skeleton.jsx
│   ├── customer/
│   │   ├── ProductCard.jsx
│   │   ├── ProductGrid.jsx
│   │   ├── CartDrawer.jsx
│   │   ├── CategoryNav.jsx
│   │   └── SearchBar.jsx
│   ├── seller/
│   │   ├── SellerDashboard.jsx
│   │   ├── ProductForm.jsx
│   │   └── OrderList.jsx
│   └── admin/
│       ├── DataTable.jsx
│       ├── FilterDrawer.jsx
│       ├── MetricCard.jsx
│       └── Sidebar.jsx
├── pages/
│   ├── customer/
│   │   ├── HomePage.jsx
│   │   ├── ProductPage.jsx
│   │   ├── CheckoutPage.jsx
│   │   └── OrderHistoryPage.jsx
│   ├── seller/
│   │   ├── SellerDashboardPage.jsx
│   │   └── SellerProductsPage.jsx
│   └── admin/
│       ├── AdminDashboardPage.jsx
│       ├── UsersPage.jsx
│       └── AnalyticsPage.jsx
├── services/
│   ├── api.js (axios instance with interceptors)
│   ├── authService.js
│   ├── productService.js
│   ├── orderService.js
│   └── userService.js
├── hooks/
│   ├── useAuth.js
│   ├── useCart.js
│   ├── useProducts.js
│   └── useDebounce.js
├── contexts/
│   ├── AuthContext.jsx
│   ├── CartContext.jsx
│   └── ThemeContext.jsx
├── utils/
│   ├── formatters.js (currency, date, etc.)
│   ├── validators.js
│   └── constants.js
└── App.jsx
```

#### Component Standards:
```jsx
import React from 'react';
import PropTypes from 'prop-types';

/**
 * Button component with loading and disabled states
 * @param {Object} props - Component props
 * @param {string} props.variant - Button style variant (primary, secondary, danger)
 * @param {boolean} props.loading - Show loading spinner
 * @param {Function} props.onClick - Click handler
 * @param {ReactNode} props.children - Button content
 */
const Button = ({ variant = 'primary', loading = false, disabled = false, onClick, children }) => {
  return (
    <button
      className={`btn btn-${variant} ${loading ? 'loading' : ''}`}
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading && <Spinner size="small" />}
      {children}
    </button>
  );
};

Button.propTypes = {
  variant: PropTypes.oneOf(['primary', 'secondary', 'danger']).isRequired,
  loading: PropTypes.bool,
  disabled: PropTypes.bool,
  onClick: PropTypes.func.isRequired,
  children: PropTypes.node.isRequired,
};

export default Button;
```

### State Management

#### Loading States:
- **Initial Load**: Show skeleton loaders matching content structure
- **Refetching**: Show subtle loading indicator (top progress bar)
- **Button Actions**: Disable button, show spinner, change text to "Saving..."
- **Pagination**: Show loading rows at bottom of table

#### Error States:
- **Network Error**: "Unable to connect. Check your internet connection." + Retry button
- **Server Error**: "Something went wrong. Our team has been notified." + Retry button
- **Validation Error**: Show inline under input field with red border
- **Not Found**: "Product not found" with illustration + "Continue Shopping" button

#### Empty States:
- **Empty Cart**: Illustration + "Your cart is empty" + "Start Shopping" button
- **No Orders**: "You haven't placed any orders yet" + "Browse Products" button
- **No Results**: "No products found for 'search term'" + "Try different keywords"

#### Optimistic Updates:
```javascript
// Add to cart - update UI immediately, rollback on error
const addToCart = async (productId, quantity) => {
  // Optimistic update
  setCart(prev => [...prev, { productId, quantity }]);
  setCartCount(prev => prev + quantity);
  
  try {
    await api.post('/cart/items', { productId, quantity });
    // Success - already updated
    showToast('Added to cart', 'success');
  } catch (error) {
    // Rollback optimistic update
    setCart(prev => prev.filter(item => item.productId !== productId));
    setCartCount(prev => prev - quantity);
    showToast('Failed to add to cart', 'error');
  }
};
```

### Data Fetching & Tables

#### Server-Side Pagination:
```javascript
const [products, setProducts] = useState([]);
const [loading, setLoading] = useState(false);
const [page, setPage] = useState(1);
const [pageSize, setPageSize] = useState(25);
const [total, setTotal] = useState(0);
const [sortBy, setSortBy] = useState('created_at');
const [sortOrder, setSortOrder] = useState('desc');
const [filters, setFilters] = useState({});

useEffect(() => {
  fetchProducts();
}, [page, pageSize, sortBy, sortOrder, filters]);

const fetchProducts = async () => {
  setLoading(true);
  try {
    const params = new URLSearchParams({
      page,
      page_size: pageSize,
      sort_by: sortBy,
      sort_order: sortOrder,
      ...filters
    });
    
    const response = await api.get(`/products?${params}`);
    setProducts(response.data.items);
    setTotal(response.data.total);
    
    // Sync with URL
    history.pushState({}, '', `?${params}`);
  } catch (error) {
    showError(error);
  } finally {
    setLoading(false);
  }
};
```

#### Column Sorting:
```javascript
const handleSort = (column) => {
  if (sortBy === column) {
    setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
  } else {
    setSortBy(column);
    setSortOrder('asc');
  }
};

// Table header
<th onClick={() => handleSort('name')}>
  Name
  {sortBy === 'name' && (
    <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
  )}
</th>
```

#### Filters with URL Sync:
```javascript
// Read filters from URL on mount
useEffect(() => {
  const params = new URLSearchParams(window.location.search);
  const urlFilters = {
    category: params.get('category'),
    minPrice: params.get('min_price'),
    maxPrice: params.get('max_price'),
    inStock: params.get('in_stock') === 'true'
  };
  setFilters(urlFilters);
}, []);

// Update URL when filters change
useEffect(() => {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  window.history.replaceState({}, '', `?${params}`);
}, [filters]);
```

### Keyboard Shortcuts

#### Global Shortcuts:
```javascript
useEffect(() => {
  const handleKeyPress = (e) => {
    // Ignore if typing in input
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    
    // 'g then h' for home
    if (lastKey === 'g' && e.key === 'h') {
      navigate('/');
      setLastKey(null);
    }
    
    // 'g then a' for admin
    if (lastKey === 'g' && e.key === 'a' && hasRole('admin')) {
      navigate('/admin');
      setLastKey(null);
    }
    
    // 's' to focus search
    if (e.key === 's') {
      e.preventDefault();
      searchInputRef.current.focus();
    }
    
    // '?' for help
    if (e.key === '?') {
      setShowShortcutsModal(true);
    }
    
    setLastKey(e.key);
  };
  
  window.addEventListener('keydown', handleKeyPress);
  return () => window.removeEventListener('keydown', handleKeyPress);
}, [lastKey]);
```

#### Shortcuts Help Modal:
```jsx
<Modal isOpen={showShortcutsModal} onClose={() => setShowShortcutsModal(false)}>
  <h2>Keyboard Shortcuts</h2>
  <table>
    <tr><td>g then h</td><td>Go to Home</td></tr>
    <tr><td>g then a</td><td>Go to Admin Console (if authorized)</td></tr>
    <tr><td>s</td><td>Focus Search</td></tr>
    <tr><td>?</td><td>Show this help</td></tr>
    <tr><td>Esc</td><td>Close modal / Clear search</td></tr>
  </table>
</Modal>
```

### Feature Flags

#### Admin Console Toggle:
```jsx
// Feature flags stored in localStorage or backend
const [featureFlags, setFeatureFlags] = useState({
  newCheckoutFlow: false,
  advancedAnalytics: false,
  bulkProductUpload: false
});

// Admin feature flag manager
<div className="feature-flags">
  <h3>Feature Flags</h3>
  <label>
    <input
      type="checkbox"
      checked={featureFlags.newCheckoutFlow}
      onChange={(e) => updateFlag('newCheckoutFlow', e.target.checked)}
    />
    New Checkout Flow (Beta)
  </label>
  {/* ... more flags */}
</div>

// Use in code
{featureFlags.newCheckoutFlow ? (
  <NewCheckout />
) : (
  <OldCheckout />
)}
```

---

## API Integration

### Authentication Flow:
```javascript
// authService.js
export const login = async (email, password) => {
  const response = await api.post('/auth/login', { email, password });
  const { access_token, refresh_token } = response.data;
  
  localStorage.setItem('accessToken', access_token);
  localStorage.setItem('refreshToken', refresh_token);
  
  return response.data;
};

// Axios interceptor for token refresh
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        try {
          const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
          localStorage.setItem('accessToken', response.data.access_token);
          
          // Retry original request
          error.config.headers.Authorization = `Bearer ${response.data.access_token}`;
          return api(error.config);
        } catch (refreshError) {
          // Refresh failed - logout
          localStorage.clear();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);
```

### API Service Pattern:
```javascript
// productService.js
export const productService = {
  getAll: (params) => api.get('/products', { params }),
  getById: (id) => api.get(`/products/${id}`),
  create: (data) => api.post('/products', data),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
  search: (query, filters) => api.get('/search', { params: { query, ...filters } })
};
```

---

## Styling & Responsiveness

### CSS Framework:
- Use **Tailwind CSS** or **Material-UI** for rapid development
- Custom theme with brand colors
- Responsive breakpoints: mobile (< 768px), tablet (768-1024px), desktop (> 1024px)

### Design Tokens:
```css
:root {
  /* Colors */
  --primary-color: #FF9900; /* Amazon orange */
  --secondary-color: #146EB4;
  --success-color: #067D62;
  --danger-color: #D5281B;
  --warning-color: #F3A847;
  
  /* Typography */
  --font-family: 'Amazon Ember', Arial, sans-serif;
  --font-size-sm: 12px;
  --font-size-base: 14px;
  --font-size-lg: 16px;
  --font-size-xl: 20px;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Shadows */
  --shadow-sm: 0 2px 4px rgba(0,0,0,0.1);
  --shadow-md: 0 4px 8px rgba(0,0,0,0.12);
  --shadow-lg: 0 8px 16px rgba(0,0,0,0.15);
}
```

### Responsive Grid:
```jsx
// Product grid that adapts to screen size
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {products.map(product => (
    <ProductCard key={product.id} product={product} />
  ))}
</div>
```

---

## Performance Optimization

### Code Splitting:
```javascript
// Lazy load routes
import { lazy, Suspense } from 'react';

const CustomerRoutes = lazy(() => import('./routes/CustomerRoutes'));
const SellerRoutes = lazy(() => import('./routes/SellerRoutes'));
const AdminRoutes = lazy(() => import('./routes/AdminRoutes'));

// Use with Suspense
<Suspense fallback={<LoadingScreen />}>
  <CustomerRoutes />
</Suspense>
```

### Image Optimization:
- Lazy load images below fold
- Use `<img loading="lazy" />`
- Serve WebP format with JPEG fallback
- Thumbnail images in lists, full resolution on detail page

### Debounce Search:
```javascript
import { useState, useEffect } from 'react';

const useDebounce = (value, delay = 500) => {
  const [debouncedValue, setDebouncedValue] = useState(value);
  
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    return () => clearTimeout(handler);
  }, [value, delay]);
  
  return debouncedValue;
};

// Usage
const [searchTerm, setSearchTerm] = useState('');
const debouncedSearch = useDebounce(searchTerm);

useEffect(() => {
  if (debouncedSearch) {
    fetchSearchResults(debouncedSearch);
  }
}, [debouncedSearch]);
```

---

## Accessibility

### ARIA Labels:
- All interactive elements have `aria-label`
- Form inputs have associated `<label>`
- Error messages have `aria-live="polite"`
- Loading states announce with `aria-busy="true"`

### Keyboard Navigation:
- All actions accessible via keyboard
- Tab order follows visual order
- Skip links for screen readers
- Focus visible outlines

### Color Contrast:
- Text meets WCAG AA standards (4.5:1 ratio)
- Interactive elements have hover/focus states
- Error states use icon + color (not color alone)

---

## Testing Checklist

### Manual Testing:
- [ ] Login/logout flow
- [ ] Add to cart and checkout
- [ ] Search and filters
- [ ] Product CRUD (seller view)
- [ ] Order management (admin view)
- [ ] Role switching works correctly
- [ ] Mobile responsive (all breakpoints)
- [ ] Keyboard shortcuts work
- [ ] Error states display correctly
- [ ] Loading states show appropriately

### User Scenarios:
1. **Customer**: Browse products → Add to cart → Checkout → View order history
2. **Seller**: Create product → Manage inventory → View orders → Process fulfillment
3. **Admin**: View dashboard → Manage users → Generate reports → Configure system

---

## Deliverables

### Expected Output:
1. Complete React application with all views implemented
2. API integration with all 31 backend routes
3. Responsive design (mobile, tablet, desktop)
4. Documentation:
   - README with setup instructions
   - Component library documentation
   - API integration guide
5. Environment configuration (.env.example)

### Code Quality:
- ESLint configured (Airbnb style guide)
- Prettier for code formatting
- PropTypes or TypeScript for type checking
- Comments for complex logic
- No console.log in production code

---

## Summary

Build a professional, production-ready e-commerce platform frontend with:
- **Customer View**: Amazon/eBay-style shopping experience
- **Seller View**: Seller Central-style management portal
- **Admin Views**: AWS Console-style enterprise interface
- **Role Switching**: Seamless switching between views based on user permissions
- **Performance**: Optimistic updates, lazy loading, debounced search
- **Accessibility**: WCAG AA compliant, keyboard navigation
- **Modular**: Well-documented components with PropTypes
- **Responsive**: Mobile-first design with breakpoints
- **Error Handling**: Graceful failures with retry options
- **Feature Flags**: Admin-controlled experimental features

Follow the backend API contract strictly, implement all loading/error/empty states, and ensure keyboard shortcuts and power-user features are available in admin views.
