# API Quick Reference - Payment, Inventory, Catalog & Fulfillment

## Catalog Management (Admin Only)

### Create Category
```http
POST /api/catalog/categories
Authorization: Bearer <admin_token>

Parameters:
  - name: string (required) - Category name (e.g., "Electronics")
  - description: string (optional) - Category description
```

### Create Subcategory
```http
POST /api/catalog/categories/{category_id}/subcategories
Authorization: Bearer <admin_token>

Parameters:
  - name: string (required) - Subcategory name (e.g., "Televisions")
  - description: string (optional) - Subcategory description
```

### List Categories (Public)
```http
GET /api/catalog/categories

Parameters:
  - include_inactive: boolean (optional) - Include inactive categories
```

---

## Product Management (Sellers, CS, Managers)

### Create Product (Seller)
```http
POST /api/catalog/products
Authorization: Bearer <seller_token>

Parameters:
  - name: string (required)
  - description: string (required)
  - price_cents: int (required)
  - category_id: int (required)
  - subcategory_id: int (optional)
  - sku: string (optional, auto-generated if not provided)
```

### Update Product
```http
PUT /api/catalog/products/{product_id}
Authorization: Bearer <seller_token>

Parameters:
  - name: string (optional)
  - description: string (optional)
  - price_cents: int (optional)
  - category_id: int (optional)
  - subcategory_id: int (optional)

Notes:
  - Sellers can only update their own products
  - CS/Managers can update any product
```

### Create Product Variant (Seller Only)
```http
POST /api/catalog/products/{product_id}/variants
Authorization: Bearer <seller_token>

Parameters:
  - sku: string (required) - Unique SKU for variant
  - name: string (required) - Variant name (e.g., "Red - Medium")
  - price_cents: int (required)
  - stock_quantity: int (optional, default: 0)
```

### Update Product Variant (Seller Only)
```http
PUT /api/catalog/variants/{variant_id}
Authorization: Bearer <seller_token>

Parameters:
  - name: string (optional)
  - price_cents: int (optional)
  - stock_quantity: int (optional)
```

### Upload Product Image (Seller Only)
```http
POST /api/catalog/products/{product_id}/images
Authorization: Bearer <seller_token>
Content-Type: multipart/form-data

Body:
  - file: image file (required)
  - alt_text: string (optional)
```

---

## Fulfillment & Shipment Tracking

### Track Shipment
```http
GET /api/shipments/{shipment_id}/track
Authorization: Bearer <token>

Access Control:
  - Customers: Own orders only
  - Shipping Department Employees: All shipments
  - Customer Service: All shipments
  - Managers: All shipments

Response:
{
  "shipment_id": 123,
  "order_id": 456,
  "tracking_number": "PURO1234567890",
  "carrier": "purolator",
  "status": "in_transit",
  "estimated_delivery": "2025-12-10T18:00:00Z",
  "tracking_events": [
    {
      "timestamp": "2025-12-06T10:00:00Z",
      "status": "Picked up by carrier",
      "location": "Warehouse"
    }
  ],
  "last_updated": "2025-12-06T12:00:00Z"
}
```

### Get Order Shipments
```http
GET /api/shipments/order/{order_id}
Authorization: Bearer <token>

Access Control: Same as Track Shipment

Response:
{
  "order_id": 456,
  "shipments": [
    {
      "id": 123,
      "tracking_number": "PURO1234567890",
      "carrier": "purolator",
      "status": "shipped",
      "shipped_at": "2025-12-06T10:00:00Z",
      "estimated_delivery": "2025-12-10T18:00:00Z"
    }
  ]
}
```

**Note**: Shipments are automatically created when an order is confirmed during checkout.

---

## Payment Methods

### Add Payment Method
```http
POST /api/payment-methods
Authorization: Bearer <token>
Content-Type: application/json

{
  "gateway_token": "pm_1234567890abcdef",
  "card_brand": "visa",
  "card_last_four": "4242",
  "expiry_month": 12,
  "expiry_year": 2027,
  "billing_zip": "12345",
  "set_as_default": true
}
```

### List Payment Methods
```http
GET /api/payment-methods
Authorization: Bearer <token>
```

### Set Default Payment Method
```http
PATCH /api/payment-methods/{payment_method_id}/default
Authorization: Bearer <token>
```

### Delete Payment Method
```http
DELETE /api/payment-methods/{payment_method_id}
Authorization: Bearer <token>
```

---

## Checkout

### Create Payment Intent (Step 1)
```http
POST /api/checkout/payment-intent
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount_cents": 5000,
  "currency": "USD",
  "payment_method_id": 1
}

Response:
{
  "payment_id": 789,
  "status": "pending",
  "amount_cents": 5000,
  "currency": "USD"
}
```

### Complete Checkout (Step 2)
```http
POST /api/checkout/process
Authorization: Bearer <token>
Content-Type: application/json

{
  "cart_id": 123,
  "payment_intent_id": 789,
  "shipping_address": {
    "address_line1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "country": "US",
    "postal_code": "10001"
  },
  "idempotency_key": "unique-key-12345"
}
```

### One-Click Checkout
```http
POST /api/checkout/charge-stored-method
Authorization: Bearer <token>
Content-Type: application/json

{
  "cart_id": 123,
  "payment_method_id": 1,  // Optional - uses default if not provided
  "shipping_address": {...},
  "idempotency_key": "unique-key-12345"
}
```

---

## Cart Operations

### Remove Item
```http
DELETE /api/cart/items/{product_id}
Authorization: Bearer <token>
```

### Update Item Quantity
```http
PATCH /api/cart/items/{product_id}?quantity=5
Authorization: Bearer <token>
```

### Clear Cart
```http
DELETE /api/cart
Authorization: Bearer <token>
```

---

## Products (with Stock)

### List Products
```http
GET /api/products?currency=USD&page=1&page_size=20
Authorization: Bearer <token>

Response:
{
  "products": [
    {
      "id": 1,
      "name": "Product Name",
      "price_cents": 2999,
      "stock_quantity": 50,
      "in_stock": true,
      "display_currency": "USD",
      "display_price": 29.99
    }
  ]
}
```

### Get Single Product
```http
GET /api/products/{product_id}?currency=USD
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "name": "Product Name",
  "stock_quantity": 50,
  "in_stock": true,
  ...
}
```

---

## Seller Operations

### View Products
```http
GET /api/seller/products
Authorization: Bearer <seller_token>

Response:
{
  "products": [
    {
      "id": 1,
      "name": "My Product",
      "stock_quantity": 50,
      ...
    }
  ]
}
```

### Edit Product
```http
PATCH /api/seller/products/{product_id}
Authorization: Bearer <seller_token>
Content-Type: application/json

{
  "name": "Updated Product Name",
  "description": "New description",
  "price_cents": 3499
}
```

### Update Stock
```http
PATCH /api/seller/products/{product_id}/stock?quantity=100
Authorization: Bearer <seller_token>

Response:
{
  "message": "Stock updated successfully",
  "product_id": 1,
  "new_stock": 100
}
```

### Calculate Earnings
```http
GET /api/seller/earnings?start_date=2025-11-01&end_date=2025-11-30
Authorization: Bearer <seller_token>

Response:
{
  "start_date": "2025-11-01",
  "end_date": "2025-11-30",
  "gross_sales": 10000,
  "seller_earnings": 8000,
  "company_profit": 2000
}
```

### Trigger Payout
```http
POST /api/seller/payout
Authorization: Bearer <seller_token>

Response:
{
  "message": "Payout initiated successfully",
  "payout_id": 42,
  "amount": 8000.00,
  "status": "pending"
}
```

### Payout History
```http
GET /api/seller/payouts
Authorization: Bearer <seller_token>

Response:
{
  "payouts": [
    {
      "payout_id": 42,
      "amount": 8000.00,
      "payout_date": "2025-12-01",
      "status": "completed",
      "product_summary": {
        "Product A": {
          "quantity": 10,
          "total_sales": 5000
        },
        "Product B": {
          "quantity": 5,
          "total_sales": 5000
        }
      },
      "total_items": 15,
      "order_count": 8
    }
  ]
}
```

---

## Transfer/Delivery Operations

### Update Product Stock
```http
PUT /api/transfer/products/{product_id}/stock
Authorization: Bearer <transfer_token>
Content-Type: application/json

{
  "new_stock": 200,
  "reason": "Inventory adjustment - received shipment"
}
```

### Receive Shipment
```http
POST /api/transfer/shipments/{shipment_id}/receive
Authorization: Bearer <transfer_token>

Response:
{
  "message": "Shipment 123 received and inventory updated"
}
```

---

## Role Permissions

| Endpoint | Customer | Seller | Transfer | Customer Service | Admin |
|----------|----------|--------|----------|------------------|-------|
| GET /api/products (stock visible) | ✅ | ✅ | ✅ | ✅ | ✅ |
| POST /api/payment-methods | ✅ | ✅ | ✅ | ❌ | ✅ |
| POST /api/checkout/* | ✅ | ✅ | ✅ | ❌ | ✅ |
| DELETE /api/cart/items/* | ✅ | ❌ | ❌ | ✅ | ✅ |
| PATCH /api/seller/products/* | ❌ | ✅ (own) | ❌ | ❌ | ✅ |
| GET /api/seller/earnings | ❌ | ✅ | ❌ | ❌ | ✅ |
| POST /api/seller/payout | ❌ | ✅ | ❌ | ❌ | ✅ |
| PUT /api/transfer/products/*/stock | ❌ | ❌ | ✅ | ❌ | ✅ |

---

## Business Rules

### Payment
- **Payment Intent**: Authorizes payment (holds funds)
- **Payment Capture**: Completes payment (charges customer)
- **Stored Methods**: Tokenized via gateway (Stripe/PayPal)
- **Security**: Never store raw card numbers or CVV

### Inventory
- **Stock Visibility**: All customers see stock levels
- **Stock Reservation**: Prevents overselling
- **Auto Reduction**: Stock decreases on purchase
- **Auto Release**: Stock restored on cancellation

### Seller Payouts
- **Platform Fee**: 20% (seller gets 80%)
- **Eligibility**: Delivered 14+ days ago
- **Exclusions**: Returns, refunds, cancelled orders
- **Calculation**: `seller_earnings = (gross_sales - returns - refunds) × 0.80`

### Cart Security
- **User Isolation**: Users only access own carts
- **Customer Service**: Can assist but not purchase
- **Validation**: Stock checked on add/update
- **Quantity Control**: Auto-reduce if seller lowers stock

---

## Testing Checklist

- [ ] Add payment method
- [ ] Create payment intent
- [ ] Complete checkout (two-step)
- [ ] One-click checkout (stored method)
- [ ] View products with stock
- [ ] Remove cart item
- [ ] Update cart quantity
- [ ] Clear cart
- [ ] Seller edit product
- [ ] Seller update stock
- [ ] Seller calculate earnings
- [ ] Seller trigger payout
- [ ] Seller view payout history
- [ ] Transfer update stock
- [ ] Verify user isolation
- [ ] Test role permissions
