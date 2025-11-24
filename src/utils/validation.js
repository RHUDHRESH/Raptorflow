/**
 * Validation utilities for form inputs
 */

/**
 * Validates email format
 * @param {string} email - Email to validate
 * @returns {Object} - { isValid: boolean, error: string }
 */
export const validateEmail = (email) => {
  if (email === null || email === undefined) {
    return { isValid: false, error: 'Email is required' };
  }

  if (typeof email !== 'string') {
    return { isValid: false, error: 'Email is required' };
  }

  const trimmed = email.trim();
  if (trimmed.length === 0) {
    return { isValid: false, error: 'Email is required' };
  }

  if (trimmed.length > 254) {
    return { isValid: false, error: 'Email is too long' };
  }

  const emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
  const hasConsecutiveDots = /(\.\.)/.test(trimmed);
  const asciiOnly = [...trimmed].every(char => char.charCodeAt(0) <= 127);

  if (!asciiOnly || hasConsecutiveDots || !emailRegex.test(trimmed)) {
    return { isValid: false, error: 'Invalid email format' };
  }

  return { isValid: true, error: null };
};

/**
 * Validates password strength
 * @param {string} password - Password to validate
 * @returns {Object} - { isValid: boolean, error: string, strength: string }
 */
export const validatePassword = (password) => {
  if (password === null || password === undefined) {
    return { isValid: false, error: 'Password is required', strength: 'none' };
  }

  if (typeof password !== 'string') {
    return { isValid: false, error: 'Password is required', strength: 'none' };
  }

  if (password.length === 0) {
    return { isValid: false, error: 'Password must be at least 8 characters', strength: 'weak' };
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
  const hasSpecialChar = /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password);

  const criteriaMet = [hasUpperCase, hasLowerCase, hasNumbers, hasSpecialChar].filter(Boolean).length;

  if (criteriaMet < 2) {
    return {
      isValid: false,
      error: 'Password must include at least two of: uppercase, lowercase, numbers, special characters',
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
  if (value === null || value === undefined || typeof value !== 'string') {
    return { isValid: false, error: `${fieldName} is required` };
  }

  const trimmed = value.trim();
  if (trimmed.length === 0) {
    return { isValid: false, error: `${fieldName} is required` };
  }

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
  // eslint-disable-next-line no-useless-escape
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
 * Validates username format and length
 */
export const validateUsername = (username) => {
  if (username === null || username === undefined) {
    return { isValid: false, error: 'Username is required' };
  }

  if (typeof username !== 'string') {
    return { isValid: false, error: 'Username is required' };
  }

  const trimmed = username.trim();
  if (trimmed.length === 0) {
    return { isValid: false, error: 'Username is required' };
  }

  if (trimmed.length < 3) {
    return { isValid: false, error: 'Username must be at least 3 characters' };
  }

  if (trimmed.length > 30) {
    return { isValid: false, error: 'Username cannot exceed 30 characters' };
  }

  if (!/^[A-Za-z0-9_-]+$/.test(trimmed)) {
    return { isValid: false, error: 'Username can only include letters, numbers, hyphens, and underscores' };
  }

  return { isValid: true, error: null };
};

/**
 * Validates generic string length
 */
export const validateLength = (value, minLength = 0, maxLength = Infinity, fieldName = 'Field') => {
  if (typeof value !== 'string') {
    return { isValid: false, error: `${fieldName} is required` };
  }

  const length = value.length;

  if (length < minLength) {
    return { isValid: false, error: `${fieldName} must be at least ${minLength} characters` };
  }

  if (length > maxLength) {
    return { isValid: false, error: `${fieldName} cannot exceed ${maxLength} characters` };
  }

  return { isValid: true, error: null };
};

/**
 * Validates that two fields match
 */
export const validateMatch = (value, compareValue, fieldName = 'Field') => {
  const first = value === null || value === undefined ? '' : value;
  const second = compareValue === null || compareValue === undefined ? '' : compareValue;

  if (first === '' && second === '') {
    return { isValid: true, error: null };
  }

  if (first === second) {
    return { isValid: true, error: null };
  }

  return { isValid: false, error: `${fieldName}s do not match` };
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
      case 'username':
        result = validateUsername(value);
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
      case 'length':
        result = validateLength(value, rule.minLength, rule.maxLength, rule.label);
        break;
      case 'match':
        result = validateMatch(value, formData[rule.matchField], rule.label);
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
  validateUsername,
  validatePhone,
  validateURL,
  validateTextArea,
  validateLength,
  validateMatch,
  validateForm,
  validatePasswordMatch,
};
