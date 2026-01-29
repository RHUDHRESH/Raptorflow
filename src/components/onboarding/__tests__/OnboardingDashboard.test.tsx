import '@testing-library/jest-dom/vitest';
import { render } from '@testing-library/react';
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { OnboardingDashboard } from '../OnboardingDashboard';

const respond = (payload: unknown) =>
  new Response(JSON.stringify(payload), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });

const metricsPayload = {
  totalSessions: 1,
  activeSessions: 1,
  completedSessions: 0,
  averageCompletionTime: 2,
  averageCompletionPercentage: 50,
  sessionsThisWeek: 1,
  completionRate: 10,
};

const sessionsPayload = {
  sessions: [
    {
      sessionId: 'session-1',
      workspaceId: 'workspace-1',
      clientName: 'TechCorp Solutions',
      completionPercentage: 85,
      currentPhase: 5,
      lastActivity: '2026-01-27T12:00:00Z',
      status: 'active' as const,
      startedAt: '2026-01-20T10:00:00Z',
    },
  ],
};

const manifestPayload = {
  success: true,
  version: '2.0',
  checksum: 'abc123def',
  retrieved_at: '2026-01-27T10:00:00Z',
};

describe('OnboardingDashboard', () => {
  let originalFetch: typeof fetch;
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    originalFetch = globalThis.fetch;
    fetchMock = vi.fn();
    fetchMock.mockImplementation(async (input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/dashboard/metrics')) return respond(metricsPayload);
      if (url.includes('/dashboard/sessions')) return respond(sessionsPayload);
      if (url.includes('/context/manifest')) return respond(manifestPayload);
      return respond({});
    });
    (globalThis as any).fetch = fetchMock;
  });

  afterEach(() => {
    (globalThis as any).fetch = originalFetch;
    vi.restoreAllMocks();
  });

  it('shows loading indicator while requests are pending', () => {
    fetchMock.mockImplementation(
      () =>
        new Promise(() => {
          /* pending */
        })
    );

    const { getByText } = render(<OnboardingDashboard />);
    expect(getByText('Loading dashboard...')).toBeInTheDocument();
  });

  it('renders header and metrics once data loads', async () => {
    const { findByText, getByText } = render(<OnboardingDashboard />);

    await findByText('Onboarding Dashboard');
    expect(getByText('Active Sessions')).toBeInTheDocument();
    expect(getByText('TechCorp Solutions')).toBeInTheDocument();
  });

  it('shows Business Context card when manifest exists', async () => {
    const { findByText } = render(<OnboardingDashboard />);

    expect(await findByText('Business Context')).toBeInTheDocument();
    expect(await findByText('Version')).toBeInTheDocument();
  });
});
