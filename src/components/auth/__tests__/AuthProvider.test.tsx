/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, waitFor, act, fireEvent } from '@testing-library/react';
import { useRouter, usePathname } from 'next/navigation';
import { AuthProvider, useAuth } from '@/components/auth/AuthProvider';
import { ProfileGate } from '@/components/auth/ProfileGate';
import { clientAuth } from '@/lib/auth-service';

// Mock dependencies
jest.mock('@/lib/auth-service');
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  usePathname: jest.fn(),
}));

// Mock fetch
global.fetch = jest.fn();

const mockClientAuth = clientAuth as jest.Mocked<typeof clientAuth>;
const mockRouter = {
  replace: jest.fn(),
  push: jest.fn(),
};
const mockPathname = '/dashboard';

beforeEach(() => {
  jest.useFakeTimers();
  (useRouter as jest.Mock).mockReturnValue(mockRouter);
  (usePathname as jest.Mock).mockReturnValue(mockPathname);
  (fetch as jest.Mock).mockClear();
  mockRouter.replace.mockClear();
  mockRouter.push.mockClear();
});

afterEach(() => {
  jest.useRealTimers();
});

describe('AuthProvider', () => {
  const mockUser = {
    id: 'test-user-123',
    email: 'test@example.com',
    full_name: 'Test User',
  };

  const mockProfileResponse = {
    profile_exists: true,
    workspace_exists: true,
    workspace_id: 'test-workspace',
    subscription_plan: 'pro',
    subscription_status: 'active',
    needs_payment: false,
  };

  test('initializes with loading state', async () => {
    mockClientAuth.getCurrentUser.mockResolvedValue(null);
    mockClientAuth.getSession.mockResolvedValue(null);
    mockClientAuth.getSupabaseClient.mockReturnValue({
      auth: {
        onAuthStateChange: jest.fn(() => ({
          data: { subscription: { unsubscribe: jest.fn() } },
        })),
      },
    } as any);

    const TestComponent = () => {
      const auth = useAuth();
      return React.createElement(
        'div',
        null,
        React.createElement('div', { 'data-testid': 'is-loading' }, auth.isLoading.toString()),
        React.createElement('div', { 'data-testid': 'is-authenticated' }, auth.isAuthenticated.toString())
      );
    };

    render(
      React.createElement(
        AuthProvider,
        null,
        React.createElement(TestComponent, null)
      )
    );

    expect(screen.getByTestId('is-loading')).toHaveTextContent('true');
    expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
  });

  test('handles successful authentication and profile verification', async () => {
    mockClientAuth.getCurrentUser.mockResolvedValue(mockUser);
    mockClientAuth.getSession.mockResolvedValue({ user: mockUser });
    mockClientAuth.getSupabaseClient.mockReturnValue({
      auth: {
        onAuthStateChange: jest.fn(() => ({
          data: { subscription: { unsubscribe: jest.fn() } },
        })),
      },
    } as any);

    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockProfileResponse,
      } as Response);

    const TestComponent = () => {
      const auth = useAuth();
      return React.createElement(
        'div',
        null,
        React.createElement('div', { 'data-testid': 'profile-ready' }, auth.profileStatus.isReady.toString())
      );
    };

    render(
      React.createElement(
        AuthProvider,
        null,
        React.createElement(TestComponent, null)
      )
    );

    await waitFor(() => {
      expect(screen.getByTestId('profile-ready')).toHaveTextContent('true');
    });

    expect(fetch).toHaveBeenCalledTimes(2);
  });

  test('implements caching and debouncing', async () => {
    mockClientAuth.getCurrentUser.mockResolvedValue(mockUser);
    mockClientAuth.getSession.mockResolvedValue({ user: mockUser });
    mockClientAuth.getSupabaseClient.mockReturnValue({
      auth: {
        onAuthStateChange: jest.fn(() => ({
          data: { subscription: { unsubscribe: jest.fn() } },
        })),
      },
    } as any);

    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockProfileResponse,
      } as Response);

    const TestComponent = () => {
      const auth = useAuth();
      return React.createElement(
        'div',
        null,
        React.createElement('button', { onClick: () => auth.refreshProfileStatus() }, 'Refresh')
      );
    };

    render(
      React.createElement(
        AuthProvider,
        null,
        React.createElement(TestComponent, null)
      )
    );

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2);
    });

    (fetch as jest.Mock).mockClear();

    act(() => {
      screen.getByText('Refresh').click();
      screen.getByText('Refresh').click();
      screen.getByText('Refresh').click();
    });

    expect(fetch).not.toHaveBeenCalled();

    act(() => {
      jest.advanceTimersByTime(600);
    });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2);
    });
  });
});

describe('ProfileGate', () => {
  const mockUser = {
    id: 'test-user-123',
    email: 'test@example.com',
    full_name: 'Test User',
  };

  const mockProfileStatus = {
    workspaceId: 'test-workspace',
    subscriptionPlan: 'pro',
    subscriptionStatus: 'active',
    needsPayment: false,
    profileExists: true,
    workspaceExists: true,
    isReady: true,
  };

  test('allows access when authenticated and profile is ready', () => {
    const TestComponent = () => {
      const authValue = {
        user: mockUser,
        session: { user: mockUser },
        isLoading: false,
        isAuthenticated: true,
        profileStatus: mockProfileStatus,
        isCheckingProfile: false,
        refreshProfileStatus: jest.fn(),
        login: jest.fn(),
        loginWithGoogle: jest.fn(),
        logout: jest.fn(),
        refreshUser: jest.fn(),
      };

      return React.createElement(
        'div',
        null,
        React.createElement(
          ProfileGate,
          null,
          React.createElement('div', { 'data-testid': 'protected-content' }, 'Protected Content')
        )
      );
    };

    render(
      React.createElement(
        AuthProvider,
        null,
        React.createElement(TestComponent, null)
      )
    );

    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
  });

  test('redirects to onboarding when profile does not exist', () => {
    const profileStatus = { ...mockProfileStatus, profileExists: false, isReady: false };

    const TestComponent = () => {
      const authValue = {
        user: mockUser,
        session: { user: mockUser },
        isLoading: false,
        isAuthenticated: true,
        profileStatus,
        isCheckingProfile: false,
        refreshProfileStatus: jest.fn(),
        login: jest.fn(),
        loginWithGoogle: jest.fn(),
        logout: jest.fn(),
        refreshUser: jest.fn(),
      };

      return React.createElement(
        'div',
        null,
        React.createElement(ProfileGate, null, null)
      );
    };

    render(
      React.createElement(
        AuthProvider,
        null,
        React.createElement(TestComponent, null)
      )
    );

    expect(mockRouter.replace).toHaveBeenCalledWith('/onboarding/start');
  });

  test('prevents endless redirects', () => {
    const profileStatus = { ...mockProfileStatus, profileExists: false, isReady: false };

    const TestComponent = () => {
      const authValue = {
        user: mockUser,
        session: { user: mockUser },
        isLoading: false,
        isAuthenticated: true,
        profileStatus,
        isCheckingProfile: false,
        refreshProfileStatus: jest.fn(),
        login: jest.fn(),
        loginWithGoogle: jest.fn(),
        logout: jest.fn(),
        refreshUser: jest.fn(),
      };

      return React.createElement(
        'div',
        null,
        React.createElement(ProfileGate, null, null)
      );
    };

    render(
      React.createElement(
        AuthProvider,
        null,
        React.createElement(TestComponent, null)
      )
    );

    expect(mockRouter.replace).toHaveBeenCalledTimes(1);
    expect(mockRouter.replace).toHaveBeenCalledWith('/onboarding/start');

    mockRouter.replace.mockClear();
    render(
      React.createElement(
        AuthProvider,
        null,
        React.createElement(TestComponent, null)
      )
    );

    expect(mockRouter.replace).not.toHaveBeenCalled();
  });
});
