import { Target, Zap, Sparkles, BarChart3, Shield, Clock, Users } from 'lucide-react'

export const HERO_STATS = [
    { value: '90', label: 'day war plan' },
    { value: '3x', label: 'execution speed' },
    { value: '∞', label: 'clarity unlocked' }
]

// "Hook Model" aligned - sharper, more aggressive copy
export const FEATURES = [
    {
        step: 1,
        icon: Target,
        title: 'Lock Strategy',
        description: "Define your ICP, positioning, and competitive angle in one session. Know exactly who you're targeting and why they'll choose you.",
        benefit: 'Absolute Clarity',
        details: ['ICP Definition Workshop', 'Competitive Positioning', 'Message-Market Fit']
    },
    {
        step: 2,
        icon: Zap,
        title: 'Launch Attacks',
        description: "Break campaigns into daily Moves—LinkedIn posts, emails, DMs. Each Move has a purpose, a deadline, and tracks back to revenue.",
        benefit: 'Relentless Action',
        details: ['Daily Move Checklists', 'Campaign Timelines', 'Progress Tracking']
    },
    {
        step: 3,
        icon: Sparkles,
        title: 'Generate Ammo',
        description: "Muse AI writes posts, emails, and ad copy in your voice. Get 30+ content pieces ready to fire in minutes, not hours.",
        benefit: 'Infinite Content',
        details: ['AI Content Generation', 'Brand Voice Training', 'Multi-Channel Output']
    },
    {
        step: 4,
        icon: BarChart3,
        title: 'Kill Weakness',
        description: "Black Box tests your headlines, CTAs, and offers automatically. See what converts, cut what doesn't. Data-driven ruthlessness.",
        benefit: 'Auto-Optimization',
        details: ['A/B Testing Engine', 'Conversion Tracking', 'Winner Promotion']
    }
]

export const GUARANTEES = [
    { title: '14-Day Money-Back', description: 'If you don\'t love it, we refund it. Simple.', icon: Shield },
    { title: 'Cancel Anytime', description: 'We earn your business every month.', icon: Clock },
    { title: 'Zero AI Training', description: 'Your data is yours. We don\'t touch it.', icon: Users }
]

export const PRICING_PLANS = [
    {
        id: 'starter',
        name: 'Scout',
        price: 4999,
        period: '/mo',
        description: 'For solo operators.',
        features: ['Matrix Dashboard', '1 Active War Plan', '20 Moves/month', '200 Muse Generations'],
        cta: 'Start Scouting',
        popular: false
    },
    {
        id: 'glide',
        name: 'Vanguard',
        price: 6999,
        period: '/mo',
        description: 'For scaling teams.',
        features: ['Matrix Dashboard', '3 Active War Plans', '60 Moves/month', '600 Muse Generations', 'Black Box A/B Testing', '2 Team Seats'],
        cta: 'Deploy Vanguard',
        popular: true
    },
    {
        id: 'soar',
        name: 'Warlord',
        price: 11999,
        period: '/mo',
        description: 'For dominance.',
        features: ['Matrix Dashboard', '10 Active War Plans', '150 Moves/month', '1,500 Muse Generations', 'Black Box A/B Testing', '5 Team Seats', 'Priority Support'],
        cta: 'Total Domination',
        popular: false
    }
]

export const FAQS = [
    { q: 'Is this just a todo list?', a: 'No. Todo lists are for chores. RaptorFlow is a war room that connects strategy to daily execution.' },
    { q: 'Define "Move".', a: 'A Move is a single tactical strike—a post, an email, an ad. We help you plan it, generate it, and track the kill.' },
    { q: 'Is the AI generic?', a: 'No. Muse learns your voice and brand laws. It writes like you, but faster and without the writer\'s block.' },
    { q: 'What is Black Box?', a: 'Our A/B testing engine. Throw ideas into the box, see what survives. Stop guessing.' },
    { q: 'Contracts?', a: 'None. You stay because we win, not because you signed a paper.' },
    { q: 'Refunds?', a: '14 days. Full refund. No interrogation.' }
]

export const COMPARISON = {
    without: [
        { key: '"What do I post?"', detail: 'paralysis every morning' },
        { key: 'Burning cash on ads', detail: 'approximating success' },
        { key: 'Random acts of marketing', detail: 'hoping something sticks' },
        { key: 'Zero data', detail: 'flying blind' }
    ],
    with: [
        { key: 'Sniper Positioning', detail: 'know your target cold' },
        { key: 'Daily Battle Plan', detail: 'execute without thinking' },
        { key: 'Infinite Ammo', detail: 'assets ready to fire' },
        { key: 'Scientific Growth', detail: 'data dictates decisions' }
    ]
}

export const ROTATING_WORDS = [
    { from: 'guessing', to: 'knowing' },
    { from: 'burning cash', to: 'printing money' },
    { from: 'chaos', to: 'domination' }
]
