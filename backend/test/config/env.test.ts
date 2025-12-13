import { describe, it, expect, beforeEach, vi } from 'vitest';
import { env, parseEnv } from '../../src/config/env';

describe('Environment Configuration', () => {
  beforeEach(() => {
    // Clear process.env for each test
    Object.keys(process.env).forEach(key => {
      if (key.startsWith('TEST_')) {
        delete process.env[key];
      }
    });
    
    // Reset modules to get fresh env import
    vi.resetModules();
  });

  it('should load default values when no env vars are set', () => {
    const config = parseEnv();
    
    expect(config.NODE_ENV).toBe('test');
    expect(config.PORT).toBe(3001);
    expect(config.FRONTEND_PUBLIC_URL).toBe('http://localhost:5173');
    expect(config.GOOGLE_CLOUD_LOCATION).toBe('us-central1');
  });

  it('should validate required production variables', () => {
    process.env.NODE_ENV = 'production';
    
    expect(() => parseEnv()).toThrow('Production environment configuration incomplete');
  });

  it('should accept valid production configuration', () => {
    process.env.NODE_ENV = 'production';
    process.env.SUPABASE_SERVICE_ROLE_KEY = 'valid-key';
    process.env.GOOGLE_CLOUD_PROJECT_ID = 'test-project';
    process.env.FRONTEND_PUBLIC_URL = 'https://app.raptorflow.in';
    process.env.BACKEND_PUBLIC_URL = 'https://api.raptorflow.in';
    
    const config = parseEnv();
    
    expect(config.NODE_ENV).toBe('production');
    expect(config.SUPABASE_SERVICE_ROLE_KEY).toBe('valid-key');
    expect(config.GOOGLE_CLOUD_PROJECT_ID).toBe('test-project');
  });

  it('should validate URL formats', () => {
    process.env.FRONTEND_PUBLIC_URL = 'invalid-url';
    
    expect(() => parseEnv()).toThrow('Validation failed');
  });

  it('should handle alternative env var names', () => {
    process.env.VITE_SUPABASE_URL = 'https://alt.supabase.co';
    process.env.VITE_GOOGLE_CLOUD_PROJECT_ID = 'alt-project';
    
    const config = parseEnv();
    
    expect(config.SUPABASE_URL).toBe('https://alt.supabase.co');
    expect(config.GOOGLE_CLOUD_PROJECT_ID).toBe('alt-project');
  });

  it('should validate PhonePe environment values', () => {
    process.env.PHONEPE_ENV = 'INVALID';
    
    expect(() => parseEnv()).toThrow('Validation failed');
  });
});



