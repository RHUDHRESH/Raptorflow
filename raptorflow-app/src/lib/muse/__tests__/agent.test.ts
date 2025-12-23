import { describe, it, expect, vi } from 'vitest';

vi.mock('pg', () => {
  return {
    Pool: vi.fn(() => ({
      connect: vi.fn(),
      query: vi.fn(),
    })),
  };
});

vi.mock('../vertexai', () => ({
    gemini2Flash: {
        bindTools: vi.fn(() => ({
            invoke: vi.fn(),
        })),
    }
}));

vi.mock('@langchain/google-vertexai', () => ({
    ChatVertexAI: class {},
    GoogleVertexAIEmbeddings: class {
        constructor() {}
        embedQuery() { return Promise.resolve([]); }
    },
}));

import { createMuseGraph } from '../agent';

describe('Muse Agent Graph', () => {
    it('should compile the graph', () => {
        const graphInstance = createMuseGraph();
        expect(graphInstance).toBeDefined();
        // Check if it has invoke method (Runnable)
        expect(typeof graphInstance.invoke).toBe('function');
    });
});
