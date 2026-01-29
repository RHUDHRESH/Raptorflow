import '@testing-library/jest-dom/vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, beforeEach, afterEach, vi, expect } from 'vitest';
import { ProfileGate } from '../ProfileGate';

let currentPathname = '/dashboard';
const replaceMock = vi.fn();
const pushMock = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    replace: replaceMock,
    push: pushMock,
  }),
  usePathname: () => currentPathname,
}));

const defaultProfileStatus = {
  workspaceId: 'ws-1',
  subscriptionPlan: 'growth',
  subscriptionStatus: 'active',
  needsPayment: false,
  profileExists: true,
  workspaceExists: true,
  isReady: true,
};

const authState = {
  isAuthenticated: true,
  isLoading: false,
  profileStatus: defaultProfileStatus,
  isCheckingProfile: false,
};

vi.mock('@/components/auth/AuthProvider', () => ({
  useAuth: () => authState,
}));

describe('ProfileGate', () => {
  beforeEach(() => {
    currentPathname = '/dashboard';
    replaceMock.mockReset();
    pushMock.mockReset();
    authState.isAuthenticated = true;
    authState.isLoading = false;
    authState.isCheckingProfile = false;
    authState.profileStatus = { ...defaultProfileStatus };
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders children for public paths when unauthenticated', () => {
    currentPathname = '/signin';
    authState.isAuthenticated = false;

    render(
      <ProfileGate>
        <div>public-content</div>
      </ProfileGate>
    );

    expect(screen.getByText('public-content')).toBeInTheDocument();
    expect(replaceMock).not.toHaveBeenCalled();
  });

  it('shows loader while profile verification is running', () => {
    authState.isAuthenticated = true;
    authState.isCheckingProfile = true;
    authState.profileStatus = { ...defaultProfileStatus, isReady: false };

    render(
      <ProfileGate>
        <div>dashboard</div>
      </ProfileGate>
    );

    expect(
      screen.getByText('VERIFYING WORKSPACE & PAYMENT STATUS…')
    ).toBeInTheDocument();
  });

  it('redirects to onboarding when profile is missing', async () => {
    authState.profileStatus = {
      ...defaultProfileStatus,
      profileExists: false,
      workspaceExists: false,
      isReady: false,
    };

    render(
      <ProfileGate>
        <div>should-not-render</div>
      </ProfileGate>
    );

    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith('/onboarding/start');
    });
  });

  it('redirects to plans when payment is required', async () => {
    authState.profileStatus = {
      ...defaultProfileStatus,
      needsPayment: true,
      isReady: false,
    };

    render(
      <ProfileGate>
        <div>needs-payment</div>
      </ProfileGate>
    );

    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith('/onboarding/plans');
    });
  });
});
