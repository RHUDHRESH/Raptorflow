import { Router, Request, Response } from 'express';
import crypto from 'crypto';
import { db, supabase } from '../lib/supabase';
import { env } from '../config/env';

const router = Router();

/**
 * PhonePe Configuration
 * Documentation: https://developer.phonepe.com/v1/docs/api-integration
 */
const PHONEPE_CONFIG = {
  merchantId: env.PHONEPE_MERCHANT_ID || '',
  saltKey: env.PHONEPE_SALT_KEY || '',
  saltIndex: '1',
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

// Plan pricing (in paise - 100 paise = 1 INR)
const PLANS: Record<string, { price: number; name: string; cohorts: number }> = {
  starter: { price: 9900, name: 'Starter', cohorts: 2 },      // ₹99
  growth: { price: 24900, name: 'Growth', cohorts: 5 },       // ₹249
  scale: { price: 49900, name: 'Scale', cohorts: 10 },        // ₹499
  ascent: { price: 500000, name: 'Ascent', cohorts: 3 },      // ₹5,000
  glide: { price: 700000, name: 'Glide', cohorts: 5 },        // ₹7,000
  soar: { price: 1000000, name: 'Soar', cohorts: 10 }         // ₹10,000
};

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
function verifyChecksum(response: string, receivedChecksum: string): boolean {
  const expectedChecksum = generateChecksum(response, '/pg/v1/status');
  return receivedChecksum === expectedChecksum;
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
    priceDisplay: `₹${(plan.price / 100).toLocaleString('en-IN')}`,
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
    const { plan, phone } = req.body;

    // Validate plan
    if (!plan || !PLANS[plan]) {
      return res.status(400).json({ error: 'Invalid plan selected' });
    }

    const planDetails = PLANS[plan];
    
    // Generate unique transaction ID
    const txnId = `RF${Date.now()}${crypto.randomBytes(4).toString('hex').toUpperCase()}`;
    
    // Create payment record in database
    const { data: payment, error: dbError } = await db.createPayment(
      userId, 
      plan, 
      planDetails.price, 
      txnId
    );

    if (dbError) {
      console.error('DB Error creating payment:', dbError);
      return res.status(500).json({ error: 'Failed to create payment record' });
    }

    // Frontend URL for redirect
    const frontendUrl = env.FRONTEND_PUBLIC_URL || 'http://localhost:5173';

    // Build PhonePe payload
    const payload = {
      merchantId: PHONEPE_CONFIG.merchantId,
      merchantTransactionId: txnId,
      merchantUserId: userId,
      amount: planDetails.price, // Amount in paise
      redirectUrl: `${frontendUrl}/payment/callback?txnId=${txnId}`,
      redirectMode: 'REDIRECT',
      callbackUrl: `${frontendUrl}/api/payments/webhook`, // Server callback
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

        const data = await response.json();
        console.log('PhonePe Response:', JSON.stringify(data, null, 2));

        if (data.success && data.data?.instrumentResponse?.redirectInfo?.url) {
          return res.json({
            success: true,
            txnId,
            paymentUrl: data.data.instrumentResponse.redirectInfo.url,
            amount: planDetails.price,
            amountDisplay: `₹${(planDetails.price / 100).toLocaleString('en-IN')}`,
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
      amountDisplay: `₹${(planDetails.price / 100).toLocaleString('en-IN')}`,
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
    
    const { response: encodedResponse } = req.body;
    const xVerify = req.headers['x-verify'] as string;

    if (!encodedResponse) {
      return res.status(400).json({ error: 'Missing response payload' });
    }

    // Decode the response
    const decodedResponse = JSON.parse(
      Buffer.from(encodedResponse, 'base64').toString('utf-8')
    );
    
    console.log('Decoded webhook response:', decodedResponse);

    const txnId = decodedResponse.data?.merchantTransactionId;
    const code = decodedResponse.code;

    if (!txnId) {
      return res.status(400).json({ error: 'Missing transaction ID' });
    }

    // Handle different payment statuses
    if (code === 'PAYMENT_SUCCESS') {
      // Update payment status
      await db.updatePayment(txnId, {
        status: 'completed',
        completed_at: new Date().toISOString(),
        phonepe_transaction_id: decodedResponse.data?.transactionId,
        phonepe_response: decodedResponse
      });

      // Get payment details and activate plan
      const { data: payment } = await db.getPayment(txnId);
      
      if (payment) {
        await db.activatePlan(
          payment.user_id,
          payment.plan,
          payment.id,
          payment.amount
        );

        // Mark onboarding as complete
        await db.updateProfile(payment.user_id, {
          onboarding_completed: true,
          onboarding_completed_at: new Date().toISOString()
        });
      }

      console.log('Payment successful for txn:', txnId);

    } else if (code === 'PAYMENT_PENDING') {
      await db.updatePayment(txnId, {
        status: 'pending',
        phonepe_response: decodedResponse
      });
    } else {
      // Failed or other status
      await db.updatePayment(txnId, {
        status: 'failed',
        error: code,
        phonepe_response: decodedResponse
      });
    }

    res.json({ status: 'ok' });
  } catch (err: any) {
    console.error('Webhook processing error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/payments/status/:txnId
 * Check payment status
 */
router.get('/status/:txnId', async (req: Request, res: Response) => {
  try {
    const { txnId } = req.params;

    // Get from database first
    const { data: payment, error } = await db.getPayment(txnId);

    if (error || !payment) {
      return res.status(404).json({ error: 'Payment not found' });
    }

    // If payment is not completed and we have PhonePe credentials, check with PhonePe
    if (payment.status !== 'completed' && PHONEPE_CONFIG.merchantId && PHONEPE_CONFIG.saltKey) {
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

        const data = await response.json();

        if (data.code === 'PAYMENT_SUCCESS' && payment.status !== 'completed') {
          // Update payment
          await db.updatePayment(txnId, {
            status: 'completed',
            completed_at: new Date().toISOString(),
            phonepe_response: data
          });

          // Activate plan
          await db.activatePlan(payment.user_id, payment.plan, payment.id, payment.amount);

          return res.json({
            status: 'completed',
            plan: payment.plan,
            amount: payment.amount
          });
        }
      } catch (apiError) {
        console.error('PhonePe status check error:', apiError);
      }
    }

    res.json({
      status: payment.status,
      plan: payment.plan,
      amount: payment.amount,
      completedAt: payment.completed_at
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

    const { data: payment, error } = await db.getPayment(txnId);

    if (error || !payment) {
      return res.status(404).json({ error: 'Payment not found' });
    }

    // Verify ownership
    if (payment.user_id !== userId) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    // If already completed
    if (payment.status === 'completed') {
      return res.json({
        success: true,
        status: 'completed',
        plan: payment.plan,
        message: 'Payment already verified'
      });
    }

    // Handle mock payment (for testing)
    if (mock === true || mock === 'true') {
      await db.updatePayment(txnId, {
        status: 'completed',
        completed_at: new Date().toISOString()
      });

      await db.activatePlan(userId, payment.plan, payment.id, payment.amount);

      await db.updateProfile(userId, {
        onboarding_completed: true,
        onboarding_completed_at: new Date().toISOString()
      });

      return res.json({
        success: true,
        status: 'completed',
        plan: payment.plan,
        mock: true
      });
    }

    // For real payments, check with PhonePe
    if (PHONEPE_CONFIG.merchantId && PHONEPE_CONFIG.saltKey) {
      try {
        const statusUrl = `${PHONEPE_CONFIG.statusEndpoint}/${PHONEPE_CONFIG.merchantId}/${txnId}`;
        const stringToHash = `/pg/v1/status/${PHONEPE_CONFIG.merchantId}/${txnId}${PHONEPE_CONFIG.saltKey}`;
        const checksum = crypto.createHash('sha256').update(stringToHash).digest('hex') + '###' + PHONEPE_CONFIG.saltIndex;

        const response = await fetch(statusUrl, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'X-VERIFY': checksum,
            'X-MERCHANT-ID': PHONEPE_CONFIG.merchantId
          }
        });

        const data = await response.json();

        if (data.code === 'PAYMENT_SUCCESS') {
          await db.updatePayment(txnId, {
            status: 'completed',
            completed_at: new Date().toISOString(),
            phonepe_response: data
          });

          await db.activatePlan(userId, payment.plan, payment.id, payment.amount);

          await db.updateProfile(userId, {
            onboarding_completed: true,
            onboarding_completed_at: new Date().toISOString()
          });

          return res.json({
            success: true,
            status: 'completed',
            plan: payment.plan
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
      success: payment.status === 'completed',
      status: payment.status,
      plan: payment.plan
    });

  } catch (err: any) {
    console.error('Payment verification error:', err);
    res.status(500).json({ error: err.message });
  }
});

export default router;
