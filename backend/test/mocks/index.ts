import { vi } from 'vitest';

// Mock Supabase client
const mockSupabaseClient = {
  auth: {
    getUser: vi.fn().mockResolvedValue({ 
      data: { user: { id: 'test-user-id', email: 'test@example.com' } }, 
      error: null 
    }),
  },
  from: vi.fn().mockReturnThis(),
  select: vi.fn().mockReturnThis(),
  insert: vi.fn().mockReturnThis(),
  update: vi.fn().mockReturnThis(),
  eq: vi.fn().mockReturnThis(),
  single: vi.fn().mockResolvedValue({ data: null, error: null }),
};

vi.mock('@supabase/supabase-js', () => ({
  createClient: vi.fn().mockReturnValue(mockSupabaseClient),
}));

// Mock Vertex AI
const mockVertexAI = {
  getGenerativeModel: vi.fn().mockReturnValue({
    generateContent: vi.fn().mockResolvedValue({
      response: {
        text: vi.fn().mockReturnValue('Mock AI response'),
      },
    }),
  }),
};

vi.mock('@google-cloud/vertexai', () => ({
  VertexAI: vi.fn().mockImplementation(() => mockVertexAI),
}));

// Mock LangChain
vi.mock('@langchain/google-vertexai', () => ({
  ChatVertexAI: vi.fn().mockImplementation(() => ({
    invoke: vi.fn().mockResolvedValue('Mock LangChain response'),
    pipe: vi.fn().mockReturnThis(),
  })),
}));

// Mock external HTTP requests
vi.mock('node-fetch', () => ({
  default: vi.fn().mockResolvedValue({
    json: vi.fn().mockResolvedValue({ success: true }),
    status: 200,
    ok: true,
  }),
}));

// Mock crypto for payment testing
vi.mock('crypto', () => ({
  createHash: vi.fn().mockReturnValue({
    update: vi.fn().mockReturnThis(),
    digest: vi.fn().mockReturnValue('mock-hash'),
  }),
  randomBytes: vi.fn().mockReturnValue(Buffer.from('mock-random')),
}));

// Mock console for cleaner test output
const originalConsole = { ...console };

beforeEach(() => {
  console.log = vi.fn();
  console.error = vi.fn();
  console.warn = vi.fn();
  console.info = vi.fn();
});

afterAll(() => {
  console.log = originalConsole.log;
  console.error = originalConsole.error;
  console.warn = originalConsole.warn;
  console.info = originalConsole.info;
});

// Export mocks for use in tests
export { mockSupabaseClient, mockVertexAI };



