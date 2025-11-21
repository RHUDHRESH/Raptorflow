import { describe, it, expect } from 'vitest';
import {
  validateEmail,
  validatePassword,
  validateUsername,
  validateRequired,
  validateLength,
  validateMatch
} from '../validation';

describe('Email Validation', () => {
  it('should validate correct email addresses', () => {
    const validEmails = [
      'user@example.com',
      'test.user@domain.co.uk',
      'john+tag@company.org',
      'admin_123@test-domain.com'
    ];

    validEmails.forEach(email => {
      const result = validateEmail(email);
      expect(result.isValid).toBe(true);
      expect(result.error).toBeNull();
    });
  });

  it('should reject invalid email addresses', () => {
    const invalidEmails = [
      'invalid',
      '@example.com',
      'user@',
      'user @example.com',
      'user@.com',
      '',
      'user@domain',
      'user..name@example.com'
    ];

    invalidEmails.forEach(email => {
      const result = validateEmail(email);
      expect(result.isValid).toBe(false);
      expect(result.error).toBeTruthy();
    });
  });

  it('should reject emails exceeding max length', () => {
    const longEmail = 'a'.repeat(250) + '@example.com';
    const result = validateEmail(longEmail);
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('too long');
  });

  it('should handle null and undefined gracefully', () => {
    expect(validateEmail(null).isValid).toBe(false);
    expect(validateEmail(undefined).isValid).toBe(false);
  });
});

describe('Password Validation', () => {
  it('should validate strong passwords', () => {
    const strongPasswords = [
      'MyP@ssw0rd!',
      'Secure123!Pass',
      'C0mpl3x!Pwd',
      'Test@1234Pass'
    ];

    strongPasswords.forEach(password => {
      const result = validatePassword(password);
      expect(result.isValid).toBe(true);
      expect(result.error).toBeNull();
      expect(result.strength).toBe('strong');
    });
  });

  it('should validate medium strength passwords', () => {
    const mediumPasswords = [
      'password123',
      'Test1234',
      'simplePass1'
    ];

    mediumPasswords.forEach(password => {
      const result = validatePassword(password);
      expect(result.isValid).toBe(true);
      expect(result.error).toBeNull();
      expect(['medium', 'strong']).toContain(result.strength);
    });
  });

  it('should reject weak passwords', () => {
    const weakPasswords = [
      'pass',
      '1234567',
      'short1',
      'abc'
    ];

    weakPasswords.forEach(password => {
      const result = validatePassword(password);
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('at least 8 characters');
    });
  });

  it('should reject passwords exceeding max length', () => {
    const longPassword = 'A'.repeat(130) + '1!';
    const result = validatePassword(longPassword);
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('too long');
  });

  it('should require at least 3 of 4 character types', () => {
    const result = validatePassword('onlylowercase');
    expect(result.isValid).toBe(false);
    expect(result.error).toBeTruthy();
  });

  it('should handle empty passwords', () => {
    const result = validatePassword('');
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('at least 8 characters');
  });

  it('should handle null and undefined', () => {
    expect(validatePassword(null).isValid).toBe(false);
    expect(validatePassword(undefined).isValid).toBe(false);
  });
});

describe('Username Validation', () => {
  it('should validate correct usernames', () => {
    const validUsernames = [
      'john_doe',
      'user123',
      'test-user',
      'JohnDoe2024'
    ];

    validUsernames.forEach(username => {
      const result = validateUsername(username);
      expect(result.isValid).toBe(true);
      expect(result.error).toBeNull();
    });
  });

  it('should reject usernames that are too short', () => {
    const result = validateUsername('ab');
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('at least 3 characters');
  });

  it('should reject usernames that are too long', () => {
    const longUsername = 'a'.repeat(31);
    const result = validateUsername(longUsername);
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('cannot exceed 30 characters');
  });

  it('should reject usernames with invalid characters', () => {
    const invalidUsernames = [
      'user@name',
      'test user',
      'user#123',
      'test!name'
    ];

    invalidUsernames.forEach(username => {
      const result = validateUsername(username);
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('letters, numbers, hyphens, and underscores');
    });
  });

  it('should handle empty usernames', () => {
    const result = validateUsername('');
    expect(result.isValid).toBe(false);
    expect(result.error).toBeTruthy();
  });
});

describe('Required Field Validation', () => {
  it('should validate non-empty strings', () => {
    const result = validateRequired('test value', 'Field');
    expect(result.isValid).toBe(true);
    expect(result.error).toBeNull();
  });

  it('should reject empty strings', () => {
    const result = validateRequired('', 'Field');
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('required');
  });

  it('should reject whitespace-only strings', () => {
    const result = validateRequired('   ', 'Field');
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('required');
  });

  it('should reject null and undefined', () => {
    expect(validateRequired(null, 'Field').isValid).toBe(false);
    expect(validateRequired(undefined, 'Field').isValid).toBe(false);
  });

  it('should use custom field name in error message', () => {
    const result = validateRequired('', 'Email address');
    expect(result.error).toContain('Email address');
  });
});

describe('Length Validation', () => {
  it('should validate strings within length range', () => {
    const result = validateLength('test', 2, 10, 'Field');
    expect(result.isValid).toBe(true);
    expect(result.error).toBeNull();
  });

  it('should reject strings below minimum length', () => {
    const result = validateLength('ab', 3, 10, 'Field');
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('at least 3 characters');
  });

  it('should reject strings above maximum length', () => {
    const result = validateLength('toolongvalue', 3, 10, 'Field');
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('cannot exceed 10 characters');
  });

  it('should accept strings at exact boundaries', () => {
    expect(validateLength('abc', 3, 5, 'Field').isValid).toBe(true);
    expect(validateLength('abcde', 3, 5, 'Field').isValid).toBe(true);
  });

  it('should handle null and undefined', () => {
    expect(validateLength(null, 3, 10, 'Field').isValid).toBe(false);
    expect(validateLength(undefined, 3, 10, 'Field').isValid).toBe(false);
  });
});

describe('Match Validation', () => {
  it('should validate matching values', () => {
    const result = validateMatch('password123', 'password123', 'Password');
    expect(result.isValid).toBe(true);
    expect(result.error).toBeNull();
  });

  it('should reject non-matching values', () => {
    const result = validateMatch('password123', 'password456', 'Password');
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('do not match');
  });

  it('should be case-sensitive', () => {
    const result = validateMatch('Password', 'password', 'Password');
    expect(result.isValid).toBe(false);
  });

  it('should handle empty strings', () => {
    const result = validateMatch('', '', 'Password');
    expect(result.isValid).toBe(true);
  });

  it('should handle null and undefined', () => {
    expect(validateMatch(null, null, 'Field').isValid).toBe(true);
    expect(validateMatch(null, 'value', 'Field').isValid).toBe(false);
    expect(validateMatch('value', null, 'Field').isValid).toBe(false);
  });
});

describe('Edge Cases and Integration', () => {
  it('should handle very long strings gracefully', () => {
    const veryLongString = 'a'.repeat(10000);
    const emailResult = validateEmail(veryLongString + '@example.com');
    expect(emailResult.isValid).toBe(false);
  });

  it('should handle special characters in passwords', () => {
    const specialChars = '!@#$%^&*()_+-=[]{}|;:,.<>?';
    const password = 'Test123' + specialChars;
    const result = validatePassword(password);
    expect(result.isValid).toBe(true);
  });

  it('should handle Unicode characters', () => {
    const unicodeEmail = 'user@例え.jp';
    const result = validateEmail(unicodeEmail);
    // Should fail basic email validation
    expect(result.isValid).toBe(false);
  });

  it('should validate multiple fields in sequence', () => {
    const email = validateEmail('test@example.com');
    const password = validatePassword('SecureP@ss123');
    const username = validateUsername('testuser');

    expect(email.isValid).toBe(true);
    expect(password.isValid).toBe(true);
    expect(username.isValid).toBe(true);
  });
});
