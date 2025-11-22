import DOMPurify from 'isomorphic-dompurify';

const decodeEntities = (value) =>
  value
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
<<<<<<< Updated upstream
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#x2F;/g, '/')
    .replace(/&amp;/g, '&');
=======
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#x2F;/g, '/');

>>>>>>> Stashed changes
/**
 * Sanitizes user input to prevent XSS attacks
 * @param {string} dirty - The unsanitized input string
 * @param {Object} options - DOMPurify configuration options
 * @returns {string} - The sanitized string
 */
export const sanitizeInput = (dirty, options = {}) => {
  if (dirty === null || dirty === undefined) {
    return '';
  }

  const stringValue = typeof dirty === 'string' ? dirty : String(dirty);

  const defaultConfig = {
    ALLOWED_TAGS: [],
    ALLOWED_ATTR: [],
    KEEP_CONTENT: true,
    ...options,
  };

  let sanitized = DOMPurify.sanitize(stringValue, defaultConfig);

  if (!sanitized && /<[^>]+>/.test(stringValue)) {
    sanitized = stringValue.replace(/<[^>]*>/g, '');
  }

  const decoded = decodeEntities(sanitized);
  return decoded.replace(/javascript:/gi, '').replace(/data:/gi, '');
};

/**
 * Sanitizes HTML content while allowing safe tags
 * @param {string} dirty - The unsanitized HTML string
 * @returns {string} - The sanitized HTML string
 */
export const sanitizeHTML = (dirty) => {
  if (dirty === null || dirty === undefined) {
    return '';
  }

  if (typeof dirty !== 'string') {
    return sanitizeInput(String(dirty));
  }

  const config = {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li', 'span'],
    ALLOWED_ATTR: ['href', 'target', 'rel', 'title'],
    ALLOW_DATA_ATTR: false,
  };

  return DOMPurify.sanitize(dirty, config);
};

/**
 * Sanitizes an object's string properties recursively
 * @param {Object} obj - The object to sanitize
 * @returns {Object} - The sanitized object
 */
export const sanitizeObject = (obj, seen = new WeakSet()) => {
  if (obj === null) {
    return null;
  }

  if (typeof obj === 'string') {
    return sanitizeInput(obj);
  }

  if (typeof obj !== 'object') {
    return obj;
  }

  if (seen.has(obj)) {
    return obj;
  }

  seen.add(obj);

  if (Array.isArray(obj)) {
    return obj.map(item => sanitizeObject(item, seen));
  }

  const sanitized = {};
  for (const [key, value] of Object.entries(obj)) {
    sanitized[key] = sanitizeObject(value, seen);
  }

  return sanitized;
};

/**
 * Validates and sanitizes email addresses
 * @param {string} email - The email to validate and sanitize
 * @returns {string|null} - The sanitized email or null if invalid
 */
export const sanitizeEmail = (email) => {
  if (email === null || email === undefined) {
    return '';
  }

  const normalized = sanitizeInput(typeof email === 'string' ? email : String(email)).trim().toLowerCase();
  if (normalized.length === 0) {
    return '';
  }

  const emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
  return emailRegex.test(normalized) ? normalized : '';
};

/**
 * Sanitizes localStorage data before storing
 * @param {string} key - The localStorage key
 * @param {any} value - The value to store
 */
export const setSecureLocalStorage = (key, value) => {
  try {
    const sanitizedKey = sanitizeInput(key);
    if (!sanitizedKey) return;

    let sanitizedValue = value;
    if (value === undefined) {
      sanitizedValue = null;
    } else if (typeof value === 'string') {
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
export const getSecureLocalStorage = (key, defaultValue = null) => {
  try {
    const sanitizedKey = sanitizeInput(key);
    if (!sanitizedKey) return defaultValue;

    const item = localStorage.getItem(sanitizedKey);
    if (!item) {
      return defaultValue;
    }

    let parsed;
    try {
      parsed = JSON.parse(item);
    } catch {
      return defaultValue;
    }

    if (parsed === null) {
      return null;
    }

    if (typeof parsed === 'string') {
      return sanitizeInput(parsed);
    }

    if (typeof parsed === 'object') {
      return sanitizeObject(parsed);
    }

    return parsed;
  } catch (error) {
    console.error('Error getting secure localStorage:', error);
    return defaultValue;
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
