import { Router, Request, Response } from 'express';
import crypto from 'crypto';
import { db, supabase } from '../lib/supabase';
import { env } from '../config/env';

const router = Router();

const RBI_AUTOPAY_LIMIT_PAISE = 500000;

type PhonePeCheckoutState = 'PENDING' | 'COMPLETED' | 'FAILED';

/**
 * PhonePe Configuration
 * Documentation: https://developer.phonepe.com/v1/docs/api-integration
 */
const PHONEPE_CONFIG = {
  merchantId: env.PHONEPE_MERCHANT_ID || '',
  saltKey: env.PHONEPE_SALT_KEY || '',
  saltIndex: env.PHONEPE_SALT_INDEX || '1',
  env: (env.PHONEPE_ENV || 'UAT') as 'UAT' | 'PRODUCTION',
  // API Endpoints
  get payEndpoint() {
    return this.env === 'PRODUCTION'
      ? 'https://api.phonepe.com/apis/hermes/pg/v1/pay'
      : 'https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay';
  },
  get statusEndpoint() {
    return this.env === 'PRODUCTION'
      ? 'https://api.phonepe.com/apis/hermes/pg/v1/status'
      : 'https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/status';
  }
};

const PHONEPE_STANDARD_CONFIG = {
  env: (env.PHONEPE_ENV || 'UAT') as 'UAT' | 'PRODUCTION',
  clientId: env.PHONEPE_CLIENT_ID || '',
  clientSecret: env.PHONEPE_CLIENT_SECRET || '',
  clientVersion: env.PHONEPE_CLIENT_VERSION || '1',
  webhookUsername: env.PHONEPE_WEBHOOK_USERNAME || '',
  webhookPassword: env.PHONEPE_WEBHOOK_PASSWORD || '',
  get apiBase() {
    if (this.env === 'PRODUCTION' && env.PHONEPE_STANDARD_API_BASE) {
      return env.PHONEPE_STANDARD_API_BASE;
    }
    // Docs show sandbox as: https://api-preprod.phonepe.com/apis/pg-sandbox
    // Production base is not explicitly shown in the snippet; PhonePe uses api.phonepe.com/apis for live.
    return this.env === 'PRODUCTION'
      ? 'https://api.phonepe.com/apis'
      : 'https://api-preprod.phonepe.com/apis/pg-sandbox';
  },
  get oauthTokenEndpoint() {
    return `${this.apiBase}/v1/oauth/token`;
  },
  get checkoutPayEndpoint() {
    return `${this.apiBase}/checkout/v2/pay`;
  },
  get checkoutOrderStatusBase() {
    return `${this.apiBase}/checkout/v2/order`;
  }
};

const isPhonePeStandardConfigured = () => {
  return !!(PHONEPE_STANDARD_CONFIG.clientId && PHONEPE_STANDARD_CONFIG.clientSecret && PHONEPE_STANDARD_CONFIG.clientVersion);
};

let phonepeOAuthTokenCache: { token: string; expiresAtEpochSeconds: number } | null = null;

async function getPhonePeStandardAuthToken(): Promise<string> {
  if (!isPhonePeStandardConfigured()) {
    throw new Error('PhonePe Standard Checkout not configured');
  }

  const nowSeconds = Math.floor(Date.now() / 1000);
  if (phonepeOAuthTokenCache && phonepeOAuthTokenCache.expiresAtEpochSeconds - 60 > nowSeconds) {
    return phonepeOAuthTokenCache.token;
  }

  const body = new URLSearchParams({
    client_id: PHONEPE_STANDARD_CONFIG.clientId,
    client_version: PHONEPE_STANDARD_CONFIG.clientVersion,
    client_secret: PHONEPE_STANDARD_CONFIG.clientSecret,
    grant_type: 'client_credentials'
  });

  const response = await fetch(PHONEPE_STANDARD_CONFIG.oauthTokenEndpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body
  });

  const data: any = await response.json();
  if (!response.ok) {
    throw new Error(data?.message || 'Failed to fetch PhonePe auth token');
  }

  const token = data?.access_token;
  const expiresAt = data?.expires_at;
  if (!token || !expiresAt) {
    throw new Error('Invalid PhonePe auth token response');
  }

  phonepeOAuthTokenCache = { token, expiresAtEpochSeconds: Number(expiresAt) };
  return token;
}

// Plan pricing (in paise - 100 paise = 1 INR)
// All plans are 30-day subscriptions, no proration allowed
const PLANS: Record<string, { price: number; name: string; cohorts: number; durationDays: number }> = {
  ascent: { price: 499900, name: 'Ascent', cohorts: 3, durationDays: 30 },      // ₹4,999
  glide: { price: 699900, name: 'Glide', cohorts: 5, durationDays: 30 },        // ₹6,999
  soar: { price: 1199900, name: 'Soar', cohorts: 10, durationDays: 30 }         // ₹11,999
};

const formatPrice = (paise: number) => `INR ${(paise / 100).toLocaleString('en-IN')}`;

/**
 * Generate PhonePe checksum
 * Formula: SHA256(base64Payload + "/pg/v1/pay" + saltKey) + "###" + saltIndex
 */
function generateChecksum(base64Payload: string, endpoint: string = '/pg/v1/pay'): string {
  const stringToHash = base64Payload + endpoint + PHONEPE_CONFIG.saltKey;
  const sha256Hash = crypto.createHash('sha256').update(stringToHash).digest('hex');
  return sha256Hash + '###' + PHONEPE_CONFIG.saltIndex;
}

/**
 * Verify webhook checksum
 */
function verifyChecksum(base64Response: string, receivedChecksum: string): boolean {
  if (!receivedChecksum) return false;

  const received = receivedChecksum.trim();
  const candidates = [
    generateChecksum(base64Response, '/pg/v1/pay'),
    generateChecksum(base64Response, '/pg/v1/status'),
    crypto.createHash('sha256').update(base64Response + PHONEPE_CONFIG.saltKey).digest('hex') + '###' + PHONEPE_CONFIG.saltIndex,
  ];

  return candidates.some(c => c.toLowerCase() === received.toLowerCase());
}

function sha256Hex(input: string): string {
  return crypto.createHash('sha256').update(input).digest('hex');
}

function verifyStandardWebhookAuth(receivedAuthorization: string | undefined): boolean {
  if (!receivedAuthorization) return false;
  if (!PHONEPE_STANDARD_CONFIG.webhookUsername || !PHONEPE_STANDARD_CONFIG.webhookPassword) return false;
  const expected = sha256Hex(`${PHONEPE_STANDARD_CONFIG.webhookUsername}:${PHONEPE_STANDARD_CONFIG.webhookPassword}`);
  return expected.toLowerCase() === String(receivedAuthorization).trim().toLowerCase();
}

function mapCheckoutStateToPaymentStatus(state: PhonePeCheckoutState): 'completed' | 'pending' | 'failed' {
  if (state === 'COMPLETED') return 'completed';
  if (state === 'PENDING') return 'pending';
  return 'failed';
}

// Middleware to verify JWT token
const verifyToken = async (req: Request, res: Response, next: Function) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing authorization' });
  }

  const token = authHeader.split(' ')[1];
  
  try {
    const { data: { user }, error } = await supabase.auth.getUser(token);
    
    if (error || !user) {
      return res.status(401).json({ error: 'Invalid token' });
    }

    (req as any).user = user;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Token verification failed' });
  }
};

/**
 * GET /api/payments/plans
 * Get available plans
 */
router.get('/plans', (req: Request, res: Response) => {
  const plans = Object.entries(PLANS).map(([id, plan]) => ({
    id,
    name: plan.name,
    price: plan.price,
    priceDisplay: formatPrice(plan.price),
    cohorts: plan.cohorts
  }));
  
  res.json({ plans });
});

/**
 * POST /api/payments/initiate
 * Initiate a PhonePe payment
 */
router.post('/initiate', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const userEmail = (req as any).user.email;
    const { plan, phone, autopayRequested, billingCycle } = req.body;

    // Validate plan
    if (!plan || !PLANS[plan]) {
      return res.status(400).json({ error: 'Invalid plan selected' });
    }

    const planDetails = PLANS[plan];

    if (autopayRequested === true && billingCycle && String(billingCycle).toLowerCase() !== 'monthly') {
      return res.status(400).json({
        error: 'Autopay is only supported for monthly plans'
      });
    }

    if (autopayRequested === true && planDetails.price > RBI_AUTOPAY_LIMIT_PAISE) {
      return res.status(400).json({
        error: 'Autopay is not allowed for amounts over ₹5,000 (RBI e-mandate limit)'
      });
    }
    
    // Generate unique transaction ID
    const txnId = `RF${Date.now()}${crypto.randomBytes(4).toString('hex').toUpperCase()}`;
    
    // Create payment record in database
    const { data: payment, error: dbError } = await db.createPayment(
      userId, 
      plan, 
      planDetails.price, 
      txnId,
      userEmail
    );

    if (dbError) {
      console.error('DB Error creating payment:', dbError);
      return res.status(500).json({ error: 'Failed to create payment record' });
    }

    // Frontend URL for redirect
    const frontendUrl = env.FRONTEND_PUBLIC_URL || 'http://localhost:5173';
    const backendUrl = env.BACKEND_PUBLIC_URL || `http://localhost:${env.PORT || '8080'}`;

    // Create a pending mandate record when user opts into autopay (eligibility enforced above)
    if (autopayRequested === true) {
      const { data: paymentWithSub } = await db.getPaymentWithSubscriptionAndPlan(txnId);
      const subscriptionId = (paymentWithSub as any)?.subscription_id || (paymentWithSub as any)?.subscription?.id;
      const organizationId = (paymentWithSub as any)?.organization_id;
      if (subscriptionId && organizationId) {
        const now = new Date();
        const validUntil = new Date(now.getTime() + 365 * 24 * 60 * 60 * 1000);
        const { data: mandate } = await db.createPaymentMandate({
          organizationId,
          subscriptionId,
          maxAmountPaise: planDetails.price,
          provider: 'phonepe',
          mandateType: 'upi_autopay',
          validFrom: now.toISOString(),
          validUntil: validUntil.toISOString(),
          status: 'pending_authorization'
        });
        if (mandate?.id) {
          await db.linkMandateToSubscription(subscriptionId, mandate.id);
        }
      }
    }

    // Prefer Standard Checkout (OAuth + checkout/v2) when configured
    if (isPhonePeStandardConfigured()) {
      try {
        const token = await getPhonePeStandardAuthToken();

        const requestPayload = {
          merchantOrderId: txnId,
          amount: planDetails.price,
          paymentFlow: {
            type: 'PG_CHECKOUT',
            message: `Raptorflow ${planDetails.name} subscription`,
            merchantUrls: {
              redirectUrl: `${frontendUrl}/payment/callback?txnId=${txnId}`
            }
          }
        };

        const response = await fetch(PHONEPE_STANDARD_CONFIG.checkoutPayEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `O-Bearer ${token}`
          },
          body: JSON.stringify(requestPayload)
        });

        const data: any = await response.json();
        if (!response.ok) {
          await db.updatePayment(txnId, {
            status: 'failed',
            response_message: data?.message || 'PhonePe create payment failed'
          });
          return res.status(400).json({ error: data?.message || 'Payment initiation failed' });
        }

        if (data?.orderId) {
          await db.updatePayment(txnId, {
            provider_payment_id: data.orderId
          });
        }

        if (data?.redirectUrl) {
          return res.json({
            success: true,
            txnId,
            paymentUrl: data.redirectUrl,
            amount: planDetails.price,
            amountDisplay: formatPrice(planDetails.price),
            plan: planDetails.name,
            mock: false
          });
        }

        await db.updatePayment(txnId, {
          status: 'failed',
          response_message: 'PhonePe create payment response missing redirectUrl'
        });
        return res.status(400).json({ error: 'Payment initiation failed' });
      } catch (apiError: any) {
        console.error('PhonePe Standard Checkout error:', apiError);
        // fall through to legacy checksum mode / mock
      }
    }

    // Build PhonePe payload
    const payload = {
      merchantId: PHONEPE_CONFIG.merchantId,
      merchantTransactionId: txnId,
      merchantUserId: userId,
      amount: planDetails.price, // Amount in paise
      redirectUrl: `${frontendUrl}/payment/callback?txnId=${txnId}`,
      redirectMode: 'REDIRECT',
      callbackUrl: `${backendUrl}/api/payments/webhook`, // Server callback
      mobileNumber: phone || '',
      paymentInstrument: {
        type: 'PAY_PAGE'
      }
    };

    // Base64 encode the payload
    const base64Payload = Buffer.from(JSON.stringify(payload)).toString('base64');
    
    // Generate checksum
    const checksum = generateChecksum(base64Payload);

    // If we have valid PhonePe credentials, make the API call
    if (PHONEPE_CONFIG.merchantId && PHONEPE_CONFIG.saltKey) {
      try {
        console.log('Calling PhonePe API:', PHONEPE_CONFIG.payEndpoint);
        
        const response = await fetch(PHONEPE_CONFIG.payEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-VERIFY': checksum
          },
          body: JSON.stringify({ request: base64Payload })
        });

        const data: any = await response.json();
        console.log('PhonePe Response:', JSON.stringify(data, null, 2));

        if (data.success && data.data?.instrumentResponse?.redirectInfo?.url) {
          return res.json({
            success: true,
           txnId,
           paymentUrl: data.data.instrumentResponse.redirectInfo.url,
           amount: planDetails.price,
           amountDisplay: formatPrice(planDetails.price),
           plan: planDetails.name
         });
        }

        // If PhonePe returns an error
        console.error('PhonePe Error:', data);
        
        // Update payment with error
        await db.updatePayment(txnId, {
          status: 'failed',
          error: data.message || data.code || 'PhonePe API error'
        });

        return res.status(400).json({
          error: data.message || 'Payment initiation failed',
          code: data.code
        });

      } catch (apiError: any) {
        console.error('PhonePe API Error:', apiError);
        // Fall through to mock mode
      }
    }

    // Mock mode - for development/testing without PhonePe credentials
    console.log('Using mock payment mode');
    res.json({
      success: true,
      txnId,
      paymentUrl: `${frontendUrl}/payment/callback?txnId=${txnId}&mock=true`,
      amount: planDetails.price,
      amountDisplay: formatPrice(planDetails.price),
      plan: planDetails.name,
      mock: true
    });

  } catch (err: any) {
    console.error('Payment initiation error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/payments/webhook
 * Handle PhonePe server-to-server callback
 */
router.post('/webhook', async (req: Request, res: Response) => {
  try {
    console.log('PhonePe Webhook received:', req.body);

    // Standard Checkout webhook: JSON body with { event, payload } and Authorization header
    if (req.body?.event && req.body?.payload) {
      const authHeader = req.headers['authorization'] as string | undefined;
      if (!verifyStandardWebhookAuth(authHeader)) {
        return res.status(401).json({ error: 'Invalid webhook authorization' });
      }

      const event = String(req.body.event);
      const payload: any = req.body.payload;
      const merchantOrderId = payload?.merchantOrderId;
      const state: PhonePeCheckoutState | undefined = payload?.state;
      const orderId = payload?.orderId;
      const amount = payload?.amount;

      if (!merchantOrderId || !state) {
        return res.status(400).json({ error: 'Missing merchantOrderId/state' });
      }

      const { data: existingPayment } = await db.getPaymentWithSubscriptionAndPlan(merchantOrderId);
      if (!existingPayment) {
        // Unknown order id; acknowledge to avoid repeated retries.
        return res.json({ status: 'ignored' });
      }

      const expectedAmount = (existingPayment as any)?.amount_paise;
      if (typeof amount === 'number' && typeof expectedAmount === 'number' && Number(amount) !== Number(expectedAmount)) {
        console.error('Webhook amount mismatch', {
          merchantOrderId,
          received: amount,
          expected: expectedAmount
        });
        return res.json({ status: 'ignored' });
      }

      // Only process order events for now
      if (event === 'checkout.order.completed' || event === 'checkout.order.failed') {
        const status = mapCheckoutStateToPaymentStatus(state);
        await db.updatePayment(merchantOrderId, {
          status,
          provider_payment_id: orderId || undefined,
          response_message: status === 'failed' ? payload?.errorCode || payload?.detailedErrorCode || 'FAILED' : undefined
        });

        if (status === 'completed') {
          const subscriptionId = (existingPayment as any)?.subscription_id || (existingPayment as any)?.subscription?.id;
          if (subscriptionId) {
            await db.activateSubscription(subscriptionId);
          }
        }
      }

      return res.json({ status: 'ok' });
    }

    // Legacy PG webhook: base64 encoded response + X-VERIFY checksum
    const { response: encodedResponse } = req.body;
    const xVerify = req.headers['x-verify'] as string;

    if (!encodedResponse) {
      return res.status(400).json({ error: 'Missing response payload' });
    }

    if (!PHONEPE_CONFIG.saltKey || !PHONEPE_CONFIG.merchantId) {
      return res.status(500).json({ error: 'Payment gateway not configured' });
    }

    if (!xVerify) {
      return res.status(401).json({ error: 'Missing verification header' });
    }

    if (!verifyChecksum(encodedResponse, xVerify)) {
      console.error('Invalid webhook checksum', { received: xVerify });
      return res.status(401).json({ error: 'Invalid signature' });
    }

    const decodedResponse = JSON.parse(Buffer.from(encodedResponse, 'base64').toString('utf-8'));
    console.log('Decoded webhook response:', decodedResponse);

    const txnId = decodedResponse.data?.merchantTransactionId;
    const code = decodedResponse.code;

    if (!txnId) {
      return res.status(400).json({ error: 'Missing transaction ID' });
    }

    const { data: existingPayment } = await db.getPaymentWithSubscriptionAndPlan(txnId);
    if (!existingPayment) {
      return res.json({ status: 'ignored' });
    }

    const expectedAmount = (existingPayment as any)?.amount_paise;
    const receivedAmount = decodedResponse?.data?.amount;
    if (typeof receivedAmount === 'number' && typeof expectedAmount === 'number' && Number(receivedAmount) !== Number(expectedAmount)) {
      console.error('Legacy webhook amount mismatch', {
        txnId,
        received: receivedAmount,
        expected: expectedAmount
      });
      return res.json({ status: 'ignored' });
    }

    if (code === 'PAYMENT_SUCCESS') {
      await db.updatePayment(txnId, {
        status: 'completed',
        phonepe_transaction_id: decodedResponse.data?.transactionId
      });

      const subscriptionId = (existingPayment as any)?.subscription_id || (existingPayment as any)?.subscription?.id;
      if (subscriptionId) {
        await db.activateSubscription(subscriptionId);
      }
    } else if (code === 'PAYMENT_PENDING') {
      await db.updatePayment(txnId, {
        status: 'pending'
      });
    } else {
      await db.updatePayment(txnId, {
        status: 'failed',
        response_message: code
      });
    }

    return res.json({ status: 'ok' });
  } catch (err: any) {
    console.error('Webhook processing error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/payments/status/:txnId
 * Check payment status
 */
router.get('/status/:txnId', verifyToken, async (req: Request, res: Response) => {
  try {
    const { txnId } = req.params;
    const userId = (req as any).user.id;

    // Get from database first
    const { data: paymentWithSub, error } = await db.getPaymentWithSubscriptionAndPlan(txnId);

    if (error || !paymentWithSub) {
      return res.status(404).json({ error: 'Payment not found' });
    }

    const { data: currentOrgId, error: orgError } = await db.getOrCreateCurrentOrgId(userId);
    if (orgError || !currentOrgId) {
      return res.status(500).json({ error: 'Failed to resolve organization' });
    }

    if ((paymentWithSub as any).organization_id !== currentOrgId) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const planCode = (paymentWithSub as any)?.subscription?.plan?.code;
    const plan = planCode ? db.mapDbPlanCodeToFrontendPlan(planCode) : undefined;
    const amount = (paymentWithSub as any).amount_paise;

    // If payment is not completed and we have PhonePe credentials, check with PhonePe
    if ((paymentWithSub as any).status !== 'completed' && isPhonePeStandardConfigured()) {
      try {
        const token = await getPhonePeStandardAuthToken();
        const url = `${PHONEPE_STANDARD_CONFIG.checkoutOrderStatusBase}/${txnId}/status?details=false`;
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `O-Bearer ${token}`
          }
        });

        const data: any = await response.json();
        const state: PhonePeCheckoutState | undefined = data?.state;

        if (state && Number(data?.amount) === Number(amount)) {
          const mapped = mapCheckoutStateToPaymentStatus(state);
          if (mapped === 'completed') {
            await db.updatePayment(txnId, {
              status: 'completed',
              provider_payment_id: data?.orderId || undefined
            });

            const subscriptionId = (paymentWithSub as any)?.subscription_id || (paymentWithSub as any)?.subscription?.id;
            if (subscriptionId) {
              await db.activateSubscription(subscriptionId);
            }

            await db.markOnboardingCompleted(userId);

            return res.json({
              status: 'completed',
              plan,
              amount
            });
          }

          if (mapped === 'pending') {
            return res.json({
              status: 'pending',
              plan,
              amount
            });
          }

          await db.updatePayment(txnId, {
            status: 'failed',
            response_message: 'FAILED'
          });
          return res.json({
            status: 'failed',
            plan,
            amount
          });
        }
      } catch (apiError) {
        console.error('PhonePe Standard status check error:', apiError);
      }
    }

    if ((paymentWithSub as any).status !== 'completed' && PHONEPE_CONFIG.merchantId && PHONEPE_CONFIG.saltKey) {
      try {
        const statusUrl = `${PHONEPE_CONFIG.statusEndpoint}/${PHONEPE_CONFIG.merchantId}/${txnId}`;
        const checksum = generateChecksum('', `/pg/v1/status/${PHONEPE_CONFIG.merchantId}/${txnId}`);

        const response = await fetch(statusUrl, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'X-VERIFY': checksum,
            'X-MERCHANT-ID': PHONEPE_CONFIG.merchantId
          }
        });

        const data: any = await response.json();

        if (data.code === 'PAYMENT_SUCCESS' && (paymentWithSub as any).status !== 'completed') {
          // Update payment
          await db.updatePayment(txnId, {
            status: 'completed',
            phonepe_response: data
          });

          const subscriptionId = (paymentWithSub as any)?.subscription_id || (paymentWithSub as any)?.subscription?.id;
          if (subscriptionId) {
            await db.activateSubscription(subscriptionId);
          }

          await db.markOnboardingCompleted(userId);

          return res.json({
            status: 'completed',
            plan,
            amount
          });
        }
      } catch (apiError) {
        console.error('PhonePe status check error:', apiError);
      }
    }

    res.json({
      status: (paymentWithSub as any).status,
      plan,
      amount
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/payments/verify
 * Verify and complete payment (called from callback page)
 */
router.post('/verify', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { txnId, mock } = req.body;

    if (!txnId) {
      return res.status(400).json({ error: 'Transaction ID required' });
    }

    const { data: paymentWithSub, error } = await db.getPaymentWithSubscriptionAndPlan(txnId);

    if (error || !paymentWithSub) {
      return res.status(404).json({ error: 'Payment not found' });
    }

    const { data: currentOrgId, error: orgError } = await db.getOrCreateCurrentOrgId(userId);
    if (orgError || !currentOrgId) {
      return res.status(500).json({ error: 'Failed to resolve organization' });
    }

    // Verify ownership
    if ((paymentWithSub as any).organization_id !== currentOrgId) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const planCode = (paymentWithSub as any)?.subscription?.plan?.code;
    const plan = planCode ? db.mapDbPlanCodeToFrontendPlan(planCode) : 'free';
    const amount = (paymentWithSub as any).amount_paise;
    const subscriptionId = (paymentWithSub as any)?.subscription_id || (paymentWithSub as any)?.subscription?.id;

    // If already completed
    if ((paymentWithSub as any).status === 'completed') {
      return res.json({
        success: true,
        status: 'completed',
        plan,
        message: 'Payment already verified'
      });
    }

    // Handle mock payment (for testing)
    if (mock === true || mock === 'true') {
      await db.updatePayment(txnId, {
        status: 'completed',
      });

      if (subscriptionId) {
        await db.activateSubscription(subscriptionId);
      }
      await db.markOnboardingCompleted(userId);

      return res.json({
        success: true,
        status: 'completed',
        plan,
        mock: true
      });
    }

    if (!PHONEPE_CONFIG.merchantId || !PHONEPE_CONFIG.saltKey) {
      // allow Standard Checkout to verify without legacy salt keys
      if (!isPhonePeStandardConfigured()) {
        return res.status(500).json({ error: 'Payment gateway not configured' });
      }
    }

    // Standard Checkout verify (preferred)
    if (isPhonePeStandardConfigured()) {
      try {
        const token = await getPhonePeStandardAuthToken();
        const url = `${PHONEPE_STANDARD_CONFIG.checkoutOrderStatusBase}/${txnId}/status?details=false`;
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `O-Bearer ${token}`
          }
        });

        const data: any = await response.json();
        const state: PhonePeCheckoutState | undefined = data?.state;

        if (state === 'COMPLETED') {
          await db.updatePayment(txnId, {
            status: 'completed',
            provider_payment_id: data?.orderId || undefined
          });

          if (subscriptionId) {
            await db.activateSubscription(subscriptionId);
          }
          await db.markOnboardingCompleted(userId);

          return res.json({
            success: true,
            status: 'completed',
            plan
          });
        }

        if (state === 'PENDING') {
          return res.json({
            success: false,
            status: 'pending',
            message: 'Payment is still being processed'
          });
        }

        if (state === 'FAILED') {
          return res.json({
            success: false,
            status: 'failed',
            message: 'Payment failed'
          });
        }
      } catch (apiError: any) {
        console.error('PhonePe Standard verification error:', apiError);
      }
    }

    // For real payments, check with PhonePe
    if (PHONEPE_CONFIG.merchantId && PHONEPE_CONFIG.saltKey) {
      try {
        const statusUrl = `${PHONEPE_CONFIG.statusEndpoint}/${PHONEPE_CONFIG.merchantId}/${txnId}`;
        const checksum = generateChecksum('', `/pg/v1/status/${PHONEPE_CONFIG.merchantId}/${txnId}`);

        const response = await fetch(statusUrl, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'X-VERIFY': checksum,
            'X-MERCHANT-ID': PHONEPE_CONFIG.merchantId
          }
        });

        const data: any = await response.json();

        if (data.code === 'PAYMENT_SUCCESS') {
          await db.updatePayment(txnId, {
            status: 'completed',
            phonepe_response: data
          });

          if (subscriptionId) {
            await db.activateSubscription(subscriptionId);
          }
          await db.markOnboardingCompleted(userId);

          return res.json({
            success: true,
            status: 'completed',
            plan
          });
        }

        if (data.code === 'PAYMENT_PENDING') {
          return res.json({
            success: false,
            status: 'pending',
            message: 'Payment is still being processed'
          });
        }

        return res.json({
          success: false,
          status: 'failed',
          message: data.message || 'Payment failed'
        });

      } catch (apiError: any) {
        console.error('PhonePe verification error:', apiError);
      }
    }

    // Return current status
    res.json({
      success: (paymentWithSub as any).status === 'completed',
      status: (paymentWithSub as any).status,
      plan
    });

  } catch (err: any) {
    console.error('Payment verification error:', err);
    res.status(500).json({ error: err.message });
  }
});

export default router;
