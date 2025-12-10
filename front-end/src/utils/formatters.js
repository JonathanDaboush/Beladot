/**
 * Formatting Utilities
 * Consistent data display formatting across the application
 */

// Format currency with symbol
export const formatCurrency = (amount, currency = 'USD') => {
  const symbols = {
    USD: '$',
    EUR: '€',
    GBP: '£',
    JPY: '¥',
    CAD: 'CA$',
    AUD: 'A$',
  };

  const symbol = symbols[currency] || currency;
  const formatted = new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);

  return `${symbol}${formatted}`;
};

// Format date to locale string
export const formatDate = (dateString, includeTime = false) => {
  if (!dateString) return 'N/A';
  
  const date = new Date(dateString);
  const options = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  };

  if (includeTime) {
    options.hour = '2-digit';
    options.minute = '2-digit';
  }

  return date.toLocaleDateString('en-US', options);
};

// Format date to relative time (e.g., "2 hours ago")
export const formatRelativeTime = (dateString) => {
  if (!dateString) return 'N/A';

  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) return 'Just now';
  if (diffMin < 60) return `${diffMin} minute${diffMin !== 1 ? 's' : ''} ago`;
  if (diffHour < 24) return `${diffHour} hour${diffHour !== 1 ? 's' : ''} ago`;
  if (diffDay < 7) return `${diffDay} day${diffDay !== 1 ? 's' : ''} ago`;
  
  return formatDate(dateString);
};

// Format phone number
export const formatPhoneNumber = (phoneNumber) => {
  if (!phoneNumber) return 'N/A';
  
  // Remove all non-digit characters
  const cleaned = phoneNumber.replace(/\D/g, '');
  
  // Format as (XXX) XXX-XXXX for US numbers
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  }
  
  // Return original if not 10 digits
  return phoneNumber;
};

// Format percentage
export const formatPercentage = (value, decimals = 1) => {
  if (value === null || value === undefined) return 'N/A';
  return `${value.toFixed(decimals)}%`;
};

// Format file size
export const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

// Format order status with color
export const getOrderStatusBadge = (status) => {
  const statusConfig = {
    PENDING: { text: 'Pending', color: 'warning' },
    PROCESSING: { text: 'Processing', color: 'info' },
    SHIPPED: { text: 'Shipped', color: 'primary' },
    DELIVERED: { text: 'Delivered', color: 'success' },
    CANCELLED: { text: 'Cancelled', color: 'danger' },
    REFUNDED: { text: 'Refunded', color: 'secondary' },
  };
  
  return statusConfig[status] || { text: status, color: 'secondary' };
};

// Format payment status
export const getPaymentStatusBadge = (status) => {
  const statusConfig = {
    PENDING: { text: 'Pending', color: 'warning' },
    COMPLETED: { text: 'Completed', color: 'success' },
    FAILED: { text: 'Failed', color: 'danger' },
    REFUNDED: { text: 'Refunded', color: 'info' },
  };
  
  return statusConfig[status] || { text: status, color: 'secondary' };
};

// Format shipment status
export const getShipmentStatusBadge = (status) => {
  const statusConfig = {
    PENDING: { text: 'Pending Pickup', color: 'warning' },
    IN_TRANSIT: { text: 'In Transit', color: 'info' },
    OUT_FOR_DELIVERY: { text: 'Out for Delivery', color: 'primary' },
    DELIVERED: { text: 'Delivered', color: 'success' },
    RETURNED: { text: 'Returned', color: 'danger' },
  };
  
  return statusConfig[status] || { text: status, color: 'secondary' };
};

// Truncate text with ellipsis
export const truncateText = (text, maxLength = 50) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}...`;
};

// Format address for display
export const formatAddress = (address) => {
  if (!address) return 'N/A';
  
  const parts = [
    address.street_address,
    address.city,
    address.state,
    address.postal_code,
    address.country,
  ].filter(Boolean);
  
  return parts.join(', ');
};

// Format name (First Last)
export const formatName = (firstName, lastName) => {
  const parts = [firstName, lastName].filter(Boolean);
  return parts.join(' ') || 'N/A';
};

// Format duration (e.g., minutes to hours:minutes)
export const formatDuration = (minutes) => {
  if (!minutes) return '0m';
  
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  
  if (hours === 0) return `${mins}m`;
  if (mins === 0) return `${hours}h`;
  return `${hours}h ${mins}m`;
};

// Format inventory quantity with status color
export const getInventoryStatus = (quantity, lowStockThreshold = 10) => {
  if (quantity === 0) {
    return { text: 'Out of Stock', color: 'danger' };
  }
  if (quantity <= lowStockThreshold) {
    return { text: `Low Stock (${quantity})`, color: 'warning' };
  }
  return { text: `In Stock (${quantity})`, color: 'success' };
};

// Format hours worked (decimal to hours:minutes)
export const formatHoursWorked = (decimalHours) => {
  if (!decimalHours) return '0h 0m';
  
  const hours = Math.floor(decimalHours);
  const minutes = Math.round((decimalHours - hours) * 60);
  
  return `${hours}h ${minutes}m`;
};

// Format score/rating
export const formatRating = (rating, maxRating = 5) => {
  if (!rating) return 'N/A';
  return `${rating.toFixed(1)}/${maxRating}`;
};

// Format CSV filename with timestamp
export const formatExportFilename = (prefix) => {
  const timestamp = new Date().toISOString().split('T')[0];
  return `${prefix}_${timestamp}.csv`;
};

// Format boolean to Yes/No
export const formatBoolean = (value) => {
  return value ? 'Yes' : 'No';
};

// Format array as comma-separated list
export const formatList = (array, maxItems = 3) => {
  if (!array || array.length === 0) return 'None';
  
  if (array.length <= maxItems) {
    return array.join(', ');
  }
  
  const visible = array.slice(0, maxItems).join(', ');
  const remaining = array.length - maxItems;
  return `${visible} +${remaining} more`;
};

// Format error message for user display
export const formatErrorMessage = (error) => {
  if (typeof error === 'string') return error;
  if (error?.response?.data?.message) return error.response.data.message;
  if (error?.message) return error.message;
  return 'An unexpected error occurred. Please try again.';
};

// Format validation errors
export const formatValidationErrors = (errors) => {
  if (!errors || typeof errors !== 'object') return null;
  
  return Object.entries(errors)
    .map(([field, messages]) => {
      const fieldName = field.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
      const errorList = Array.isArray(messages) ? messages : [messages];
      return `${fieldName}: ${errorList.join(', ')}`;
    })
    .join('; ');
};
