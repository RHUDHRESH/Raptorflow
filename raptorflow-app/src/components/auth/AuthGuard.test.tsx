import { render, screen } from '@testing-library/react';
import { AuthGuard } from './AuthGuard';
import { supabase } from '@/lib/supabase';
import { vi, describe, it, expect, beforeEach } from 'vitest';

vi.mock('@/lib/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn(),
      onAuthStateChange: vi.fn(() => ({
        data: { subscription: { unsubscribe: vi.fn() } },
      })),
    },
  },
}));

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

describe('AuthGuard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders children when authenticated', async () => {
    (supabase.auth.getSession as any).mockResolvedValue({
      data: { session: { user: { id: 'test-user' } } },
      error: null,
    });

    render(
      <AuthGuard>
        <div data-testid="protected-content">Protected</div>
      </AuthGuard>
    );

    // Should show children after session check
    const content = await screen.findByTestId('protected-content');
    expect(content).toBeDefined();
  });

  it('redirects or shows loading when NOT authenticated', async () => {
    (supabase.auth.getSession as any).mockResolvedValue({
      data: { session: null },
      error: null,
    });

    render(
      <AuthGuard>
        <div data-testid="protected-content">Protected</div>
      </AuthGuard>
    );

    // Protected content should NOT be rendered
    const content = screen.queryByTestId('protected-content');
    expect(content).toBeNull();
  });
});
