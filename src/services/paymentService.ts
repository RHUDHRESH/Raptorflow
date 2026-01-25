/**
 * Unified Payment Service
 * Consolidates all payment-related operations into a single service
 */

export interface PaymentRequest {
  planId: string;
  billingCycle: 'monthly' | 'annual';
  userId?: string;
}

export interface PaymentResponse {
  success: boolean;
  payment?: {
    paymentId: string;
    amount: number;
    currency: string;
    status: string;
    redirectUrl: string;
    message?: string;
  };
  error?: string;
}

export interface PlanDetails {
  id: string;
  name: string;
  price: {
    monthly: number;
    annual: number;
  };
  features: string[];
}

class PaymentService {
  private static instance: PaymentService;
  private baseUrl: string;

  private constructor() {
    this.baseUrl = typeof window !== 'undefined' 
      ? window.location.origin 
      : 'http://localhost:3001';
  }

  public static getInstance(): PaymentService {
    if (!PaymentService.instance) {
      PaymentService.instance = new PaymentService();
    }
    return PaymentService.instance;
  }

  /**
   * Create a payment order
   */
  public async createPayment(request: PaymentRequest): Promise<PaymentResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/create-payment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      const data = await response.json();
      
      if (!response.ok) {
        return {
          success: false,
          error: data.error || 'Failed to create payment'
        };
      }

      return data;
    } catch (error) {
      console.error('Payment service error:', error);
      return {
        success: false,
        error: 'Payment service unavailable'
      };
    }
  }

  /**
   * Get available plans
   */
  public async getPlans(): Promise<PlanDetails[]> {
    // For now, return mock plans - in production this would fetch from API
    return [
      {
        id: 'ascent',
        name: 'Ascent',
        price: { monthly: 2900, annual: 2400 }, // in cents
        features: [
          'Foundation setup (ICP + Positioning)',
          'Weekly Moves (3 per week)',
          'Basic Muse AI generation',
          'Matrix analytics dashboard',
          'Email support'
        ]
      },
      {
        id: 'glide',
        name: 'Glide',
        price: { monthly: 7900, annual: 6600 }, // in cents
        features: [
          'Everything in Ascent',
          'Unlimited Moves',
          'Advanced Muse (voice training)',
          'Cohort segmentation',
          'Campaign planning tools',
          'Priority support',
          'Blackbox learnings vault'
        ]
      },
      {
        id: 'soar',
        name: 'Soar',
        price: { monthly: 19900, annual: 16600 }, // in cents
        features: [
          'Everything in Glide',
          'Team seats (up to 5)',
          'White-label exports',
          'Custom AI training',
          'API access',
          'Dedicated success manager',
          'Custom integrations'
        ]
      }
    ];
  }

  /**
   * Validate payment request
   */
  private validatePaymentRequest(request: PaymentRequest): string[] {
    const errors: string[] = [];

    if (!request.planId) {
      errors.push('Plan ID is required');
    }

    if (!request.billingCycle || !['monthly', 'annual'].includes(request.billingCycle)) {
      errors.push('Valid billing cycle is required');
    }

    return errors;
  }

  /**
   * Calculate price based on plan and billing cycle
   */
  public calculatePrice(planId: string, billingCycle: 'monthly' | 'annual'): number {
    const plans = [
      { id: 'ascent', monthly: 2900, annual: 2400 },
      { id: 'glide', monthly: 7900, annual: 6600 },
      { id: 'soar', monthly: 19900, annual: 16600 }
    ];

    const plan = plans.find(p => p.id === planId);
    if (!plan) {
      throw new Error('Invalid plan ID');
    }

    return billingCycle === 'annual' ? plan.annual : plan.monthly;
  }
}

// Export singleton instance
export const paymentService = PaymentService.getInstance();
