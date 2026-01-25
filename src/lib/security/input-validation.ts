// Input validation utilities for security
import DOMPurify from 'isomorphic-dompurify';

// Email validation regex
const EMAIL_REGEX = /^[^\s]*([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\s*$/;

// Password strength validation
const PASSWORD_REGEX = {
  minLength: 8,
  hasUpperCase: /[A-Z]/,
  hasLowerCase: /[a-z]/,
  hasNumber: /\d/,
  hasSpecialChar: /[[\]!@#$%^&*()_+\-=\\{};':"\\|,.<>/?]/,
  noSpaces: /^\S+$/
};

// Sanitization configuration
const SANITIZE_CONFIG = {
  ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a'],
  ALLOWED_ATTR: ['href', 'target', 'title', 'rel'],
  ALLOW_DATA_ATTR: false
};

// Input validation functions
export const validateEmail = (email: string): boolean => {
  if (!email || typeof email !== 'string') return false;
  return EMAIL_REGEX.test(email.trim());
};

export const validatePassword = (password: string): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  if (!password || typeof password !== 'string') {
    errors.push('Password is required');
    return { isValid: false, errors };
  }
  
  const trimmedPassword = password.trim();
  
  if (trimmedPassword.length < PASSWORD_REGEX.minLength) {
    errors.push(`Password must be at least ${PASSWORD_REGEX.minLength} characters long`);
  }
  
  if (!PASSWORD_REGEX.hasUpperCase.test(trimmedPassword)) {
    errors.push('Password must contain at least one uppercase letter');
  }
  
  if (!PASSWORD_REGEX.hasLowerCase.test(trimmedPassword)) {
    errors.push('Password must contain at least one lowercase letter');
  }
  
  if (!PASSWORD_REGEX.hasNumber.test(trimmedPassword)) {
    errors.push('password must contain at least one number');
  }
  
  if (!PASSWORD_REGEX.hasSpecialChar.test(trimmedPassword)) {
    errors.push('Password must contain at least one special character');
  }
  
  if (!PASSWORD_REGEX.noSpaces.test(trimmedPassword)) {
    errors.push('Password cannot contain spaces');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

export const validateName = (name: string, minLength: number = 2, maxLength: number = 100): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  if (!name || typeof name !== 'string') {
    errors.push('Name is required');
    return { isValid: false, errors };
  }
  
  const trimmedName = name.trim();
  
  if (trimmedName.length < minLength) {
    errors.push(`Name must be at least ${minLength} characters long`);
  }
  
  if (trimmedName.length > maxLength) {
    errors.push(`Name cannot be more than ${maxLength} characters long`);
  }
  
  // Check for valid characters (letters, spaces, hyphens, apostrophes)
  const nameRegex = /^[a-zA-Z\s\-']+$/;
  if (!nameRegex.test(trimmedName)) {
    errors.push('Name can only contain letters, spaces, hyphens, and apostrophes');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

export const sanitizeInput = (input: string): string => {
  if (!input || typeof input !== 'string') return '';
  
  // Remove any HTML/JS tags and scripts
  const sanitized = DOMPurify.sanitize(input, SANITIZE_CONFIG);
  
  // Additional sanitization
  return sanitized
    .replace(/<script[^>]*>.*?<\/script>/gi, '') // Remove scripts
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+\s*=/gi, '') // Remove event handlers
    .trim();
};

export const validateUrl = (url: string): boolean => {
  if (!url || typeof url !== 'string') return false;
  
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const validatePhone = (phone: string): boolean => {
  if (!phone || typeof phone !== 'string') return false;
  
  // Basic phone validation (10 digits, optional country code)
  const phoneRegex = /^\+?[\d\s\-()]{10,}$/;
  return phoneRegex.test(phone.replace(/\D/g, ''));
};

export const validateNumeric = (input: string): boolean => {
  if (!input || typeof input !== 'string') return false;
  return /^\d+$/.test(input.trim());
};

export const validateAlpha = (input: string): boolean => {
  if (!input || typeof input !== 'string') return false;
  return /^[a-zA-Z]+$/.test(input.trim());
};

export const validateAlphaNumeric = (input: string): boolean => {
  if (!input || typeof input !== 'string') return false;
  return /^[a-zA-Z0-9]+$/.test(input.trim());
};

export const validateDate = (dateString: string): boolean => {
  if (!dateString || typeof dateString !== 'string') return false;
  
  const date = new Date(dateString);
  return date instanceof Date && !isNaN(date.getTime());
};

export const validateUuid = (uuid: string): boolean => {
  if (!uuid || typeof uuid !== 'string') return false;
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
};

// SQL injection prevention
export const sanitizeSqlInput = (input: string): string => {
  if (!input || typeof input !== 'string') return '';
  
  // Remove common SQL injection patterns
  return input
    .replace(/['"]/g, '') // Remove quotes
    .replace(/;/g, '') // Remove semicolons
    .replace(/--/g, '') // Remove SQL comments
    .replace(/\/\*/g, '') // Remove SQL comments
    .replace(/\*\//g, '') // Remove SQL comments
    .replace(/\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b/gi, '') // Remove SQL keywords
    .trim();
};

// XSS prevention
export const escapeHtml = (unsafe: string): string => {
  if (!unsafe || typeof unsafe !== 'string') return '';
  
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
};

// CSRF token validation
export const validateCsrfToken = (token: string, sessionToken: string): boolean => {
  if (!token || !sessionToken || typeof token !== 'string' || typeof sessionToken !== 'string') {
    return false;
  }
  
  // Simple token comparison (in production, use HMAC)
  return token === sessionToken && token.length > 20;
};

// File upload validation
export const validateFileUpload = (file: File, allowedTypes: string[], maxSize: number): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  if (!file) {
    errors.push('No file provided');
    return { isValid: false, errors };
  }
  
  // Check file type
  if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
    errors.push(`File type ${file.type} is not allowed`);
  }
  
  // Check file size
  if (file.size > maxSize) {
    errors.push(`File size exceeds maximum allowed size of ${maxSize} bytes`);
  }
  
  // Check file name for suspicious patterns
  const suspiciousPatterns = ['<script', 'javascript:', 'vbscript:', 'onload=', 'onerror='];
  const fileName = file.name.toLowerCase();
  
  for (const pattern of suspiciousPatterns) {
    if (fileName.includes(pattern)) {
      errors.push('File name contains suspicious content');
      break;
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

// Rate limiting helper
export const createRateLimitKey = (identifier: string, endpoint: string): string => {
  return `${identifier}:${endpoint}`;
};

// Security headers helper
export const getSecurityHeaders = (): Record<string, string> => ({
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), payment=()',
  'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:apis.google.com https://accounts.google.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https: blob:; font-src 'self' data:; connect-src 'self' https://api.supabase.io https://*.supabase.co https://accounts.google.com https://oauth2.googleapis.com; frame-ancestors 'none';"
});

// Input sanitization middleware helper
export const sanitizeRequestData = (data: Record<string, any>): Record<string, any> => {
  const sanitized: Record<string, any> = {};
  
  for (const [key, value] of Object.entries(data)) {
    if (typeof value === 'string') {
      sanitized[key] = sanitizeInput(value);
    } else if (Array.isArray(value)) {
      sanitized[key] = value.map(item => 
        typeof item === 'string' ? sanitizeInput(item) : item
      );
    } else if (typeof value === 'object' && value !== null) {
      sanitized[key] = sanitizeRequestData(value);
    } else {
      sanitized[key] = value;
    }
  }
  
  return sanitized;
};
