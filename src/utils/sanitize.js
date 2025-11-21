import DOMPurify from 'isomorphic-dompurify';

/**
 * Sanitizes user input to prevent XSS attacks
 * @param {string} dirty - The unsanitized input string
 * @param {Object} options - DOMPurify configuration options
 * @returns {string} - The sanitized string
 */
export const sanitizeInput = (dirty, options = {}) => {
  if (typeof dirty !== 'string') {
    return dirty;
  }

  const defaultConfig = {
    ALLOWED_TAGS: [], // Strip all HTML tags by default
    ALLOWED_ATTR: [],
    KEEP_CONTENT: true, // Keep text content when stripping tags
    ...options,
  };

  return DOMPurify.sanitize(dirty, defaultConfig);
};

/**
 * Sanitizes HTML content while allowing safe tags
 * @param {string} dirty - The unsanitized HTML string
 * @returns {string} - The sanitized HTML string
 */
export const sanitizeHTML = (dirty) => {
  if (typeof dirty !== 'string') {
    return dirty;
  }

  const config = {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li', 'span'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
    ALLOW_DATA_ATTR: false,
  };

  return DOMPurify.sanitize(dirty, config);
};

/**
 * Sanitizes an object's string properties recursively
 * @param {Object} obj - The object to sanitize
 * @returns {Object} - The sanitized object
 */
export const sanitizeObject = (obj) => {
  if (typeof obj !== 'object' || obj === null) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(item => sanitizeObject(item));
  }

  const sanitized = {};
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'string') {
      sanitized[key] = sanitizeInput(value);
    } else if (typeof value === 'object' && value !== null) {
      sanitized[key] = sanitizeObject(value);
    } else {
      sanitized[key] = value;
    }
  }

  return sanitized;
};

/**
 * Validates and sanitizes email addresses
 * @param {string} email - The email to validate and sanitize
 * @returns {string|null} - The sanitized email or null if invalid
 */
export const sanitizeEmail = (email) => {
  if (typeof email !== 'string') {
    return null;
  }

  const sanitized = sanitizeInput(email.trim().toLowerCase());
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  return emailRegex.test(sanitized) ? sanitized : null;
};

/**
 * Sanitizes localStorage data before storing
 * @param {string} key - The localStorage key
 * @param {any} value - The value to store
 */
export const setSecureLocalStorage = (key, value) => {
  try {
    const sanitizedKey = sanitizeInput(key);
    let sanitizedValue = value;

    if (typeof value === 'string') {
      sanitizedValue = sanitizeInput(value);
    } else if (typeof value === 'object' && value !== null) {
      sanitizedValue = sanitizeObject(value);
    }

    localStorage.setItem(sanitizedKey, JSON.stringify(sanitizedValue));
  } catch (error) {
    console.error('Error setting secure localStorage:', error);
  }
};

/**
 * Retrieves and validates data from localStorage
 * @param {string} key - The localStorage key
 * @returns {any} - The sanitized value or null
 */
export const getSecureLocalStorage = (key) => {
  try {
    const sanitizedKey = sanitizeInput(key);
    const item = localStorage.getItem(sanitizedKey);

    if (!item) {
      return null;
    }

    const parsed = JSON.parse(item);

    if (typeof parsed === 'string') {
      return sanitizeInput(parsed);
    } else if (typeof parsed === 'object' && parsed !== null) {
      return sanitizeObject(parsed);
    }

    return parsed;
  } catch (error) {
    console.error('Error getting secure localStorage:', error);
    return null;
  }
};

export default {
  sanitizeInput,
  sanitizeHTML,
  sanitizeObject,
  sanitizeEmail,
  setSecureLocalStorage,
  getSecureLocalStorage,
};
