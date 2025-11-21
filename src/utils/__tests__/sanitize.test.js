import {
  sanitizeInput,
  sanitizeHTML,
  sanitizeObject,
  sanitizeEmail,
  setSecureLocalStorage,
  getSecureLocalStorage
} from '../sanitize';

describe('Input Sanitization', () => {
  it('should strip all HTML tags from input', () => {
    const malicious = '<script>alert("XSS")</script>Hello';
    const result = sanitizeInput(malicious);
    expect(result).toBe('Hello');
    expect(result).not.toContain('<script>');
  });

  it('should remove event handlers', () => {
    const malicious = '<div onclick="alert(\'XSS\')">Click me</div>';
    const result = sanitizeInput(malicious);
    expect(result).toBe('Click me');
    expect(result).not.toContain('onclick');
  });

  it('should handle nested HTML tags', () => {
    const nested = '<div><span><strong>Text</strong></span></div>';
    const result = sanitizeInput(nested);
    expect(result).toBe('Text');
  });

  it('should preserve plain text', () => {
    const plainText = 'Hello, World!';
    const result = sanitizeInput(plainText);
    expect(result).toBe(plainText);
  });

  it('should handle empty strings', () => {
    expect(sanitizeInput('')).toBe('');
  });

  it('should handle null and undefined', () => {
    expect(sanitizeInput(null)).toBe('');
    expect(sanitizeInput(undefined)).toBe('');
  });

  it('should handle special characters', () => {
    const specialChars = '!@#$%^&*()_+-=[]{}|;:,.<>?';
    const result = sanitizeInput(specialChars);
    expect(result).toContain(specialChars);
  });
});

describe('HTML Sanitization', () => {
  it('should allow safe HTML tags', () => {
    const safeHTML = '<p>Paragraph</p><strong>Bold</strong><em>Italic</em>';
    const result = sanitizeHTML(safeHTML);
    expect(result).toContain('<p>');
    expect(result).toContain('<strong>');
    expect(result).toContain('<em>');
  });

  it('should remove dangerous tags while keeping safe content', () => {
    const dangerous = '<script>alert("XSS")</script><p>Safe content</p>';
    const result = sanitizeHTML(dangerous);
    expect(result).not.toContain('<script>');
    expect(result).toContain('<p>');
    expect(result).toContain('Safe content');
  });

  it('should remove dangerous attributes', () => {
    const dangerous = '<a href="javascript:alert(\'XSS\')">Link</a>';
    const result = sanitizeHTML(dangerous);
    expect(result).not.toContain('javascript:');
  });

  it('should allow safe attributes', () => {
    const safeHTML = '<a href="https://example.com" title="Example">Link</a>';
    const result = sanitizeHTML(safeHTML);
    expect(result).toContain('href="https://example.com"');
    expect(result).toContain('title="Example"');
  });

  it('should remove event handlers from allowed tags', () => {
    const dangerous = '<p onclick="alert(\'XSS\')">Text</p>';
    const result = sanitizeHTML(dangerous);
    expect(result).not.toContain('onclick');
    expect(result).toContain('<p>');
  });
});

describe('Object Sanitization', () => {
  it('should sanitize all string values in an object', () => {
    const obj = {
      name: '<script>alert("XSS")</script>John',
      email: 'john@example.com',
      bio: '<div>Safe text</div>'
    };
    const result = sanitizeObject(obj);
    expect(result.name).toBe('John');
    expect(result.email).toBe('john@example.com');
    expect(result.bio).toBe('Safe text');
  });

  it('should handle nested objects', () => {
    const obj = {
      user: {
        name: '<script>XSS</script>Jane',
        profile: {
          bio: '<b>Developer</b>'
        }
      }
    };
    const result = sanitizeObject(obj);
    expect(result.user.name).toBe('Jane');
    expect(result.user.profile.bio).toBe('Developer');
  });

  it('should handle arrays within objects', () => {
    const obj = {
      tags: ['<script>alert()</script>tag1', 'tag2', '<b>tag3</b>'],
      count: 3
    };
    const result = sanitizeObject(obj);
    expect(result.tags[0]).toBe('tag1');
    expect(result.tags[1]).toBe('tag2');
    expect(result.tags[2]).toBe('tag3');
    expect(result.count).toBe(3);
  });

  it('should preserve non-string values', () => {
    const obj = {
      name: '<script>Test</script>User',
      age: 25,
      active: true,
      score: 99.5,
      nothing: null,
      missing: undefined
    };
    const result = sanitizeObject(obj);
    expect(result.name).toBe('User');
    expect(result.age).toBe(25);
    expect(result.active).toBe(true);
    expect(result.score).toBe(99.5);
    expect(result.nothing).toBeNull();
    expect(result.missing).toBeUndefined();
  });

  it('should handle empty objects', () => {
    const result = sanitizeObject({});
    expect(result).toEqual({});
  });

  it('should handle null and undefined', () => {
    expect(sanitizeObject(null)).toBeNull();
    expect(sanitizeObject(undefined)).toBeUndefined();
  });
});

describe('Email Sanitization', () => {
  it('should trim and lowercase email addresses', () => {
    const email = '  John@Example.COM  ';
    const result = sanitizeEmail(email);
    expect(result).toBe('john@example.com');
  });

  it('should remove HTML tags from emails', () => {
    const malicious = '<script>alert()</script>user@example.com';
    const result = sanitizeEmail(malicious);
    expect(result).toBe('user@example.com');
    expect(result).not.toContain('<script>');
  });

  it('should handle valid emails without changes', () => {
    const email = 'user@example.com';
    const result = sanitizeEmail(email);
    expect(result).toBe(email);
  });

  it('should handle empty strings', () => {
    expect(sanitizeEmail('')).toBe('');
  });

  it('should handle null and undefined', () => {
    expect(sanitizeEmail(null)).toBe('');
    expect(sanitizeEmail(undefined)).toBe('');
  });
});

describe('Secure LocalStorage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should sanitize data before storing', () => {
    const data = {
      name: '<script>XSS</script>John',
      email: 'john@example.com'
    };
    setSecureLocalStorage('user', data);
    const stored = localStorage.getItem('user');
    const parsed = JSON.parse(stored);
    expect(parsed.name).toBe('John');
    expect(parsed.email).toBe('john@example.com');
  });

  it('should retrieve and sanitize data from localStorage', () => {
    const data = { name: 'John', role: 'admin' };
    localStorage.setItem('user', JSON.stringify(data));
    const result = getSecureLocalStorage('user');
    expect(result).toEqual(data);
  });

  it('should return default value when key does not exist', () => {
    const defaultValue = { name: 'Guest' };
    const result = getSecureLocalStorage('nonexistent', defaultValue);
    expect(result).toEqual(defaultValue);
  });

  it('should return null when key does not exist and no default provided', () => {
    const result = getSecureLocalStorage('nonexistent');
    expect(result).toBeNull();
  });

  it('should handle malformed JSON gracefully', () => {
    localStorage.setItem('bad', 'not valid json {]');
    const result = getSecureLocalStorage('bad', { fallback: true });
    expect(result).toEqual({ fallback: true });
  });

  it('should handle null and undefined values', () => {
    setSecureLocalStorage('nullValue', null);
    expect(getSecureLocalStorage('nullValue')).toBeNull();

    setSecureLocalStorage('undefinedValue', undefined);
    const result = getSecureLocalStorage('undefinedValue');
    expect(result).toBeDefined(); // Will be null or empty string
  });

  it('should sanitize nested objects before storage', () => {
    const data = {
      user: {
        name: '<b>Admin</b>',
        settings: {
          theme: '<script>dark</script>'
        }
      }
    };
    setSecureLocalStorage('config', data);
    const result = getSecureLocalStorage('config');
    expect(result.user.name).toBe('Admin');
    expect(result.user.settings.theme).toBe('dark');
  });
});

describe('XSS Attack Prevention', () => {
  const xssVectors = [
    '<script>alert("XSS")</script>',
    '<img src=x onerror=alert("XSS")>',
    '<svg/onload=alert("XSS")>',
    'javascript:alert("XSS")',
    '<iframe src="javascript:alert(\'XSS\')">',
    '<body onload=alert("XSS")>',
    '<input onfocus=alert("XSS") autofocus>',
    '<select onfocus=alert("XSS") autofocus>',
    '<textarea onfocus=alert("XSS") autofocus>',
    '<object data="data:text/html,<script>alert(\'XSS\')</script>">',
    '<embed src="data:text/html,<script>alert(\'XSS\')</script>">'
  ];

  xssVectors.forEach((vector, index) => {
    it(`should prevent XSS attack vector ${index + 1}`, () => {
      const result = sanitizeInput(vector);
      expect(result).not.toContain('<script>');
      expect(result).not.toContain('javascript:');
      expect(result).not.toContain('onerror');
      expect(result).not.toContain('onload');
      expect(result).not.toContain('onfocus');
    });
  });

  it('should sanitize XSS in object properties', () => {
    const maliciousObject = {
      title: '<script>alert("XSS")</script>',
      description: '<img src=x onerror=alert("XSS")>',
      content: '<svg/onload=alert("XSS")>'
    };
    const result = sanitizeObject(maliciousObject);
    Object.values(result).forEach(value => {
      if (typeof value === 'string') {
        expect(value).not.toContain('<script>');
        expect(value).not.toContain('onerror');
        expect(value).not.toContain('onload');
      }
    });
  });
});

describe('Performance and Edge Cases', () => {
  it('should handle very long strings efficiently', () => {
    const longString = 'a'.repeat(100000);
    const start = Date.now();
    const result = sanitizeInput(longString);
    const duration = Date.now() - start;
    expect(result).toBe(longString);
    expect(duration).toBeLessThan(1000); // Should complete in less than 1 second
  });

  it('should handle deeply nested objects', () => {
    let nested = { value: '<script>XSS</script>Test' };
    for (let i = 0; i < 10; i++) {
      nested = { child: nested };
    }
    const result = sanitizeObject(nested);
    // Navigate to deepest level
    let current = result;
    for (let i = 0; i < 10; i++) {
      current = current.child;
    }
    expect(current.value).toBe('Test');
  });

  it('should handle circular references gracefully', () => {
    const obj = { name: '<b>Test</b>' };
    obj.self = obj; // Circular reference
    // This should not throw an error or cause infinite loop
    expect(() => sanitizeObject(obj)).not.toThrow();
  });
});
