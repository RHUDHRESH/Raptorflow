/**
 * Validation utilities for form inputs
 */

/**
 * Validates email format
 * @param {string} email - Email to validate
 * @returns {Object} - { isValid: boolean, error: string }
 */
export const validateEmail = (email) => {
  if (!email || typeof email !== 'string') {
    return { isValid: false, error: 'Email is required' };
  }

  const trimmed = email.trim();
  if (trimmed.length === 0) {
    return { isValid: false, error: 'Email is required' };
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(trimmed)) {
    return { isValid: false, error: 'Invalid email format' };
  }

  if (trimmed.length > 254) {
    return { isValid: false, error: 'Email is too long' };
  }

  return { isValid: true, error: null };
};

/**
 * Validates password strength
 * @param {string} password - Password to validate
 * @returns {Object} - { isValid: boolean, error: string, strength: string }
 */
export const validatePassword = (password) => {
  if (!password || typeof password !== 'string') {
    return { isValid: false, error: 'Password is required', strength: 'none' };
  }

  if (password.length < 8) {
    return { isValid: false, error: 'Password must be at least 8 characters', strength: 'weak' };
  }

  if (password.length > 128) {
    return { isValid: false, error: 'Password is too long', strength: 'none' };
  }

  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);

  const criteriaMet = [hasUpperCase, hasLowerCase, hasNumbers, hasSpecialChar].filter(Boolean).length;

  if (criteriaMet < 3) {
    return {
      isValid: false,
      error: 'Password must contain at least 3 of: uppercase, lowercase, numbers, special characters',
      strength: 'weak',
    };
  }

  const strength = criteriaMet === 4 ? 'strong' : 'medium';

  return { isValid: true, error: null, strength };
};

/**
 * Validates required text field
 * @param {string} value - Value to validate
 * @param {string} fieldName - Field name for error message
 * @param {number} minLength - Minimum length (default: 1)
 * @param {number} maxLength - Maximum length (default: 255)
 * @returns {Object} - { isValid: boolean, error: string }
 */
export const validateRequired = (value, fieldName = 'Field', minLength = 1, maxLength = 255) => {
  if (!value || typeof value !== 'string') {
    return { isValid: false, error: `${fieldName} is required` };
  }

  const trimmed = value.trim();
  if (trimmed.length < minLength) {
    return { isValid: false, error: `${fieldName} must be at least ${minLength} characters` };
  }

  if (trimmed.length > maxLength) {
    return { isValid: false, error: `${fieldName} must be less than ${maxLength} characters` };
  }

  return { isValid: true, error: null };
};

/**
 * Validates phone number format
 * @param {string} phone - Phone number to validate
 * @returns {Object} - { isValid: boolean, error: string }
 */
export const validatePhone = (phone) => {
  if (!phone || typeof phone !== 'string') {
    return { isValid: true, error: null }; // Phone is optional
  }

  const trimmed = phone.trim();
  if (trimmed.length === 0) {
    return { isValid: true, error: null };
  }

  // Allow various phone formats: +1-234-567-8900, (234) 567-8900, 234-567-8900, etc.
  const phoneRegex = /^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$/;
  if (!phoneRegex.test(trimmed)) {
    return { isValid: false, error: 'Invalid phone number format' };
  }

  return { isValid: true, error: null };
};

/**
 * Validates URL format
 * @param {string} url - URL to validate
 * @param {boolean} required - Whether URL is required
 * @returns {Object} - { isValid: boolean, error: string }
 */
export const validateURL = (url, required = false) => {
  if (!url || typeof url !== 'string') {
    return required
      ? { isValid: false, error: 'URL is required' }
      : { isValid: true, error: null };
  }

  const trimmed = url.trim();
  if (trimmed.length === 0) {
    return required
      ? { isValid: false, error: 'URL is required' }
      : { isValid: true, error: null };
  }

  try {
    new URL(trimmed);
    return { isValid: true, error: null };
  } catch (e) {
    return { isValid: false, error: 'Invalid URL format' };
  }
};

/**
 * Validates text area content
 * @param {string} value - Text area content
 * @param {string} fieldName - Field name for error message
 * @param {number} maxLength - Maximum length (default: 5000)
 * @returns {Object} - { isValid: boolean, error: string }
 */
export const validateTextArea = (value, fieldName = 'Field', maxLength = 5000) => {
  if (!value || typeof value !== 'string') {
    return { isValid: true, error: null }; // Text areas are usually optional
  }

  const trimmed = value.trim();
  if (trimmed.length > maxLength) {
    return { isValid: false, error: `${fieldName} must be less than ${maxLength} characters` };
  }

  return { isValid: true, error: null };
};

/**
 * Validates a form object with multiple fields
 * @param {Object} formData - Form data object
 * @param {Object} rules - Validation rules object
 * @returns {Object} - { isValid: boolean, errors: Object }
 */
export const validateForm = (formData, rules) => {
  const errors = {};
  let isValid = true;

  for (const [field, rule] of Object.entries(rules)) {
    const value = formData[field];
    let result = { isValid: true, error: null };

    switch (rule.type) {
      case 'email':
        result = validateEmail(value);
        break;
      case 'password':
        result = validatePassword(value);
        break;
      case 'required':
        result = validateRequired(value, rule.label, rule.minLength, rule.maxLength);
        break;
      case 'phone':
        result = validatePhone(value);
        break;
      case 'url':
        result = validateURL(value, rule.required);
        break;
      case 'textarea':
        result = validateTextArea(value, rule.label, rule.maxLength);
        break;
      default:
        break;
    }

    if (!result.isValid) {
      errors[field] = result.error;
      isValid = false;
    }
  }

  return { isValid, errors };
};

/**
 * Validates that passwords match
 * @param {string} password - Password
 * @param {string} confirmPassword - Confirm password
 * @returns {Object} - { isValid: boolean, error: string }
 */
export const validatePasswordMatch = (password, confirmPassword) => {
  if (password !== confirmPassword) {
    return { isValid: false, error: 'Passwords do not match' };
  }

  return { isValid: true, error: null };
};

export default {
  validateEmail,
  validatePassword,
  validateRequired,
  validatePhone,
  validateURL,
  validateTextArea,
  validateForm,
  validatePasswordMatch,
};
