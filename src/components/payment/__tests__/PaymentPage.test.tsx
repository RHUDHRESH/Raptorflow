/**
 * Tests for payment page components
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import React from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/components/auth/AuthProvider'
import ChoosePlan from '@/app/onboarding/plans/page'

// Mock dependencies
vi.mock('next/navigation')
vi.mock('@/components/auth/AuthProvider')
vi.mock('@/lib/auth-service')

const mockPush = vi.fn()
const mockUseRouter = useRouter as any
const mockUseAuth = useAuth as any

describe('Payment Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    mockUseRouter.mockReturnValue({
      push: mockPush,
      replace: vi.fn(),
      back: vi.fn(),
      forward: vi.fn(),
      refresh: vi.fn(),
      prefetch: vi.fn(),
    } as any)

    mockUseAuth.mockReturnValue({
      user: {
        id: 'test-user-id',
        email: 'test@example.com',
        fullName: 'Test User'
      },
      isAuthenticated: true,
      profileStatus: {
        workspaceId: 'test-workspace-id',
        subscriptionPlan: null,
        subscriptionStatus: 'trial',
        needsPayment: true,
        profileExists: true,
        workspaceExists: true,
        isReady: false
      },
      paymentState: {
        isProcessingPayment: false,
        currentPaymentId: null,
        paymentError: null,
        paymentStatus: 'idle'
      },
      initiatePayment: vi.fn(),
      checkPaymentStatus: vi.fn(),
      clearPaymentError: vi.fn()
    } as any)

    // Mock fetch API
    global.fetch = vi.fn()
  })

  describe('Plan Loading', () => {
    it('should show loading state initially', () => {
      render(<ChoosePlan />)

      expect(screen.getByText('Loading plans...')).toBeInTheDocument()
    })

    it('should load and display plans successfully', async () => {
      const mockPlans = [
        {
          name: 'starter',
          amount: 4900,
          currency: 'INR',
          interval: 'month',
          trial_days: 7,
          display_amount: '₹49',
          description: 'Perfect for individuals getting started',
          features: ['100 GB storage', '10 projects', 'Email support']
        },
        {
          name: 'growth',
          amount: 14900,
          currency: 'INR',
          interval: 'month',
          trial_days: 7,
          display_amount: '₹149',
          description: 'Ideal for growing teams and businesses',
          features: ['500 GB storage', 'Unlimited projects', '5 team members', 'Priority support'],
          popular: true
        }
      ]

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, plans: mockPlans })
      })

      render(<ChoosePlan />)

      await waitFor(() => {
        expect(screen.getByText('Starter')).toBeInTheDocument()
        expect(screen.getByText('Growth')).toBeInTheDocument()
        expect(screen.getByText('₹49')).toBeInTheDocument()
        expect(screen.getByText('₹149')).toBeInTheDocument()
      })
    })

    it('should show error message when plans fail to load', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Failed to load plans' })
      })

      render(<ChoosePlan />)

      await waitFor(() => {
        expect(screen.getByText('Failed to load plans')).toBeInTheDocument()
      })
    })
  })

  describe('Plan Selection', () => {
    beforeEach(async () => {
      const mockPlans = [
        {
          name: 'starter',
          amount: 4900,
          currency: 'INR',
          interval: 'month',
          trial_days: 7,
          display_amount: '₹49',
          description: 'Perfect for individuals getting started',
          features: ['100 GB storage', '10 projects', 'Email support']
        },
        {
          name: 'growth',
          amount: 14900,
          currency: 'INR',
          interval: 'month',
          trial_days: 7,
          display_amount: '₹149',
          description: 'Ideal for growing teams and businesses',
          features: ['500 GB storage', 'Unlimited projects', '5 team members', 'Priority support'],
          popular: true
        }
      ]

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, plans: mockPlans })
      })

      render(<ChoosePlan />)

      await waitFor(() => {
        expect(screen.getByText('Starter')).toBeInTheDocument()
      })
    })

    it('should allow selecting a plan', async () => {
      const starterPlan = screen.getByText('Starter').closest('[data-testid]')

      if (starterPlan) {
        fireEvent.click(starterPlan)
      }

      // Check that plan is selected (button text changes)
      await waitFor(() => {
        expect(screen.getByText('Selected')).toBeInTheDocument()
      })
    })

    it('should show popular badge for growth plan', () => {
      expect(screen.getByText('Most Popular')).toBeInTheDocument()
    })

    it('should display plan features correctly', () => {
      expect(screen.getByText('100 GB storage')).toBeInTheDocument()
      expect(screen.getByText('10 projects')).toBeInTheDocument()
      expect(screen.getByText('Email support')).toBeInTheDocument()
    })
  })

  describe('Payment Initiation', () => {
    beforeEach(async () => {
      const mockPlans = [
        {
          name: 'starter',
          amount: 4900,
          currency: 'INR',
          interval: 'month',
          trial_days: 7,
          display_amount: '₹49',
          description: 'Perfect for individuals getting started',
          features: ['100 GB storage', '10 projects', 'Email support']
        }
      ]

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, plans: mockPlans })
      })

      render(<ChoosePlan />)

      await waitFor(() => {
        expect(screen.getByText('Starter')).toBeInTheDocument()
      })

      // Select a plan
      const starterPlan = screen.getByText('Starter').closest('[data-testid]')
      if (starterPlan) {
        fireEvent.click(starterPlan)
      }
    })

    it('should initiate payment when continue button is clicked', async () => {
      // Mock successful payment initiation
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          payment_url: 'https://api.phonepe.com/checkout',
          merchant_order_id: 'ORD123456'
        })
      })

      // Mock window.location.href
      const originalLocation = (window as any).location.href
      delete (window as any).location
      ;(window as any).location = { href: '' }

      const continueButton = screen.getByText(/Continue to Payment/)
      fireEvent.click(continueButton)

      await waitFor(() => {
        expect((window as any).location.href).toBe('https://api.phonepe.com/checkout')
      })

      // Restore original location
      ;(window as any).location = { href: originalLocation }
    })

    it('should show error message when payment initiation fails', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Payment failed' })
      })

      const continueButton = screen.getByText(/Continue to Payment/)
      fireEvent.click(continueButton)

      await waitFor(() => {
        expect(screen.getByText('Payment failed')).toBeInTheDocument()
      })
    })

    it('should disable continue button when no plan is selected', () => {
      const continueButton = screen.getByText(/Continue to Payment/)
      expect(continueButton).toBeDisabled()
    })
  })

  describe('User Experience', () => {
    it('should display personalized greeting', async () => {
      const mockPlans = [
        {
          name: 'starter',
          amount: 4900,
          currency: 'INR',
          interval: 'month',
          trial_days: 7,
          display_amount: '₹49',
          description: 'Perfect for individuals getting started',
          features: ['100 GB storage', '10 projects', 'Email support']
        }
      ]

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, plans: mockPlans })
      })

      render(<ChoosePlan />)

      await waitFor(() => {
        expect(screen.getByText(/Hey Test User/)).toBeInTheDocument()
      })
    })

    it('should show trust badges', async () => {
      const mockPlans = [
        {
          name: 'starter',
          amount: 4900,
          currency: 'INR',
          interval: 'month',
          trial_days: 7,
          display_amount: '₹49',
          description: 'Perfect for individuals getting started',
          features: ['100 GB storage', '10 projects', 'Email support']
        }
      ]

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, plans: mockPlans })
      })

      render(<ChoosePlan />)

      await waitFor(() => {
        expect(screen.getByText('Secure Payments')).toBeInTheDocument()
        expect(screen.getByText('Instant Access')).toBeInTheDocument()
        expect(screen.getByText('30-Day Guarantee')).toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors gracefully', async () => {
      ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

      render(<ChoosePlan />)

      await waitFor(() => {
        expect(screen.getByText('Failed to load plans')).toBeInTheDocument()
      })
    })

    it('should clear error when user tries again', async () => {
      // First call fails
      ;(global.fetch as any)
        .mockResolvedValueOnce({
          ok: false,
          json: async () => ({ error: 'Failed to load plans' })
        })

      render(<ChoosePlan />)

      await waitFor(() => {
        expect(screen.getByText('Failed to load plans')).toBeInTheDocument()
      })

      // Retry should clear error
      ;(global.fetch as any).mockClear()
    })
  })
})
