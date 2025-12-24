import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

describe('Vertex AI Configuration', () => {
    const originalEnv = process.env;

    beforeEach(() => {
        vi.resetModules();
        process.env = { ...originalEnv };
    });

    afterEach(() => {
        process.env = originalEnv;
    });

    it('returns null when no API key is configured', async () => {
        delete process.env.INFERENCE_SIMPLE;
        delete process.env.VERTEX_AI_API_KEY;
        delete process.env.NEXT_PUBLIC_INFERENCE_SIMPLE;
        delete process.env.NEXT_PUBLIC_VERTEX_AI_API_KEY;
        delete process.env.GOOGLE_APPLICATION_CREDENTIALS;
        delete process.env.GOOGLE_CLOUD_PROJECT;
        delete process.env.VERTEX_AI_USE_ADC;
        delete process.env.NEXT_PUBLIC_VERTEX_AI_USE_ADC;

        const { getGemini2Flash, getGemini15Pro, getGemini15Flash } = await import('../vertexai');
        expect(getGemini2Flash()).toBeNull();
        expect(getGemini15Pro()).toBeNull();
        expect(getGemini15Flash()).toBeNull();
    });

    it('returns model instances when API key is configured', async () => {
        process.env.VERTEX_AI_API_KEY = 'test-key';

        const { getGemini2Flash, getGemini15Pro, getGemini15Flash } = await import('../vertexai');
        expect(getGemini2Flash()).not.toBeNull();
        expect(getGemini15Pro()).not.toBeNull();
        expect(getGemini15Flash()).not.toBeNull();
    });
});
