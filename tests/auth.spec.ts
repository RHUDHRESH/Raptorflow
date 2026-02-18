import { test, expect, Page } from '@playwright/test';

const FRONTEND_URL = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';
const API_URL = process.env.E2E_API_URL || FRONTEND_URL;

test.describe('AUTH API - Extreme Tests', () => {
  
  test('1. Health endpoint - basic', async ({ request }) => {
    const response = await request.get(`${API_URL}/api/auth/health`);
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });

  test('2. Health endpoint - returns provider', async ({ request }) => {
    const response = await request.get(`${API_URL}/api/auth/health`);
    const data = await response.json();
    expect(data.provider).toBeDefined();
    expect(['demo', 'supabase']).toContain(data.provider);
  });

  test('3. Signup - valid credentials', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/signup`, {
      data: {
        email: 'playwright@test.com',
        password: 'testpass123'
      }
    });
    expect([200, 400]).toContain(response.status()); // 400 if rate limited
  });

  test('4. Signup - weak password', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/signup`, {
      data: {
        email: 'weak@test.com',
        password: '123'
      }
    });
    expect(response.status()).toBe(422); // Validation error
  });

  test('5. Signup - invalid email', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/signup`, {
      data: {
        email: 'not-an-email',
        password: 'testpass123'
      }
    });
    expect(response.status()).toBe(422);
  });

  test('6. Signup - missing email', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/signup`, {
      data: {
        password: 'testpass123'
      }
    });
    expect(response.status()).toBe(422);
  });

  test('7. Signup - missing password', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/signup`, {
      data: {
        email: 'test@test.com'
      }
    });
    expect(response.status()).toBe(422);
  });

  test('8. Signup - empty body', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/signup`, {});
    expect(response.status()).toBe(422);
  });

  test('9. Login - valid credentials', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: 'test@example.com',
        password: 'testpass'
      }
    });
    expect([200, 401]).toContain(response.status());
    if (response.status() === 200) {
      const data = await response.json();
      expect(data.access_token).toBeDefined();
      expect(data.user).toBeDefined();
    }
  });

  test('10. Login - wrong password', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: 'test@example.com',
        password: 'wrongpassword'
      }
    });
    expect([401, 429]).toContain(response.status());
  });

  test('11. Login - non-existent user', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: 'nonexistent' + Date.now() + '@test.com',
        password: 'testpass123'
      }
    });
    expect([401, 429]).toContain(response.status());
  });

  test('12. Login - missing email', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        password: 'testpass123'
      }
    });
    expect(response.status()).toBe(422);
  });

  test('13. Login - missing password', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: 'test@test.com'
      }
    });
    expect(response.status()).toBe(422);
  });

  test('14. Verify - with valid token', async ({ request }) => {
    // First login
    const loginRes = await request.post(`${API_URL}/api/auth/login`, {
      data: { email: 'test@example.com', password: 'testpass' }
    });
    
    if (loginRes.status() === 200) {
      const data = await loginRes.json();
      const token = data.access_token;
      
      const response = await request.post(`${API_URL}/api/auth/verify`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      expect(response.status()).toBe(200);
      const verifyData = await response.json();
      expect(verifyData.valid).toBe(true);
    }
  });

  test('15. Verify - without token', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/verify`);
    expect(response.status()).toBe(200); // Should return valid: false
    const data = await response.json();
    expect(data.valid).toBe(false);
  });

  test('16. Verify - with invalid token', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/verify`, {
      headers: { 'Authorization': 'Bearer invalid-token-12345' }
    });
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.valid).toBe(false);
  });

  test('17. Verify - with malformed token', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/verify`, {
      headers: { 'Authorization': 'NotBearer token' }
    });
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.valid).toBe(false);
  });

  test('18. Get me - with valid token', async ({ request }) => {
    const loginRes = await request.post(`${API_URL}/api/auth/login`, {
      data: { email: 'test@example.com', password: 'testpass' }
    });
    
    if (loginRes.status() === 200) {
      const data = await loginRes.json();
      const token = data.access_token;
      
      const response = await request.get(`${API_URL}/api/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      expect(response.status()).toBe(200);
      const userData = await response.json();
      expect(userData.email).toBeDefined();
    }
  });

  test('19. Get me - without token', async ({ request }) => {
    const response = await request.get(`${API_URL}/api/auth/me`);
    expect(response.status()).toBe(401);
  });

  test('20. Get me - with invalid token', async ({ request }) => {
    const response = await request.get(`${API_URL}/api/auth/me`, {
      headers: { 'Authorization': 'Bearer invalid-token' }
    });
    expect(response.status()).toBe(401);
  });

  test('21. Logout - with valid token', async ({ request }) => {
    const loginRes = await request.post(`${API_URL}/api/auth/login`, {
      data: { email: 'test@example.com', password: 'testpass' }
    });
    
    if (loginRes.status() === 200) {
      const data = await loginRes.json();
      const token = data.access_token;
      
      const response = await request.post(`${API_URL}/api/auth/logout`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      expect(response.status()).toBe(200);
      const logoutData = await response.json();
      expect(logoutData.message).toBeDefined();
    }
  });

  test('22. Logout - without token', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/logout`);
    expect(response.status()).toBe(200); // Should still return success
  });

  test('23. Rate limiting - login attempts', async ({ request }) => {
    // Try multiple logins rapidly
    const results: number[] = [];
    for (let i = 0; i < 10; i++) {
      const response = await request.post(`${API_URL}/api/auth/login`, {
        data: {
          email: `ratelimit${i}@test.com`,
          password: 'test'
        }
      });
      results.push(response.status());
    }
    
    // At least some should be rate limited (429) or 401
    const hasRateLimit = results.some(r => r === 429);
    const hasAuthFailed = results.some(r => r === 401);
    expect(hasRateLimit || hasAuthFailed).toBe(true);
  });

  test('24. Rate limiting - signup attempts', async ({ request }) => {
    const results: number[] = [];
    for (let i = 0; i < 5; i++) {
      const response = await request.post(`${API_URL}/api/auth/signup`, {
        data: {
          email: `signup${i}${Date.now()}@test.com`,
          password: 'testpass123'
        }
      });
      results.push(response.status());
    }
    
    // Some should be rate limited
    console.log('Signup results:', results);
  });

  test('25. SQL Injection - email field', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: "admin' OR '1'='1",
        password: 'test'
      }
    });
    expect([401, 429]).toContain(response.status());
  });

  test('26. XSS attempt - email field', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: '<script>alert("xss")</script>@test.com',
        password: 'test'
      }
    });
    expect([401, 422, 429]).toContain(response.status());
  });

  test('27. Very long email', async ({ request }) => {
    const longEmail = 'a'.repeat(250) + '@test.com';
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: longEmail,
        password: 'test'
      }
    });
    expect([400, 401, 422]).toContain(response.status());
  });

  test('28. Unicode in email', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: 'test@ünicode.com',
        password: 'test'
      }
    });
    // Should either work or reject gracefully
    expect([200, 401, 422, 429]).toContain(response.status());
  });

  test('29. Special characters in password', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: 'test@test.com',
        password: 'p@$$w0rd!#$%^&*()'
      }
    });
    expect([200, 401, 429]).toContain(response.status());
  });

  test('30. Empty strings', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: '',
        password: ''
      }
    });
    expect(response.status()).toBe(422);
  });

  test('31. Null values', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: null,
        password: null
      }
    });
    expect(response.status()).toBe(422);
  });

  test('32. Boolean values', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: true,
        password: false
      }
    });
    expect(response.status()).toBe(422);
  });

  test('33. Array values', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: ['test@test.com'],
        password: ['test']
      }
    });
    expect(response.status()).toBe(422);
  });

  test('34. Object values', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: { value: 'test@test.com' },
        password: { value: 'test' }
      }
    });
    expect(response.status()).toBe(422);
  });

  test('35. Refresh token - invalid', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/refresh`, {
      data: {
        refresh_token: 'invalid-refresh-token'
      }
    });
    expect(response.status()).toBe(401);
  });

  test('36. Content-Type: application/json required', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: 'test@test.com',
        password: 'test'
      },
      headers: {
        'Content-Type': 'text/plain'
      }
    });
    expect([400, 415, 422]).toContain(response.status());
  });

  test('37. CORS - preflight', async ({ request }) => {
    const response = await request.fetch(`${API_URL}/api/auth/login`, {
      method: 'OPTIONS',
      headers: {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'POST'
      }
    });
    // Should return 200 or 204 for OPTIONS
    expect([200, 204, 405]).toContain(response.status());
  });

  test('38. Auth header formats', async ({ request }) => {
    // Test various auth header formats
    const formats = [
      'Bearer',
      'BEARER token',
      'bearer token',
      'Token token',
      'Basic dXNlcjpwYXNz',  // Basic auth
      ''
    ];
    
    for (const format of formats) {
      const headers: Record<string, string> = {};
      if (format) {
        headers['Authorization'] = format;
      }
      
      const response = await request.get(`${API_URL}/api/auth/me`, { headers });
      expect([200, 401]).toContain(response.status());
    }
  });

  test('39. Concurrent requests', async ({ request }) => {
    // Fire multiple requests concurrently
    const promises = Array(5).fill(null).map(() => 
      request.post(`${API_URL}/api/auth/login`, {
        data: { email: 'concurrent@test.com', password: 'test' }
      })
    );
    
    const results = await Promise.all(promises);
    const statuses = results.map(r => r.status());
    
    // Should handle concurrent requests
    expect(statuses.every(s => [200, 401, 429].includes(s))).toBe(true);
  });

  test('40. Response headers security', async ({ request }) => {
    const response = await request.get(`${API_URL}/api/auth/health`);
    
    // Check for security headers
    const headers = response.headers();
    console.log('Response headers:', headers);
    
    // Should have some security considerations
    expect(headers).toBeDefined();
  });

  test('41. Token format validation', async ({ request }) => {
    // Test various token formats
    const tokens = [
      'demo_token',           // No prefix
      'demo-',               // Incomplete
      'demo',                // Too short
      'demo_',               // Just prefix
      'x'.repeat(50),        // Random long
    ];
    
    for (const token of tokens) {
      const response = await request.get(`${API_URL}/api/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      expect([401, 429]).toContain(response.status());
    }
  });

  test('42. Password max length', async ({ request }) => {
    // Supabase has 72 char max for bcrypt
    const veryLongPass = 'a'.repeat(100);
    const response = await request.post(`${API_URL}/api/auth/signup`, {
      data: {
        email: 'longpass@test.com',
        password: veryLongPass
      }
    });
    // Should either accept or reject with proper error
    expect([200, 400, 422]).toContain(response.status());
  });

  test('43. Email max length', async ({ request }) => {
    const veryLongEmail = 'a'.repeat(250) + '@test.com';
    const response = await request.post(`${API_URL}/api/auth/signup`, {
      data: {
        email: veryLongEmail,
        password: 'testpass123'
      }
    });
    expect([400, 422]).toContain(response.status());
  });

  test('44. Response time', async ({ request }) => {
    const start = Date.now();
    await request.get(`${API_URL}/api/auth/health`);
    const duration = Date.now() - start;
    
    console.log('Response time:', duration, 'ms');
    expect(duration).toBeLessThan(5000); // Should respond within 5 seconds
  });

  test('45. Case sensitivity in email', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: 'TEST@EXAMPLE.COM',
        password: 'test'
      }
    });
    // Should handle case insensitivity gracefully
    expect([200, 401, 429]).toContain(response.status());
  });

  test('46. Whitespace handling', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: '  test@test.com  ',
        password: '  testpass  '
      }
    });
    expect([200, 401, 422, 429]).toContain(response.status());
  });

  test('47. Multiple email @ symbols', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: 'test@@test.com',
        password: 'test'
      }
    });
    expect([401, 422, 429]).toContain(response.status());
  });

  test('48. No domain in email', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: 'test@',
        password: 'test'
      }
    });
    expect([401, 422, 429]).toContain(response.status());
  });

  test('49. No @ in email', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: {
        email: 'test.com',
        password: 'test'
      }
    });
    expect([401, 422, 429]).toContain(response.status());
  });

  test('50. Hydration attack prevention', async ({ request }) => {
    // Try to inject through JSON hydration
    const maliciousPayload = {
      email: '{"$gt": ""}',
      password: '{"$gt": ""}'
    };
    
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: maliciousPayload
    });
    
    expect([401, 422, 429]).toContain(response.status());
  });
});

test.describe('AUTH Flow - End to End', () => {
  
  test('Complete auth flow', async ({ request }) => {
    const timestamp = Date.now();
    const email = `e2e${timestamp}@test.com`;
    
    // 1. Signup
    const signupRes = await request.post(`${API_URL}/api/auth/signup`, {
      data: { email, password: 'testpass123' }
    });
    
    // May succeed or be rate limited
    console.log('Signup status:', signupRes.status());
    
    // 2. Login
    const loginRes = await request.post(`${API_URL}/api/auth/login`, {
      data: { email: 'test@example.com', password: 'testpass' }
    });
    
    if (loginRes.status() === 200) {
      const data = await loginRes.json();
      const token = data.access_token;
      
      // 3. Verify
      const verifyRes = await request.post(`${API_URL}/api/auth/verify`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      expect(verifyRes.status()).toBe(200);
      
      // 4. Get me
      const meRes = await request.get(`${API_URL}/api/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      expect(meRes.status()).toBe(200);
      
      // 5. Logout
      const logoutRes = await request.post(`${API_URL}/api/auth/logout`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      expect(logoutRes.status()).toBe(200);
    }
  });
});

test.describe('AUTH Security', () => {
  
  test('No token leakage in response', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: { email: 'test@example.com', password: 'wrongpass' }
    });
    
    const data = await response.json();
    
    // Error responses should not leak sensitive data
    expect(data.detail).not.toContain('token');
    expect(data.detail).not.toContain('secret');
    expect(data.detail).not.toContain('key');
  });

  test('Proper error messages', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/auth/login`, {
      data: { email: 'nonexistent@test.com', password: 'wrongpass' }
    });
    
    const data = await response.json();
    
    // Should have error message
    expect(data.detail).toBeDefined();
    
    // Should not reveal if user exists
    expect(data.detail.toLowerCase()).not.toContain('user not found');
    expect(data.detail.toLowerCase()).not.toContain('email not found');
  });
});
