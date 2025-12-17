// ═══════════════════════════════════════════════════════════════════════════════
// CANONICAL PLANS CONFIG - Single Source of Truth
// Used by: Landing pricing, /pricing page, Billing page, entitlement checks
// ═══════════════════════════════════════════════════════════════════════════════

export type PlanId = 'ascent' | 'glide' | 'soar'

export interface PlanEntitlements {
    active_campaign_limit: number
    moves_monthly_limit: number
    muse_generations_monthly: number
    radar_scans_per_day: number
    lab_duels_monthly: number
    seats: number
}

export interface Plan {
    id: PlanId
    name: string
    tagline: string
    price: number // INR per month
    priceDisplay: string
    entitlements: PlanEntitlements
    recommended?: boolean
    features: string[]
}

export const PLANS: Record<PlanId, Plan> = {
    ascent: {
        id: 'ascent',
        name: 'Ascent',
        tagline: 'For solo founders getting started',
        price: 5000,
        priceDisplay: '₹5,000',
        entitlements: {
            active_campaign_limit: 3,
            moves_monthly_limit: 20,
            muse_generations_monthly: 60,
            radar_scans_per_day: 3,
            lab_duels_monthly: 8,
            seats: 1
        },
        features: [
            '3 active campaigns',
            '20 moves/month',
            '60 Muse generations',
            'Matrix access',
            'Email support'
        ]
    },
    glide: {
        id: 'glide',
        name: 'Glide',
        tagline: 'For growing teams scaling up',
        price: 7000,
        priceDisplay: '₹7,000',
        recommended: true,
        entitlements: {
            active_campaign_limit: 6,
            moves_monthly_limit: 60,
            muse_generations_monthly: 200,
            radar_scans_per_day: 6,
            lab_duels_monthly: 25,
            seats: 2
        },
        features: [
            '6 active campaigns',
            '60 moves/month',
            '200 Muse generations',
            'Matrix access',
            'Lab (A/B duels)',
            'Priority support',
            '2 team seats'
        ]
    },
    soar: {
        id: 'soar',
        name: 'Soar',
        tagline: 'For agencies and power users',
        price: 10000,
        priceDisplay: '₹10,000',
        entitlements: {
            active_campaign_limit: 9,
            moves_monthly_limit: 150,
            muse_generations_monthly: 700,
            radar_scans_per_day: 15,
            lab_duels_monthly: 80,
            seats: 5
        },
        features: [
            '9 active campaigns',
            '150 moves/month',
            '700 Muse generations',
            'Matrix access',
            'Lab (A/B duels)',
            'Radar intelligence',
            'Dedicated support',
            '5 team seats'
        ]
    }
}

// Helper to get plan by ID
export const getPlan = (id: PlanId): Plan => PLANS[id]

// Comparison table data
export const COMPARISON_FEATURES = [
    {
        category: 'Campaigns',
        features: [
            { name: 'Active Campaigns', ascent: '3', glide: '6', soar: '9' },
            { name: 'Moves/month', ascent: '20', glide: '60', soar: '150' }
        ]
    },
    {
        category: 'Execution',
        features: [
            { name: 'Muse generations/mo', ascent: '60', glide: '200', soar: '700' },
            { name: 'Matrix access', ascent: true, glide: true, soar: true }
        ]
    },
    {
        category: 'Intelligence',
        features: [
            { name: 'Radar scans/day', ascent: '3', glide: '6', soar: '15' },
            { name: 'Lab duels/month', ascent: '8', glide: '25', soar: '80' }
        ]
    },
    {
        category: 'Team',
        features: [
            { name: 'Team seats', ascent: '1', glide: '2', soar: '5' }
        ]
    },
    {
        category: 'Support',
        features: [
            { name: 'Support level', ascent: 'Email', glide: 'Priority', soar: 'Dedicated' }
        ]
    }
]

// Plan IDs in display order
export const PLAN_ORDER: PlanId[] = ['ascent', 'glide', 'soar']
