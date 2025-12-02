export interface PhonePeConfig {
  merchantId: string;
  merchantKey: string;
  env: 'sandbox' | 'production';
  webhookSecret?: string;
}

export interface TokenResponse {
  access_token: string;
  encrypted_access_token: string;
  expires_in: number | null;
  issued_at: number;
  expires_at: number;
  session_expires_at: number;
  token_type: string;
}

export interface CreatePaymentRequest {
  merchantOrderId: string;
  amount: number;
  redirectUrl?: string;
  callbackUrl?: string;
  mobileNumber?: string;
  paymentInstrument?: any;
}

export interface PaymentResponse {
  code: string;
  message: string;
  data: {
    merchantId: string;
    merchantTransactionId: string;
    instrumentResponse: {
      type: string;
      redirectInfo: {
        url: string;
        method: string;
      };
    };
  };
}

export interface SubscriptionSetupRequest {
  merchantOrderId: string;
  amount: number; // In paise (min 100)
  expireAt?: number; // Epoch millis
  metaInfo?: Record<string, string>;
  paymentFlow: {
    type: 'SUBSCRIPTION_SETUP';
    merchantSubscriptionId: string;
    authWorkflowType: 'TRANSACTION' | 'PENNY_DROP';
    amountType: 'FIXED' | 'VARIABLE';
    maxAmount: number; // In paise
    frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'YEARLY' | 'ON_DEMAND';
    expireAt?: number; // Subscription expiry
    paymentMode: {
      type: 'UPI_INTENT' | 'UPI_COLLECT';
      targetApp?: string; // For UPI_INTENT
      details?: {
        type: 'VPA';
        vpa: string;
      }; // For UPI_COLLECT
    };
  };
  deviceContext?: {
    deviceOS: 'ANDROID' | 'IOS';
  };
}

export interface SubscriptionSetupResponse {
  orderId: string;
  state: 'PENDING' | 'COMPLETED' | 'FAILED';
  intentUrl?: string; // For UPI_INTENT
}

export interface RecurringChargeRequest {
  merchantOrderId: string;
  amount: number; // In paise
  paymentFlow: {
    type: 'SUBSCRIPTION_REDEMPTION';
    merchantSubscriptionId: string;
    redemptionRetryStrategy: 'STANDARD' | 'CUSTOM';
    autoDebit: boolean;
  };
}
