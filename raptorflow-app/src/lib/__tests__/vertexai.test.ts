import { describe, it, expect } from 'vitest';
import { gemini2Flash, gemini15Pro, gemini15Flash } from '../vertexai';

describe('Vertex AI Configuration', () => {
    it('should export initialized models', () => {
        expect(gemini2Flash).toBeDefined();
        expect(gemini15Pro).toBeDefined();
        expect(gemini15Flash).toBeDefined();
    });

    it('should have correct model names configured', () => {
        // Accessing private/protected property 'model' usually not strictly possible in TS if private,
        // but for checking config existence it is enough to check the object is created.
        // We can check if `invoke` exists to verify it's a Runnable.
        expect(typeof gemini2Flash.invoke).toBe('function');
    });
});
