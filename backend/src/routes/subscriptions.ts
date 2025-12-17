/**
 * Subscription Routes
 * API endpoints for subscription lifecycle management
 */

import { Router, Request, Response } from 'express';
import { supabase, db } from '../lib/supabase';
import {
    subscriptionService,
    getSubscriptionDetails,
    upgradeSubscription,
    downgradeSubscription,
    cancelSubscription,
    pauseSubscription,
    resumeSubscription,
    reactivateSubscription,
    calculateProration
} from '../services/subscriptionService';

const router = Router();

// Middleware to verify JWT token and get user
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

// Helper to get organization ID for authenticated user
async function getOrgId(userId: string, userEmail?: string): Promise<{ orgId: string | null; error: any }> {
    const { data, error } = await db.getOrCreateCurrentOrgId(userId, userEmail);
    return { orgId: data, error };
}

/**
 * GET /api/subscriptions/current
 * Get current subscription details for the authenticated user's organization
 */
router.get('/current', verifyToken, async (req: Request, res: Response) => {
    try {
        const userId = (req as any).user.id;
        const userEmail = (req as any).user.email;

        const { orgId, error: orgError } = await getOrgId(userId, userEmail);
        if (orgError || !orgId) {
            return res.status(500).json({ error: 'Failed to get organization' });
        }

        const { data, error } = await getSubscriptionDetails(orgId);
        if (error) {
            return res.status(500).json({ error: error.message });
        }

        if (!data) {
            return res.json({
                subscription: null,
                message: 'No active subscription'
            });
        }

        res.json({ subscription: data });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

/**
 * POST /api/subscriptions/preview-upgrade
 * Preview proration for an upgrade (no charge yet)
 */
router.post('/preview-upgrade', verifyToken, async (req: Request, res: Response) => {
    try {
        const userId = (req as any).user.id;
        const { planId } = req.body;

        if (!planId) {
            return res.status(400).json({ error: 'planId is required' });
        }

        const { orgId, error: orgError } = await getOrgId(userId);
        if (orgError || !orgId) {
            return res.status(500).json({ error: 'Failed to get organization' });
        }

        const { data: current, error } = await getSubscriptionDetails(orgId);
        if (error) {
            return res.status(500).json({ error: error.message });
        }

        if (!current) {
            return res.status(400).json({ error: 'No active subscription to upgrade' });
        }

        // Plan prices
        const PLANS: Record<string, number> = {
            ascent: 500000,
            glide: 700000,
            soar: 1000000
        };

        const newPrice = PLANS[planId];
        if (!newPrice) {
            return res.status(400).json({ error: 'Invalid plan' });
        }

        const proration = calculateProration(
            current.amountPaise,
            newPrice,
            new Date(current.currentPeriodStart),
            new Date(current.currentPeriodEnd)
        );

        res.json({
            currentPlan: current.planCode,
            newPlan: planId,
            proration,
            totalDue: proration.netChargePaise,
            totalDueDisplay: `₹${(proration.netChargePaise / 100).toFixed(2)}`
        });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

/**
 * POST /api/subscriptions/upgrade
 * Upgrade to a higher plan (immediate proration charge)
 */
router.post('/upgrade', verifyToken, async (req: Request, res: Response) => {
    try {
        const userId = (req as any).user.id;
        const { planId } = req.body;

        if (!planId) {
            return res.status(400).json({ error: 'planId is required' });
        }

        const { orgId, error: orgError } = await getOrgId(userId);
        if (orgError || !orgId) {
            return res.status(500).json({ error: 'Failed to get organization' });
        }

        const { data, error } = await upgradeSubscription(orgId, planId);
        if (error) {
            return res.status(400).json({ error: error.message });
        }

        res.json({
            success: true,
            message: 'Subscription upgraded successfully',
            ...data
        });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

/**
 * POST /api/subscriptions/downgrade
 * Schedule downgrade for next billing cycle
 */
router.post('/downgrade', verifyToken, async (req: Request, res: Response) => {
    try {
        const userId = (req as any).user.id;
        const { planId } = req.body;

        if (!planId) {
            return res.status(400).json({ error: 'planId is required' });
        }

        const { orgId, error: orgError } = await getOrgId(userId);
        if (orgError || !orgId) {
            return res.status(500).json({ error: 'Failed to get organization' });
        }

        const { data, error } = await downgradeSubscription(orgId, planId);
        if (error) {
            return res.status(400).json({ error: error.message });
        }

        res.json({
            success: true,
            message: `Downgrade scheduled. New plan will be active from ${data?.effectiveDate}`,
            ...data
        });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

/**
 * POST /api/subscriptions/cancel
 * Cancel subscription (retains access until period end by default)
 */
router.post('/cancel', verifyToken, async (req: Request, res: Response) => {
    try {
        const userId = (req as any).user.id;
        const { immediate, reason } = req.body;

        const { orgId, error: orgError } = await getOrgId(userId);
        if (orgError || !orgId) {
            return res.status(500).json({ error: 'Failed to get organization' });
        }

        const { data, error } = await cancelSubscription(orgId, { immediate, reason });
        if (error) {
            return res.status(400).json({ error: error.message });
        }

        res.json({
            success: true,
            message: immediate
                ? 'Subscription cancelled immediately'
                : `Subscription will be cancelled at end of billing period (${data?.accessUntil})`,
            ...data
        });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

/**
 * POST /api/subscriptions/pause
 * Pause subscription (retention tactic)
 */
router.post('/pause', verifyToken, async (req: Request, res: Response) => {
    try {
        const userId = (req as any).user.id;
        const { pauseUntil } = req.body;

        const { orgId, error: orgError } = await getOrgId(userId);
        if (orgError || !orgId) {
            return res.status(500).json({ error: 'Failed to get organization' });
        }

        const pauseDate = pauseUntil ? new Date(pauseUntil) : undefined;
        const { data, error } = await pauseSubscription(orgId, pauseDate);
        if (error) {
            return res.status(400).json({ error: error.message });
        }

        res.json({
            success: true,
            message: `Subscription paused until ${data?.pausedUntil}`,
            ...data
        });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

/**
 * POST /api/subscriptions/resume
 * Resume a paused subscription
 */
router.post('/resume', verifyToken, async (req: Request, res: Response) => {
    try {
        const userId = (req as any).user.id;

        const { orgId, error: orgError } = await getOrgId(userId);
        if (orgError || !orgId) {
            return res.status(500).json({ error: 'Failed to get organization' });
        }

        const { data, error } = await resumeSubscription(orgId);
        if (error) {
            return res.status(400).json({ error: error.message });
        }

        res.json({
            success: true,
            message: 'Subscription resumed',
            ...data
        });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

/**
 * POST /api/subscriptions/reactivate
 * Reactivate a subscription scheduled for cancellation
 */
router.post('/reactivate', verifyToken, async (req: Request, res: Response) => {
    try {
        const userId = (req as any).user.id;

        const { orgId, error: orgError } = await getOrgId(userId);
        if (orgError || !orgId) {
            return res.status(500).json({ error: 'Failed to get organization' });
        }

        const { data, error } = await reactivateSubscription(orgId);
        if (error) {
            return res.status(400).json({ error: error.message });
        }

        res.json({
            success: true,
            message: 'Cancellation reversed, subscription is active',
            ...data
        });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

export default router;
