import { afterEach, beforeEach, vi } from 'vitest';
import './mocks';

// Global test setup
beforeEach(() => {
  // Reset all mocks before each test
  vi.clearAllMocks();
  
  // Set test environment
  process.env.NODE_ENV = 'test';
  process.env.PORT = '3001';
  process.env.FRONTEND_PUBLIC_URL = 'http://localhost:5173';
  
  // Mock environment variables for testing
  process.env.SUPABASE_URL = 'https://test.supabase.co';
  process.env.SUPABASE_SERVICE_ROLE_KEY = 'test-service-key';
  process.env.SUPABASE_ANON_KEY = 'test-anon-key';
  process.env.GOOGLE_CLOUD_PROJECT_ID = 'test-project';
});

afterEach(() => {
  // Clean up after each test
  vi.resetAllMocks();
});

// Global teardown
afterAll(() => {
  vi.restoreAllMocks();
});



