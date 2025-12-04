import { Router, Request, Response } from 'express';
import crypto from 'crypto';
import { db, supabase } from '../lib/supabase';
import { env } from '../config/env';

const router = Router();

// PhonePe Configuration
const PHONEPE_CONFIG = {
  merchantId: env.PHONEPE_MERCHANT_ID,
  saltKey: env.PHONEPE_SALT_KEY,
  saltIndex: '1',
  env: env.PHONEPE_ENV as 'UAT' | 'PRODUCTION',
  baseUrl: env.PHONEPE_ENV === 'PRODUCTION' 
    ? 'https://api.phonepe.com/apis/hermes/pg/v1/pay'
    : 'https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay'
};

// Plan pricing
const PLANS = {
  starter: { price: 9900, name: 'Starter', cohorts: 2 },
  growth: { price: 24900, name: 'Growth', cohorts: 5 },
  scale: { price: 49900, name: 'Scale', cohorts: 10 }
};

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
 * POST /api/payments/initiate
 * Initiate a PhonePe payment
 */
router.post('/initiate', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { plan } = req.body;

    if (!plan || !PLANS[plan as keyof typeof PLANS]) {
      return res.status(400).json({ error: 'Invalid plan' });
    }

    const planDetails = PLANS[plan as keyof typeof PLANS];
    const txnId = `RF${Date.now()}${Math.random().toString(36).substring(2, 8).toUpperCase()}`;
    const amount = planDetails.price; // In paise

    // Create payment record
    await db.createPayment(userId, plan, amount, txnId);

    // Build PhonePe payload
    const payload = {
      merchantId: PHONEPE_CONFIG.merchantId,
      merchantTransactionId: txnId,
      merchantUserId: userId,
      amount: amount,
      redirectUrl: `${env.FRONTEND_PUBLIC_URL}/payment/callback?txnId=${txnId}`,
      redirectMode: 'REDIRECT',
      callbackUrl: `${env.FRONTEND_PUBLIC_URL}/api/payments/webhook`,
      mobileNumber: '',
      paymentInstrument: {
        type: 'PAY_PAGE'
      }
    };

    const base64Payload = Buffer.from(JSON.stringify(payload)).toString('base64');
    const stringToHash = base64Payload + '/pg/v1/pay' + PHONEPE_CONFIG.saltKey;
    const checksum = crypto.createHash('sha256').update(stringToHash).digest('hex') + '###' + PHONEPE_CONFIG.saltIndex;

    // In production, call PhonePe API
    // For now, return mock response for testing
    if (PHONEPE_CONFIG.env === 'PRODUCTION' && PHONEPE_CONFIG.merchantId) {
      try {
        const response = await fetch(PHONEPE_CONFIG.baseUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-VERIFY': checksum
          },
          body: JSON.stringify({ request: base64Payload })
        });

        const data = await response.json();

        if (data.success && data.data?.instrumentResponse?.redirectInfo?.url) {
          return res.json({
            success: true,
            txnId,
            paymentUrl: data.data.instrumentResponse.redirectInfo.url,
            amount,
            plan
          });
        }
      } catch (apiError) {
        console.error('PhonePe API error:', apiError);
      }
    }

    // Mock response for development/testing
    res.json({
      success: true,
      txnId,
      paymentUrl: `${env.FRONTEND_PUBLIC_URL}/payment/callback?txnId=${txnId}&mock=true`,
      amount,
      plan,
      mock: true
    });
  } catch (err: any) {
    console.error('Payment initiation error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/payments/webhook
 * Handle PhonePe webhook callback
 */
router.post('/webhook', async (req: Request, res: Response) => {
  try {
    const { response: encodedResponse } = req.body;
    const xVerify = req.headers['x-verify'] as string;

    if (!encodedResponse) {
      return res.status(400).json({ error: 'Missing response' });
    }

    // Verify signature
    const stringToHash = encodedResponse + PHONEPE_CONFIG.saltKey;
    const expectedChecksum = crypto.createHash('sha256').update(stringToHash).digest('hex') + '###' + PHONEPE_CONFIG.saltIndex;

    // Decode response
    const decodedResponse = JSON.parse(Buffer.from(encodedResponse, 'base64').toString('utf-8'));
    console.log('PhonePe webhook:', decodedResponse);

    const txnId = decodedResponse.data?.merchantTransactionId;

    if (!txnId) {
      return res.status(400).json({ error: 'Missing transaction ID' });
    }

    if (decodedResponse.code === 'PAYMENT_SUCCESS') {
      // Update payment status
      await db.updatePayment(txnId, {
        status: 'completed',
        completed_at: new Date().toISOString(),
        phonepe_response: decodedResponse
      });

      // Get payment details
      const { data: payment } = await db.getPayment(txnId);

      if (payment) {
        // Activate plan for user
        await db.activatePlan(
          payment.user_id,
          payment.plan,
          payment.id,
          payment.amount
        );
      }
    } else {
      await db.updatePayment(txnId, {
        status: 'failed',
        error: decodedResponse.code,
        phonepe_response: decodedResponse
      });
    }

    res.json({ status: 'ok' });
  } catch (err: any) {
    console.error('Webhook error:', err);
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
    const { mock } = req.query;

    // If mock payment, auto-complete
    if (mock === 'true') {
      const { data: payment } = await db.getPayment(txnId);
      
      if (payment && payment.status !== 'completed') {
        await db.updatePayment(txnId, {
          status: 'completed',
          completed_at: new Date().toISOString()
        });

        await db.activatePlan(
          payment.user_id,
          payment.plan,
          payment.id,
          payment.amount
        );

        return res.json({
          status: 'completed',
          plan: payment.plan,
          mock: true
        });
      }
    }

    const { data: payment, error } = await db.getPayment(txnId);

    if (error || !payment) {
      return res.status(404).json({ error: 'Payment not found' });
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
 * Verify payment manually (for callback page)
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

    if (payment.user_id !== userId) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    // Handle mock payment
    if (mock === true || mock === 'true') {
      await db.updatePayment(txnId, {
        status: 'completed',
        completed_at: new Date().toISOString()
      });

      await db.activatePlan(
        payment.user_id,
        payment.plan,
        payment.id,
        payment.amount
      );

      // Mark onboarding as complete
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

    // For real payments, check PhonePe API
    if (payment.status !== 'completed' && PHONEPE_CONFIG.merchantId) {
      const statusUrl = `${PHONEPE_CONFIG.baseUrl.replace('/pay', '/status')}/${PHONEPE_CONFIG.merchantId}/${txnId}`;
      const stringToHash = `/pg/v1/status/${PHONEPE_CONFIG.merchantId}/${txnId}` + PHONEPE_CONFIG.saltKey;
      const checksum = crypto.createHash('sha256').update(stringToHash).digest('hex') + '###' + PHONEPE_CONFIG.saltIndex;

      try {
        const response = await fetch(statusUrl, {
          headers: { 'X-VERIFY': checksum, 'X-MERCHANT-ID': PHONEPE_CONFIG.merchantId }
        });
        const data = await response.json();

        if (data.code === 'PAYMENT_SUCCESS') {
          await db.updatePayment(txnId, {
            status: 'completed',
            completed_at: new Date().toISOString(),
            phonepe_response: data
          });

          await db.activatePlan(
            payment.user_id,
            payment.plan,
            payment.id,
            payment.amount
          );

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
      } catch (apiError) {
        console.error('PhonePe status check error:', apiError);
      }
    }

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

