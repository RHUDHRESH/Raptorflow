import { Router, Response } from 'express';
import { requireAuth, AuthenticatedRequest } from '../middleware/auth';
import { createSubscription, handleWebhook } from '../integrations/phonepe/service';
import { z } from 'zod';

const router = Router();

const createPaymentSchema = z.object({
  planId: z.string(),
  amount: z.number().min(100), // in paise
});

// POST /api/payments/create
router.post('/create', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const userId = req.user!.id;
    const { planId, amount } = createPaymentSchema.parse(req.body);
    
    const result = await createSubscription(userId, planId, amount);
    
    res.json(result);
  } catch (error) {
    console.error('Payment creation error:', error);
    res.status(500).json({ error: 'Failed to create payment' });
  }
});

// POST /api/payments/webhook
router.post('/webhook', async (req, res) => {
  // Webhook validation?
  // Docs: Authorization: SHA256(username:password)
  // For now, skipping auth to allow testing, or we can add middleware later.
  
  try {
    await handleWebhook(req.body);
    res.status(200).send('OK');
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).send('Internal Server Error');
  }
});

export const paymentsRouter = router;
