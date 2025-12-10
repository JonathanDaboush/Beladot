/**
 * Business Constants
 * Centralized business rules and configuration values
 */

// Order statuses
export const ORDER_STATUS = {
  PENDING: 'PENDING',
  PROCESSING: 'PROCESSING',
  SHIPPED: 'SHIPPED',
  DELIVERED: 'DELIVERED',
  CANCELLED: 'CANCELLED',
  REFUNDED: 'REFUNDED',
};

// Payment statuses
export const PAYMENT_STATUS = {
  PENDING: 'PENDING',
  COMPLETED: 'COMPLETED',
  FAILED: 'FAILED',
  REFUNDED: 'REFUNDED',
};

// Shipment statuses
export const SHIPMENT_STATUS = {
  PENDING: 'PENDING',
  IN_TRANSIT: 'IN_TRANSIT',
  OUT_FOR_DELIVERY: 'OUT_FOR_DELIVERY',
  DELIVERED: 'DELIVERED',
  RETURNED: 'RETURNED',
};

// Return statuses
export const RETURN_STATUS = {
  REQUESTED: 'REQUESTED',
  APPROVED: 'APPROVED',
  REJECTED: 'REJECTED',
  RECEIVED: 'RECEIVED',
  COMPLETED: 'COMPLETED',
};

// Refund statuses
export const REFUND_STATUS = {
  PENDING: 'PENDING',
  APPROVED: 'APPROVED',
  REJECTED: 'REJECTED',
  PROCESSED: 'PROCESSED',
};

// Leave request statuses
export const LEAVE_STATUS = {
  PENDING: 'PENDING',
  APPROVED: 'APPROVED',
  DENIED: 'DENIED',
};

// Supported currencies
export const CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD'];

// Default currency
export const DEFAULT_CURRENCY = 'USD';

// Business rules
export const BUSINESS_RULES = {
  // Cart limits
  MAX_CART_ITEMS: 100,
  MIN_ORDER_VALUE: 10,

  // Product limits
  MAX_PRODUCT_IMAGES: 10,
  MAX_PRODUCT_VARIANTS: 50,
  LOW_STOCK_THRESHOLD: 10,

  // Return/Refund policies
  RETURN_WINDOW_DAYS: 30,
  REFUND_PROCESSING_DAYS: 7,
  
  // Refund eligibility
  REFUNDABLE_STATUSES: [ORDER_STATUS.DELIVERED],
  MAX_REFUND_AMOUNT_WITHOUT_APPROVAL: 500,

  // Shipping
  FREE_SHIPPING_THRESHOLD: 50,
  EXPEDITED_SHIPPING_CUTOFF_HOUR: 14, // 2 PM

  // Employee constraints
  MAX_HOURS_PER_WEEK: 40,
  OVERTIME_THRESHOLD: 40,
  MAX_PTO_DAYS_PER_YEAR: 15,
  MAX_SICK_DAYS_PER_YEAR: 10,

  // Schedule constraints
  CS_MAX_SCHEDULE_CHANGES_PER_PERIOD: 5,
  MIN_SHIFT_DURATION_HOURS: 4,
  MAX_SHIFT_DURATION_HOURS: 12,

  // Performance thresholds
  LOW_RATING_THRESHOLD: 3.0,
  HIGH_RATING_THRESHOLD: 4.5,

  // Pagination defaults
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,

  // File upload limits
  MAX_IMAGE_SIZE_MB: 5,
  MAX_DOCUMENT_SIZE_MB: 10,
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
  ALLOWED_DOCUMENT_TYPES: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],

  // Password requirements
  MIN_PASSWORD_LENGTH: 8,
  PASSWORD_REQUIRE_UPPERCASE: true,
  PASSWORD_REQUIRE_LOWERCASE: true,
  PASSWORD_REQUIRE_NUMBER: true,
  PASSWORD_REQUIRE_SPECIAL_CHAR: true,

  // Session timeouts (minutes)
  SESSION_TIMEOUT_CUSTOMER: 1440, // 24 hours
  SESSION_TIMEOUT_EMPLOYEE: 480, // 8 hours
  SESSION_WARNING_TIME: 5, // Show warning 5 min before timeout

  // Rate limiting (per minute)
  MAX_LOGIN_ATTEMPTS: 5,
  MAX_API_REQUESTS: 100,

  // Search configuration
  MIN_SEARCH_LENGTH: 3,
  MAX_SEARCH_RESULTS: 100,

  // Discount limits
  MAX_DISCOUNT_PERCENTAGE: 90,
  MAX_COUPONS_PER_ORDER: 1,

  // Review requirements
  MIN_REVIEW_LENGTH: 10,
  MAX_REVIEW_LENGTH: 1000,
  MIN_RATING: 1,
  MAX_RATING: 5,

  // Seller requirements
  MIN_SELLER_RATING: 3.0,
  MAX_PENDING_ORDERS_BEFORE_SUSPENSION: 10,
};

// Feature flags (default values)
export const FEATURE_FLAGS = {
  // Customer features
  ENABLE_WISHLIST: true,
  ENABLE_PRODUCT_REVIEWS: true,
  ENABLE_GUEST_CHECKOUT: false,
  ENABLE_SAVED_PAYMENT_METHODS: true,
  ENABLE_LOYALTY_PROGRAM: false,

  // Seller features
  ENABLE_BULK_UPLOAD: true,
  ENABLE_PROMOTIONAL_PRICING: true,
  ENABLE_ANALYTICS_DASHBOARD: true,

  // Employee features
  ENABLE_MOBILE_CLOCK_IN: true,
  ENABLE_SHIFT_SWAPPING: true,
  ENABLE_SELF_SERVICE_SCHEDULE: true,

  // System features
  ENABLE_MULTI_CURRENCY: true,
  ENABLE_REAL_TIME_INVENTORY: true,
  ENABLE_EMAIL_NOTIFICATIONS: true,
  ENABLE_SMS_NOTIFICATIONS: false,

  // Admin features
  ENABLE_AUDIT_LOGGING: true,
  ENABLE_ADVANCED_ANALYTICS: true,
  ENABLE_A_B_TESTING: false,
};

// API configuration
export const API_CONFIG = {
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
};

// Date formats
export const DATE_FORMATS = {
  SHORT: 'MM/DD/YYYY',
  LONG: 'MMMM DD, YYYY',
  WITH_TIME: 'MM/DD/YYYY hh:mm A',
  ISO: 'YYYY-MM-DD',
};

// Tax rates by state (example - should come from backend)
export const TAX_RATES = {
  CA: 0.0725,
  NY: 0.04,
  TX: 0.0625,
  FL: 0.06,
  // Add more states as needed
};

// Shipping carriers
export const SHIPPING_CARRIERS = {
  USPS: 'USPS',
  UPS: 'UPS',
  FEDEX: 'FedEx',
  DHL: 'DHL',
};

// Payment methods
export const PAYMENT_METHODS = {
  CREDIT_CARD: 'CREDIT_CARD',
  DEBIT_CARD: 'DEBIT_CARD',
  PAYPAL: 'PAYPAL',
  APPLE_PAY: 'APPLE_PAY',
  GOOGLE_PAY: 'GOOGLE_PAY',
};

// Card types
export const CARD_TYPES = {
  VISA: 'Visa',
  MASTERCARD: 'MasterCard',
  AMEX: 'American Express',
  DISCOVER: 'Discover',
};

// Return reasons
export const RETURN_REASONS = [
  'Defective or damaged',
  'Wrong item received',
  'Item not as described',
  'No longer needed',
  'Better price found elsewhere',
  'Ordered by mistake',
  'Other',
];

// Refund reasons
export const REFUND_REASONS = [
  'Customer request',
  'Product defect',
  'Shipping delay',
  'Order cancellation',
  'Price adjustment',
  'Other',
];

// Employee departments
export const DEPARTMENTS = {
  CUSTOMER_SERVICE: 'Customer Service',
  FINANCE: 'Finance',
  TRANSPORT: 'Transport',
};

// Work shift types
export const SHIFT_TYPES = {
  MORNING: 'Morning (6AM - 2PM)',
  AFTERNOON: 'Afternoon (2PM - 10PM)',
  NIGHT: 'Night (10PM - 6AM)',
};

// Leave types
export const LEAVE_TYPES = {
  VACATION: 'Vacation',
  SICK: 'Sick Leave',
  PERSONAL: 'Personal Leave',
  UNPAID: 'Unpaid Leave',
};

// Action log types (for CS)
export const ACTION_TYPES = {
  USER_UPDATE: 'User Update',
  ORDER_UPDATE: 'Order Update',
  REFUND_PROCESSED: 'Refund Processed',
  RETURN_APPROVED: 'Return Approved',
  SELLER_UPDATE: 'Seller Update',
  TICKET_RESOLVED: 'Ticket Resolved',
};

// Product categories (example - should come from backend)
export const PRODUCT_CATEGORIES = [
  'Electronics',
  'Clothing',
  'Home & Garden',
  'Sports & Outdoors',
  'Books',
  'Toys & Games',
  'Health & Beauty',
  'Automotive',
  'Food & Grocery',
  'Office Supplies',
];

// Sort options
export const SORT_OPTIONS = {
  NEWEST: 'Newest First',
  OLDEST: 'Oldest First',
  PRICE_LOW_HIGH: 'Price: Low to High',
  PRICE_HIGH_LOW: 'Price: High to Low',
  RATING_HIGH_LOW: 'Rating: High to Low',
  NAME_A_Z: 'Name: A to Z',
};

// Toast notification types
export const TOAST_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
};

// Modal sizes
export const MODAL_SIZES = {
  SMALL: 'sm',
  MEDIUM: 'md',
  LARGE: 'lg',
  EXTRA_LARGE: 'xl',
};
