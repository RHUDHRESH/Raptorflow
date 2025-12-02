import crypto from 'crypto';
import { env } from '../../config/env';
import { TokenResponse, SubscriptionSetupRequest, SubscriptionSetupResponse, RecurringChargeRequest } from './types';

export class PhonePeClient {
  private merchantId: string;
  // private merchantKey: string; // Assuming salt key? Docs say client_secret for auth, salt_key for checksum?
  // Wait, Auth API uses client_id + client_secret. Standard Checkout/Subscription APIs use X-VERIFY header (checksum).
  // The provided docs show OAuth token generation using client_id/secret.
  // AND standard APIs using O-Bearer token.
  
  // Let's clarify credentials mapping based on docs:
  // Auth: client_id, client_secret
  // APIs: Access Token from Auth
  
  private clientId: string;
  private clientSecret: string;
  private clientVersion: number = 1;
  private baseUrl: string;
  
  private accessToken: string | null = null;
  private tokenExpiry: number = 0;

  constructor() {
    // We reuse PHONEPE_MERCHANT_ID as client_id if not separate?
    // Usually client_id is different from merchant_id in PhonePe new stack?
    // Docs say "Client ID shared by PhonePe PG".
    // For now, let's assume we put Client ID in PHONEPE_MERCHANT_ID and Secret in KEY.
    // Or we might need new env vars if they differ.
    // Let's assume:
    this.clientId = env.PHONEPE_MERCHANT_ID; 
    this.clientSecret = env.PHONEPE_MERCHANT_KEY;
    this.merchantId = env.PHONEPE_MERCHANT_ID; // Often same or related
    
    this.baseUrl = env.PHONEPE_ENV === 'production' 
      ? 'https://api.phonepe.com/apis'
      : 'https://api-preprod.phonepe.com/apis/pg-sandbox';
  }

  /**
   * Get valid access token
   */
  async getAccessToken(): Promise<string> {
    if (this.accessToken && Date.now() < this.tokenExpiry) {
      return this.accessToken;
    }

    const url = `${this.baseUrl}/v1/oauth/token`;
    
    const params = new URLSearchParams();
    params.append('client_id', this.clientId);
    params.append('client_version', this.clientVersion.toString());
    params.append('client_secret', this.clientSecret);
    params.append('grant_type', 'client_credentials');

    console.log('Fetching PhonePe Token from:', url);

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`PhonePe Auth Failed: ${response.status} - ${errorText}`);
    }

    const data = (await response.json()) as TokenResponse;
    this.accessToken = data.access_token;
    // expires_in is seconds? Response sample has "expires_at" (epoch seconds).
    // Let's use expires_at from response, or default to 3600s.
    // Response sample: "expires_at": 1706697605
    this.tokenExpiry = (data.expires_at * 1000) - 60000; // Buffer 1 min
    
    return this.accessToken;
  }

  /**
   * Setup Subscription (Autopay)
   */
  async setupSubscription(request: SubscriptionSetupRequest): Promise<SubscriptionSetupResponse> {
    const token = await this.getAccessToken();
    const url = `${this.baseUrl}/pg-sandbox/subscriptions/v2/setup`; // sandbox path
    // Note: Prod path is /pg/subscriptions/v2/setup. We need to handle path difference.
    const path = env.PHONEPE_ENV === 'production' 
      ? '/pg/subscriptions/v2/setup'
      : '/pg-sandbox/subscriptions/v2/setup';

    const fullUrl = this.baseUrl.replace('/apis', '/apis') + path; 
    // Wait, baseUrl is `.../apis/pg-sandbox`? No, prompt code used `.../apis/pg-sandbox` as base.
    // Auth URL was `/v1/oauth/token`.
    // Subscription URL is `/subscriptions/v2/setup`.
    // Let's adjust baseUrl logic.
    
    // Correct Base URLs from docs:
    // Sandbox Auth: https://api-preprod.phonepe.com/apis/pg-sandbox/v1/oauth/token
    // Sandbox Sub: https://api-preprod.phonepe.com/apis/pg-sandbox/subscriptions/v2/setup
    
    // So base is consistent.
    
    const response = await fetch(`${this.baseUrl}/subscriptions/v2/setup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `O-Bearer ${token}`,
        'Accept': 'application/json'
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Subscription Setup Failed: ${response.status} - ${error}`);
    }

    return (await response.json()) as SubscriptionSetupResponse;
  }

  /**
   * Notify Redemption (Recurring Charge)
   */
  async notifyRedemption(request: any): Promise<any> {
     const token = await this.getAccessToken();
     const response = await fetch(`${this.baseUrl}/subscriptions/v2/notify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `O-Bearer ${token}`,
        'Accept': 'application/json'
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
       throw new Error(`Notify Redemption Failed: ${response.status}`);
    }
    return await response.json();
  }
  
  // TODO: Add other methods (Check Status, Cancel, etc.)
}

export const phonePeClient = new PhonePeClient();
