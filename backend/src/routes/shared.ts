import { Router, Request, Response } from 'express';
import crypto from 'crypto';
import { db, supabase } from '../lib/supabase';

const router = Router();

/**
 * POST /api/shared/create
 * Create a shareable link for sales-assisted onboarding
 */
router.post('/create', async (req: Request, res: Response) => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader?.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Missing authorization' });
    }

    const token = authHeader.split(' ')[1];
    const { data: { user }, error: authError } = await supabase.auth.getUser(token);
    
    if (authError || !user) {
      return res.status(401).json({ error: 'Invalid token' });
    }

    const { intake_id } = req.body;

    if (!intake_id) {
      return res.status(400).json({ error: 'Intake ID required' });
    }

    // Generate unique token
    const shareToken = crypto.randomBytes(24).toString('hex');

    // Create shared link
    const { data, error } = await db.createSharedLink(intake_id, user.id, shareToken);

    if (error) {
      return res.status(500).json({ error: error.message });
    }

    res.json({
      success: true,
      token: shareToken,
      url: `${process.env.FRONTEND_PUBLIC_URL || 'http://localhost:5173'}/shared-view/${shareToken}`,
      expiresAt: data.expires_at
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/shared/:token
 * Get shared intake data (public - no auth required)
 */
router.get('/:token', async (req: Request, res: Response) => {
  try {
    const { token } = req.params;

    const { data, error } = await db.getSharedLink(token);

    if (error || !data) {
      return res.status(404).json({ error: 'Shared link not found or expired' });
    }

    // Check expiry
    if (data.expires_at && new Date(data.expires_at) < new Date()) {
      return res.status(410).json({ error: 'This link has expired' });
    }

    // Return intake data (sanitized for public viewing)
    const intake = data.onboarding_intake;
    
    res.json({
      success: true,
      summary: {
        // Company info
        company: {
          name: intake?.company?.name,
          industry: intake?.company?.industry,
          size: intake?.company?.size,
          website: intake?.company?.website
        },
        // Positioning
        positioning: intake?.positioning_derived ? {
          valueProp: intake.positioning_derived.value_proposition,
          clarityScore: intake.positioning_derived.clarity_score,
          target: intake.positioning_derived.primary_target,
          outcome: intake.positioning_derived.primary_outcome
        } : null,
        // ICPs
        icps: intake?.icps?.filter((icp: any) => icp.selected).map((icp: any) => ({
          label: icp.label,
          summary: icp.summary,
          fitScore: icp.fit_score || icp.fitScore
        })),
        // War Plan summary
        warPlan: intake?.war_plan?.generated ? {
          phases: intake.war_plan.phases?.length || 3,
          summary: intake.war_plan.summary
        } : null,
        // Selected plan
        selectedPlan: intake?.selected_plan,
        paymentStatus: intake?.payment_status
      },
      accessedCount: data.accessed_count,
      salesRepId: data.sales_rep_id,
      paymentCompleted: data.payment_completed
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/shared/:token/payment
 * Initiate payment for shared link (no auth - uses link token)
 */
router.post('/:token/payment', async (req: Request, res: Response) => {
  try {
    const { token } = req.params;
    const { plan, email, phone } = req.body;

    if (!plan) {
      return res.status(400).json({ error: 'Plan is required' });
    }

    const { data: sharedLink, error } = await db.getSharedLink(token);

    if (error || !sharedLink) {
      return res.status(404).json({ error: 'Shared link not found' });
    }

    // Check expiry
    if (sharedLink.expires_at && new Date(sharedLink.expires_at) < new Date()) {
      return res.status(410).json({ error: 'This link has expired' });
    }

    const intake = sharedLink.onboarding_intake;
    if (!intake) {
      return res.status(404).json({ error: 'Intake not found' });
    }

    // Generate transaction ID
    const txnId = `RF${Date.now()}${Math.random().toString(36).substring(2, 8).toUpperCase()}`;

    // Plan prices (in paise)
    const PLANS: Record<string, { price: number; name: string }> = {
      starter: { price: 9900, name: 'Starter' },
      growth: { price: 24900, name: 'Growth' },
      scale: { price: 49900, name: 'Scale' },
      ascent: { price: 500000, name: 'Ascent' },
      glide: { price: 700000, name: 'Glide' },
      soar: { price: 1000000, name: 'Soar' }
    };

    const planDetails = PLANS[plan];
    if (!planDetails) {
      return res.status(400).json({ error: 'Invalid plan' });
    }

    // Create payment record
    await db.createPayment(intake.user_id, plan, planDetails.price, txnId);

    // Update intake with selected plan
    await db.updateIntake(intake.id, {
      selected_plan: plan,
      payment_status: 'initiated'
    });

    // For now, return mock payment URL
    // In production, this would call PhonePe API
    res.json({
      success: true,
      txnId,
      paymentUrl: `${process.env.FRONTEND_PUBLIC_URL || 'http://localhost:5173'}/payment/callback?txnId=${txnId}&shared=${token}&mock=true`,
      amount: planDetails.price,
      plan: planDetails.name
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

export default router;

