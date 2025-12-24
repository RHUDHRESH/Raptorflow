import { describe, it, expect } from 'vitest';

describe('Environment Integrity Audit', () => {
    it('has required Supabase public variables', () => {
        expect(process.env.NEXT_PUBLIC_SUPABASE_URL, 'NEXT_PUBLIC_SUPABASE_URL is missing').toBeDefined();
        expect(process.env.NEXT_PUBLIC_SUPABASE_URL).not.toBe('');
        expect(process.env.NEXT_PUBLIC_SUPABASE_URL).not.toContain('dummy');

        expect(process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY, 'NEXT_PUBLIC_SUPABASE_ANON_KEY is missing').toBeDefined();
        expect(process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY).not.toBe('');
        expect(process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY).not.toContain('dummy');
    });

    it('has required API variables', () => {
        expect(process.env.NEXT_PUBLIC_API_URL, 'NEXT_PUBLIC_API_URL is missing').toBeDefined();
        expect(process.env.NEXT_PUBLIC_API_URL).not.toBe('');
    });

    it('has required GCP variables', () => {
        expect(process.env.NEXT_PUBLIC_GCP_PROJECT_ID, 'NEXT_PUBLIC_GCP_PROJECT_ID is missing').toBeDefined();
        expect(process.env.NEXT_PUBLIC_GCP_PROJECT_ID).not.toBe('');
        expect(process.env.NEXT_PUBLIC_GCP_PROJECT_ID).not.toContain('your-project-id');
    });
});
