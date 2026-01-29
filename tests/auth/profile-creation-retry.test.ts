/**
 * Profile Creation Retry Integration Tests
 * Tests for transient database failures, concurrent scenarios, and retry logic
 */

import React from 'react'
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { useRouter } from 'next/navigation'

// Mock dependencies
vi.mock('next/navigation')
vi.mock('@/components/auth/SupabaseAuthProvider', () => ({
  SupabaseAuthProvider: ({ children }: { children: React.ReactNode }) => children,
}))

// Mock fetch for API calls
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock performance API
global.performance = {
  now: vi.fn(() => Date.now()),
} as any

describe('Profile Creation Retry Logic', () => {
  const mockPush = vi.fn()
  const mockReplace = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useRouter).mockReturnValue({
      push: mockPush,
      replace: mockReplace,
      back: vi.fn(),
      forward: vi.fn(),
      refresh: vi.fn(),
      prefetch: vi.fn(),
    })

    // Default successful auth state
    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/api/proxy/v1/auth/me')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            id: 'test-user-id',
            email: 'test@example.com',
            user_metadata: { name: 'Test User' },
          }),
        })
      }
      return Promise.resolve({
        ok: false,
        status: 404,
        json: () => Promise.resolve({ detail: 'Not found' }),
      })
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Transient Database Connection Failures', () => {
    it('should retry profile creation on database timeout', async () => {
      let attemptCount = 0
      mockFetch.mockImplementation((url: string) => {
        if (url.includes('/api/proxy/v1/auth/me')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              id: 'test-user-id',
              email: 'test@example.com',
            }),
          })
        }

        if (url.includes('/ensure-profile')) {
          attemptCount++
          if (attemptCount <= 2) {
            // Simulate database timeout
            return Promise.resolve({
              ok: false,
              status: 503,
              json: () => Promise.resolve({
                detail: 'Database connection timeout',
                error: 'DATABASE_TIMEOUT',
              }),
            })
          }
          // Success on third attempt
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              workspace_id: 'test-workspace-id',
              subscription_plan: 'starter',
              subscription_status: 'active',
            }),
          })
        }

        if (url.includes('/verify-profile')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              profile_exists: true,
              workspace_exists: true,
              workspace_id: 'test-workspace-id',
              subscription_plan: 'starter',
              subscription_status: 'active',
              needs_payment: false,
            }),
          })
        }

        return Promise.resolve({
          ok: false,
          status: 404,
        })
      })

      render(
        React.createElement(AuthProvider, null,
          React.createElement('div', null, 'Test Child')
        )
      )

      // Wait for retry attempts to complete
      await waitFor(() => {
        expect(attemptCount).toBe(3)
      }, { timeout: 5000 })

      // Verify successful completion
      await waitFor(() => {
        expect(mockReplace).toHaveBeenCalledWith('/dashboard')
      })
    })

    it('should handle exponential backoff between retries', async () => {
      const retryDelays: number[] = []
      const originalSetTimeout = global.setTimeout
      const mockSetTimeout = vi.fn((callback: (...args: any[]) => void, delay?: number) => {
        retryDelays.push(delay || 0)
        return originalSetTimeout(callback, 0) // Execute immediately for test
      }) as any
      global.setTimeout = mockSetTimeout

      let attemptCount = 0
      mockFetch.mockImplementation((url: string) => {
        if (url.includes('/ensure-profile')) {
          attemptCount++
          if (attemptCount <= 2) {
            return Promise.resolve({
              ok: false,
              status: 503,
              json: () => Promise.resolve({
                detail: 'Service unavailable',
                error: 'SERVICE_UNAVAILABLE',
              }),
            })
          }
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              workspace_id: 'test-workspace-id',
            }),
          })
        }

        if (url.includes('/verify-profile')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              profile_exists: true,
              workspace_exists: true,
              needs_payment: false,
            }),
          })
        }

        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ id: 'test' }),
        })
      })

      render(
        React.createElement(AuthProvider, null,
          React.createElement('div', null, 'Test Child')
        )
      )

      await waitFor(() => {
        expect(attemptCount).toBe(3)
      })

      // Verify exponential backoff (1s, 2s, 4s pattern)
      expect(retryDelays).toContain(1000)
      expect(retryDelays).toContain(2000)
      expect(retryDelays).toContain(4000)

      global.setTimeout = originalSetTimeout
    })
  })

  describe('Concurrent Profile Creation Scenarios', () => {
    it('should handle concurrent profile creation requests safely', async () => {
      const creationOrder: string[] = []

      mockFetch.mockImplementation((url: string) => {
        if (url.includes('/ensure-profile')) {
          creationOrder.push('ensure-profile')
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              workspace_id: 'test-workspace-id',
              subscription_plan: 'starter',
            }),
          })
        }

        if (url.includes('/verify-profile')) {
          creationOrder.push('verify-profile')
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              profile_exists: true,
              workspace_exists: true,
              needs_payment: false,
            }),
          })
        }

        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ id: 'test' }),
        })
      })

      // Simulate multiple rapid auth state changes
      const { rerender } = render(
        React.createElement(AuthProvider, null,
          React.createElement('div', null, 'Test Child')
        )
      )

      // Trigger multiple rapid checks
      rerender(
        React.createElement(AuthProvider, null,
          React.createElement('div', null, 'Test Child')
        )
      )

      rerender(
        React.createElement(AuthProvider, null,
          React.createElement('div', null, 'Test Child')
        )
      )

      await waitFor(() => {
        expect(creationOrder).toContain('ensure-profile')
        expect(creationOrder).toContain('verify-profile')
      })

      // Verify no duplicate workspace creation
      const ensureCalls = creationOrder.filter(call => call === 'ensure-profile')
      expect(ensureCalls.length).toBeLessThanOrEqual(3) // Max retry limit
    })

    it('should prevent race conditions with workspace creation', async () => {
      const workspaceCreationAttempts: any[] = []

      mockFetch.mockImplementation((url: string, options: any) => {
        if (url.includes('/ensure-profile')) {
          workspaceCreationAttempts.push(options)

          // Simulate concurrent creation detection
          return Promise.resolve({
            ok: false,
            status: 409,
            json: () => Promise.resolve({
              detail: 'Workspace already exists',
              error: 'WORKSPACE_EXISTS',
            }),
          })
        }

        if (url.includes('/verify-profile')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              profile_exists: true,
              workspace_exists: true,
              workspace_id: 'existing-workspace-id',
              needs_payment: false,
            }),
          })
        }

        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ id: 'test' }),
        })
      })

      render(
        React.createElement(AuthProvider, null,
          React.createElement('div', null, 'Test Child')
        )
      )

      await waitFor(() => {
        expect(workspaceCreationAttempts.length).toBeGreaterThan(0)
      })

      // Should handle conflict gracefully and proceed with verification
      await waitFor(() => {
        expect(mockReplace).toHaveBeenCalledWith('/dashboard')
      })
    })
  })

  describe('Workspace Creation Failures and Recovery', () => {
    it('should handle workspace creation failure and retry successfully', async () => {
      let workspaceAttempts = 0

      mockFetch.mockImplementation((url: string) => {
        if (url.includes('/ensure-profile')) {
          workspaceAttempts++
          if (workspaceAttempts === 1) {
            return Promise.resolve({
              ok: false,
              status: 500,
              json: () => Promise.resolve({
                detail: 'Workspace creation failed',
                error: 'WORKSPACE_CREATION_ERROR',
              }),
            })
          }
          // Success on retry
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              workspace_id: 'test-workspace-id',
              subscription_plan: 'growth',
            }),
          })
        }

        if (url.includes('/verify-profile')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              profile_exists: true,
              workspace_exists: true,
              needs_payment: false,
            }),
          })
        }

        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ id: 'test' }),
        })
      })

      render(
        React.createElement(AuthProvider, null,
          React.createElement('div', null, 'Test Child')
        )
      )

      await waitFor(() => {
        expect(workspaceAttempts).toBe(2)
      })

      await waitFor(() => {
        expect(mockReplace).toHaveBeenCalledWith('/dashboard')
      })
    })

    it('should handle permanent workspace creation failure', async () => {
      mockFetch.mockImplementation((url: string) => {
        if (url.includes('/ensure-profile')) {
          return Promise.resolve({
            ok: false,
            status: 500,
            json: () => Promise.resolve({
              detail: 'Permanent workspace creation failure',
              error: 'WORKSPACE_CREATION_ERROR',
            }),
          })
        }

        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ id: 'test' }),
        })
      })

      render(
        React.createElement(AuthProvider, null,
          React.createElement('div', null, 'Test Child')
        )
      )

      // Should show error state after max retries
      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
      }, { timeout: 10000 })

      // Should not redirect to dashboard
      expect(mockReplace).not.toHaveBeenCalledWith('/dashboard')
    })
  })

  describe('Performance Metrics Tracking', () => {
    it('should track profile verification timing', async () => {
      const performanceLogs: string[] = []
      const originalConsole = console.log
      console.log = vi.fn((...args) => {
        performanceLogs.push(args.join(' '))
      })

      mockFetch.mockImplementation((url: string) => {
        if (url.includes('/ensure-profile')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              workspace_id: 'test-workspace-id',
            }),
          })
        }

        if (url.includes('/verify-profile')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              profile_exists: true,
              workspace_exists: true,
              needs_payment: false,
            }),
          })
        }

        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ id: 'test' }),
        })
      })

      render(
        React.createElement(AuthProvider, null,
          React.createElement('div', null, 'Test Child')
        )
      )

      await waitFor(() => {
        expect(performanceLogs.some(log =>
          log.includes('Profile verification completed')
        )).toBe(true)
      })

      console.log = originalConsole
    })

    it('should warn when verification exceeds 1s SLA', async () => {
      const warningLogs: string[] = []
      const originalConsoleWarn = console.warn
      console.warn = vi.fn((...args) => {
        warningLogs.push(args.join(' '))
      })

      // Mock slow performance
      global.performance.now = vi.fn()
        .mockReturnValueOnce(0)
        .mockReturnValueOnce(1500) // 1.5s - above SLA

      mockFetch.mockImplementation((url: string) => {
        if (url.includes('/ensure-profile')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              workspace_id: 'test-workspace-id',
            }),
          })
        }

        if (url.includes('/verify-profile')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              profile_exists: true,
              workspace_exists: true,
              needs_payment: false,
            }),
          })
        }

        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ id: 'test' }),
        })
      })

      render(
        React.createElement(AuthProvider, null,
          React.createElement('div', null, 'Test Child')
        )
      )

      await waitFor(() => {
        expect(warningLogs.some(log =>
          log.includes('above 1s SLA')
        )).toBe(true)
      })

      console.warn = originalConsoleWarn
    })
  })

  describe('Optimistic Caching', () => {
    it('should preload workspace data when profile is ready', async () => {
      const preloadCalls: string[] = []

      mockFetch.mockImplementation((url: string) => {
        if (url.includes('/ensure-profile')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              workspace_id: 'test-workspace-id',
            }),
          })
        }

        if (url.includes('/verify-profile')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              profile_exists: true,
              workspace_exists: true,
              workspace_id: 'test-workspace-id',
              needs_payment: false,
            }),
          })
        }

        if (url.includes('/me/workspace')) {
          preloadCalls.push(url)
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              workspace: { id: 'test-workspace-id', name: 'Test Workspace' },
            }),
          })
        }

        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ id: 'test' }),
        })
      })

      render(
        React.createElement(AuthProvider, null,
          React.createElement('div', null, 'Test Child')
        )
      )

      await waitFor(() => {
        expect(preloadCalls).toContain('/api/proxy/v1/auth/me/workspace')
      })
    })
  })
})
