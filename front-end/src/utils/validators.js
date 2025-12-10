/**
 * Validation Utilities
 * Client-side validation helpers
 */

// Validate email format
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Validate phone number (US format)
export const isValidPhoneNumber = (phone) => {
  const phoneRegex = /^[\d\s\-\(\)]+$/;
  const cleaned = phone.replace(/\D/g, '');
  return phoneRegex.test(phone) && cleaned.length === 10;
};

// Validate password strength
export const validatePasswordStrength = (password) => {
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  const errors = [];
  if (password.length < minLength) {
    errors.push(`Password must be at least ${minLength} characters`);
  }
  if (!hasUpperCase) {
    errors.push('Password must contain at least one uppercase letter');
  }
  if (!hasLowerCase) {
    errors.push('Password must contain at least one lowercase letter');
  }
  if (!hasNumber) {
    errors.push('Password must contain at least one number');
  }
  if (!hasSpecialChar) {
    errors.push('Password must contain at least one special character');
  }

  return {
    isValid: errors.length === 0,
    errors,
    strength: calculatePasswordStrength(password),
  };
};

// Calculate password strength score
const calculatePasswordStrength = (password) => {
  let strength = 0;
  if (password.length >= 8) strength += 20;
  if (password.length >= 12) strength += 20;
  if (/[a-z]/.test(password)) strength += 20;
  if (/[A-Z]/.test(password)) strength += 20;
  if (/\d/.test(password)) strength += 10;
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength += 10;

  if (strength <= 40) return 'Weak';
  if (strength <= 70) return 'Medium';
  return 'Strong';
};

// Validate postal code (US and Canada)
export const isValidPostalCode = (postalCode, country = 'US') => {
  if (country === 'US') {
    return /^\d{5}(-\d{4})?$/.test(postalCode);
  }
  if (country === 'CA') {
    return /^[A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d$/.test(postalCode);
  }
  return true; // Accept any format for other countries
};

// Validate credit card number (Luhn algorithm)
export const isValidCreditCard = (cardNumber) => {
  const cleaned = cardNumber.replace(/\D/g, '');
  
  if (cleaned.length < 13 || cleaned.length > 19) {
    return false;
  }

  let sum = 0;
  let isEven = false;

  for (let i = cleaned.length - 1; i >= 0; i--) {
    let digit = parseInt(cleaned[i], 10);

    if (isEven) {
      digit *= 2;
      if (digit > 9) {
        digit -= 9;
      }
    }

    sum += digit;
    isEven = !isEven;
  }

  return sum % 10 === 0;
};

// Validate CVV
export const isValidCVV = (cvv, cardType = 'visa') => {
  const cleaned = cvv.replace(/\D/g, '');
  
  if (cardType === 'amex') {
    return cleaned.length === 4;
  }
  return cleaned.length === 3;
};

// Validate expiration date (MM/YY)
export const isValidExpirationDate = (expDate) => {
  const [month, year] = expDate.split('/').map((x) => parseInt(x, 10));
  
  if (!month || !year || month < 1 || month > 12) {
    return false;
  }

  const currentDate = new Date();
  const currentYear = currentDate.getFullYear() % 100;
  const currentMonth = currentDate.getMonth() + 1;

  if (year < currentYear) {
    return false;
  }
  if (year === currentYear && month < currentMonth) {
    return false;
  }

  return true;
};

// Validate URL format
export const isValidURL = (url) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

// Validate price (positive number with max 2 decimals)
export const isValidPrice = (price) => {
  const priceRegex = /^\d+(\.\d{1,2})?$/;
  return priceRegex.test(price) && parseFloat(price) >= 0;
};

// Validate quantity (positive integer)
export const isValidQuantity = (quantity) => {
  return Number.isInteger(quantity) && quantity > 0;
};

// Validate date range
export const isValidDateRange = (startDate, endDate) => {
  const start = new Date(startDate);
  const end = new Date(endDate);
  return start <= end;
};

// Validate required field
export const isRequired = (value) => {
  if (typeof value === 'string') {
    return value.trim().length > 0;
  }
  return value !== null && value !== undefined;
};

// Validate min length
export const hasMinLength = (value, minLength) => {
  return value && value.length >= minLength;
};

// Validate max length
export const hasMaxLength = (value, maxLength) => {
  return !value || value.length <= maxLength;
};

// Validate numeric range
export const isInRange = (value, min, max) => {
  const num = parseFloat(value);
  return !isNaN(num) && num >= min && num <= max;
};

// Validate file size (in bytes)
export const isValidFileSize = (file, maxSizeInMB) => {
  const maxSizeInBytes = maxSizeInMB * 1024 * 1024;
  return file.size <= maxSizeInBytes;
};

// Validate file type
export const isValidFileType = (file, allowedTypes) => {
  return allowedTypes.includes(file.type);
};

// Validate image dimensions
export const validateImageDimensions = (file, maxWidth, maxHeight) => {
  return new Promise((resolve) => {
    const img = new Image();
    const objectUrl = URL.createObjectURL(file);

    img.onload = () => {
      URL.revokeObjectURL(objectUrl);
      resolve(img.width <= maxWidth && img.height <= maxHeight);
    };

    img.onerror = () => {
      URL.revokeObjectURL(objectUrl);
      resolve(false);
    };

    img.src = objectUrl;
  });
};

// Validate form data
export const validateForm = (formData, rules) => {
  const errors = {};

  Object.keys(rules).forEach((field) => {
    const value = formData[field];
    const fieldRules = rules[field];

    if (fieldRules.required && !isRequired(value)) {
      errors[field] = `${field} is required`;
      return;
    }

    if (fieldRules.email && value && !isValidEmail(value)) {
      errors[field] = 'Invalid email format';
      return;
    }

    if (fieldRules.phone && value && !isValidPhoneNumber(value)) {
      errors[field] = 'Invalid phone number';
      return;
    }

    if (fieldRules.minLength && !hasMinLength(value, fieldRules.minLength)) {
      errors[field] = `Minimum length is ${fieldRules.minLength}`;
      return;
    }

    if (fieldRules.maxLength && !hasMaxLength(value, fieldRules.maxLength)) {
      errors[field] = `Maximum length is ${fieldRules.maxLength}`;
      return;
    }

    if (fieldRules.min !== undefined && fieldRules.max !== undefined) {
      if (!isInRange(value, fieldRules.min, fieldRules.max)) {
        errors[field] = `Value must be between ${fieldRules.min} and ${fieldRules.max}`;
      }
    }

    if (fieldRules.custom) {
      const customError = fieldRules.custom(value, formData);
      if (customError) {
        errors[field] = customError;
      }
    }
  });

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

// Sanitize user input (prevent XSS)
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input;
  
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;',
  };
  
  return input.replace(/[&<>"'/]/g, (char) => map[char]);
};
