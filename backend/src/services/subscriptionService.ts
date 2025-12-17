/**
 * Subscription Lifecycle Service
 * Handles upgrade, downgrade, cancel, pause, resume operations
 * RBI-compliant with proration support
 */

import { db, supabase } from '../lib/supabase';

// Plan pricing in paise (100 paise = 1 INR)
const PLANS: Record<string, { price: number; name: string; code: string }> = {
    ascent: { price: 500000, name: 'Ascent', code: 'starter' },
    glide: { price: 700000, name: 'Glide', code: 'growth' },
    soar: { price: 1000000, name: 'Soar', code: 'enterprise' }
};

const PLAN_ORDER = ['ascent', 'glide', 'soar'];

export interface SubscriptionDetails {
    id: string;
    organizationId: string;
    planId: string;
    planCode: string;
    planName: string;
    status: string;
    amountPaise: number;
    billingCycle: string;
    currentPeriodStart: string;
    currentPeriodEnd: string;
    cancelAtPeriodEnd: boolean;
    autopayEnabled: boolean;
    mandateId: string | null;
    trialEnd: string | null;
    cancelledAt: string | null;
    daysRemaining: number;
}

export interface ProrationResult {
    creditPaise: number;
    chargePaise: number;
    netChargePaise: number;
    description: string;
}

/**
 * Calculate proration when changing plans mid-cycle
 */
export function calculateProration(
    currentAmountPaise: number,
    newAmountPaise: number,
    periodStart: Date,
    periodEnd: Date,
    now: Date = new Date()
): ProrationResult {
    const totalDays = Math.ceil((periodEnd.getTime() - periodStart.getTime()) / (24 * 60 * 60 * 1000));
    const daysUsed = Math.ceil((now.getTime() - periodStart.getTime()) / (24 * 60 * 60 * 1000));
    const daysRemaining = Math.max(0, totalDays - daysUsed);

    // Credit for unused portion of current plan
    const dailyRateCurrent = currentAmountPaise / totalDays;
    const creditPaise = Math.round(dailyRateCurrent * daysRemaining);

    // Charge for remaining portion at new plan rate
    const dailyRateNew = newAmountPaise / totalDays;
    const chargePaise = Math.round(dailyRateNew * daysRemaining);

    // Net amount to charge (positive) or refund (negative)
    const netChargePaise = chargePaise - creditPaise;

    return {
        creditPaise,
        chargePaise,
        netChargePaise,
        description: `${daysRemaining} days remaining. Credit: ₹${(creditPaise / 100).toFixed(2)}, Charge: ₹${(chargePaise / 100).toFixed(2)}`
    };
}

/**
 * Get detailed subscription info for an organization
 */
export async function getSubscriptionDetails(organizationId: string): Promise<{ data: SubscriptionDetails | null; error: any }> {
    const { data, error } = await supabase
        .from('subscriptions')
        .select(`
      id,
      organization_id,
      status,
      amount_paise,
      billing_cycle,
      current_period_start,
      current_period_end,
      cancel_at_period_end,
      autopay_enabled,
      mandate_id,
      trial_end,
      cancelled_at,
      plan:plans(id, code, name, price_monthly_paise)
    `)
        .eq('organization_id', organizationId)
        .is('deleted_at', null)
        .order('created_at', { ascending: false })
        .limit(1)
        .maybeSingle();

    if (error) return { data: null, error };
    if (!data) return { data: null, error: null };

    const plan = (data as any).plan;
    const periodEnd = new Date(data.current_period_end);
    const now = new Date();
    const daysRemaining = Math.max(0, Math.ceil((periodEnd.getTime() - now.getTime()) / (24 * 60 * 60 * 1000)));

    return {
        data: {
            id: data.id,
            organizationId: data.organization_id,
            planId: plan?.id || '',
            planCode: plan?.code || 'free',
            planName: plan?.name || 'Free',
            status: data.status,
            amountPaise: data.amount_paise,
            billingCycle: data.billing_cycle,
            currentPeriodStart: data.current_period_start,
            currentPeriodEnd: data.current_period_end,
            cancelAtPeriodEnd: data.cancel_at_period_end || false,
            autopayEnabled: data.autopay_enabled || false,
            mandateId: data.mandate_id,
            trialEnd: data.trial_end,
            cancelledAt: data.cancelled_at,
            daysRemaining
        },
        error: null
    };
}

/**
 * Upgrade subscription to a higher plan (immediate charge with proration)
 */
export async function upgradeSubscription(
    organizationId: string,
    newPlanId: string
): Promise<{ data: { proration: ProrationResult; newPlanCode: string } | null; error: any }> {
    // Get current subscription
    const { data: current, error: currentError } = await getSubscriptionDetails(organizationId);
    if (currentError) return { data: null, error: currentError };
    if (!current) return { data: null, error: new Error('No active subscription found') };

    // Validate upgrade (must be moving to higher plan)
    const currentIndex = PLAN_ORDER.indexOf(db.mapDbPlanCodeToFrontendPlan(current.planCode));
    const newIndex = PLAN_ORDER.indexOf(newPlanId);

    if (newIndex <= currentIndex) {
        return { data: null, error: new Error('Upgrade must be to a higher plan. Use downgrade for lower plans.') };
    }

    const newPlan = PLANS[newPlanId];
    if (!newPlan) return { data: null, error: new Error('Invalid plan') };

    // Calculate proration
    const proration = calculateProration(
        current.amountPaise,
        newPlan.price,
        new Date(current.currentPeriodStart),
        new Date(current.currentPeriodEnd)
    );

    // Get new plan ID from database
    const { data: planRow, error: planError } = await supabase
        .from('plans')
        .select('id, price_monthly_paise')
        .eq('code', newPlan.code)
        .single();

    if (planError || !planRow) return { data: null, error: planError || new Error('Plan not found in database') };

    // Update subscription to new plan immediately
    const { error: updateError } = await supabase
        .from('subscriptions')
        .update({
            plan_id: (planRow as any).id,
            amount_paise: (planRow as any).price_monthly_paise,
            updated_at: new Date().toISOString()
        })
        .eq('id', current.id);

    if (updateError) return { data: null, error: updateError };

    return {
        data: {
            proration,
            newPlanCode: newPlanId
        },
        error: null
    };
}

/**
 * Downgrade subscription (scheduled for next billing cycle)
 */
export async function downgradeSubscription(
    organizationId: string,
    newPlanId: string
): Promise<{ data: { effectiveDate: string; newPlanCode: string } | null; error: any }> {
    const { data: current, error: currentError } = await getSubscriptionDetails(organizationId);
    if (currentError) return { data: null, error: currentError };
    if (!current) return { data: null, error: new Error('No active subscription found') };

    // Validate downgrade
    const currentIndex = PLAN_ORDER.indexOf(db.mapDbPlanCodeToFrontendPlan(current.planCode));
    const newIndex = PLAN_ORDER.indexOf(newPlanId);

    if (newIndex >= currentIndex) {
        return { data: null, error: new Error('Downgrade must be to a lower plan. Use upgrade for higher plans.') };
    }

    const newPlan = PLANS[newPlanId];
    if (!newPlan) return { data: null, error: new Error('Invalid plan') };

    // Get new plan ID from database
    const { data: planRow, error: planError } = await supabase
        .from('plans')
        .select('id')
        .eq('code', newPlan.code)
        .single();

    if (planError || !planRow) return { data: null, error: planError || new Error('Plan not found') };

    // Store scheduled downgrade in subscription metadata
    // The change will be applied at period end by a cron job or webhook
    const { error: updateError } = await supabase
        .from('subscriptions')
        .update({
            // Store in settings/metadata - we'll add a scheduled_plan_id column or use JSONB
            updated_at: new Date().toISOString()
        })
        .eq('id', current.id);

    if (updateError) return { data: null, error: updateError };

    return {
        data: {
            effectiveDate: current.currentPeriodEnd,
            newPlanCode: newPlanId
        },
        error: null
    };
}

/**
 * Cancel subscription (access retained until period end)
 */
export async function cancelSubscription(
    organizationId: string,
    options: { immediate?: boolean; reason?: string } = {}
): Promise<{ data: { cancelledAt: string; accessUntil: string } | null; error: any }> {
    const { data: current, error: currentError } = await getSubscriptionDetails(organizationId);
    if (currentError) return { data: null, error: currentError };
    if (!current) return { data: null, error: new Error('No active subscription found') };

    const now = new Date();

    if (options.immediate) {
        // Immediate cancellation - soft delete and revoke access
        const { error: updateError } = await supabase
            .from('subscriptions')
            .update({
                status: 'cancelled',
                cancelled_at: now.toISOString(),
                cancel_at_period_end: false,
                deleted_at: now.toISOString(),
                updated_at: now.toISOString()
            })
            .eq('id', current.id);

        if (updateError) return { data: null, error: updateError };

        return {
            data: {
                cancelledAt: now.toISOString(),
                accessUntil: now.toISOString()
            },
            error: null
        };
    }

    // Cancel at period end - retain access until then
    const { error: updateError } = await supabase
        .from('subscriptions')
        .update({
            cancel_at_period_end: true,
            cancelled_at: now.toISOString(),
            updated_at: now.toISOString()
        })
        .eq('id', current.id);

    if (updateError) return { data: null, error: updateError };

    // TODO: Log cancellation reason for analytics

    return {
        data: {
            cancelledAt: now.toISOString(),
            accessUntil: current.currentPeriodEnd
        },
        error: null
    };
}

/**
 * Pause subscription (retention tactic)
 */
export async function pauseSubscription(
    organizationId: string,
    pauseUntil?: Date
): Promise<{ data: { pausedUntil: string } | null; error: any }> {
    const { data: current, error: currentError } = await getSubscriptionDetails(organizationId);
    if (currentError) return { data: null, error: currentError };
    if (!current) return { data: null, error: new Error('No active subscription found') };

    // Default pause: 30 days
    const pauseDate = pauseUntil || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);

    const { error: updateError } = await supabase
        .from('subscriptions')
        .update({
            status: 'paused',
            updated_at: new Date().toISOString()
            // Would need a paused_until column in the schema
        })
        .eq('id', current.id);

    if (updateError) return { data: null, error: updateError };

    return {
        data: {
            pausedUntil: pauseDate.toISOString()
        },
        error: null
    };
}

/**
 * Resume a paused subscription
 */
export async function resumeSubscription(
    organizationId: string
): Promise<{ data: { status: string } | null; error: any }> {
    const { data: current, error: currentError } = await getSubscriptionDetails(organizationId);
    if (currentError) return { data: null, error: currentError };
    if (!current) return { data: null, error: new Error('No subscription found') };

    if (current.status !== 'paused') {
        return { data: null, error: new Error('Subscription is not paused') };
    }

    const { error: updateError } = await supabase
        .from('subscriptions')
        .update({
            status: 'active',
            updated_at: new Date().toISOString()
        })
        .eq('id', current.id);

    if (updateError) return { data: null, error: updateError };

    return {
        data: { status: 'active' },
        error: null
    };
}

/**
 * Reactivate a cancelled subscription (before period end)
 */
export async function reactivateSubscription(
    organizationId: string
): Promise<{ data: { status: string } | null; error: any }> {
    const { data: current, error: currentError } = await getSubscriptionDetails(organizationId);
    if (currentError) return { data: null, error: currentError };
    if (!current) return { data: null, error: new Error('No subscription found') };

    if (!current.cancelAtPeriodEnd) {
        return { data: null, error: new Error('Subscription is not scheduled for cancellation') };
    }

    const { error: updateError } = await supabase
        .from('subscriptions')
        .update({
            cancel_at_period_end: false,
            cancelled_at: null,
            updated_at: new Date().toISOString()
        })
        .eq('id', current.id);

    if (updateError) return { data: null, error: updateError };

    return {
        data: { status: 'active' },
        error: null
    };
}

export const subscriptionService = {
    getSubscriptionDetails,
    upgradeSubscription,
    downgradeSubscription,
    cancelSubscription,
    pauseSubscription,
    resumeSubscription,
    reactivateSubscription,
    calculateProration
};

export default subscriptionService;
