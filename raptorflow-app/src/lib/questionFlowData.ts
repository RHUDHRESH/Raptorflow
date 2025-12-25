'use client';

import {
    FoundationData
} from './foundation';

// =====================================
// Question Flow Data Types
// =====================================

export type QuestionType =
    | 'text'
    | 'textarea'
    | 'radio-cards'
    | 'choice-cards'
    | 'multi-select'
    | 'text-large'
    | 'positioning-builder'
    | 'file-upload'
    | 'url'
    | 'text-list'      // NEW: Multiple text inputs (e.g., 3 best customers)
    | 'drag-ranker';   // NEW: Drag-to-reorder list for ranking

export interface QuestionOption {
    value: string;
    label: string;
    description?: string;
}

export interface Question {
    id: string;
    sectionId: string;
    type: QuestionType;
    question: string;
    hint?: string;
    placeholder?: string;
    field: string; // Path to data field, e.g., 'business.name'
    options?: QuestionOption[];
    maxSelections?: number; // For multi-select
    required?: boolean;
    condition?: (data: FoundationData) => boolean; // Logic for showing/hiding

    // UX Improvements
    inputType?: 'text' | 'email' | 'url' | 'tel' | 'number';
    autoComplete?: string;
    showSuccess?: boolean;

    // NEW: For text-list type
    listCount?: number;      // Number of text inputs (default 3)
    listPlaceholders?: string[];  // Placeholder for each input
}

export interface Section {
    id: string;
    name: string;
    title: string; // Cinematic title
    subtitle: string;
}

// =====================================
// Sections Definition — Know You MVP
// =====================================

export const SECTIONS: Section[] = [
    {
        id: 'know-you',
        name: 'Know You',
        title: 'Let\'s Get To Know You',
        subtitle: 'Answer these quick questions. Takes about 90 seconds.',
    },
    {
        id: 'clarifiers',
        name: 'Clarifiers',
        title: 'Quick Clarifiers',
        subtitle: 'A few more details to tailor your strategy.',
    },
    {
        id: 'deep-dive',
        name: 'Deep Dive',
        title: 'The Confession',
        subtitle: 'Optional: Go deeper into positioning psychology.',
    },
    {
        id: 'review',
        name: 'Review',
        title: 'Your Foundation',
        subtitle: 'Review and launch your marketing foundation.',
    },
];

// =====================================
// Questions Definition — Know You MVP
// =====================================

export const QUESTIONS: Question[] = [
    // ===== KNOW YOU SECTION (Core 10 Questions) =====

    // 1) The One Link
    {
        id: 'know-link',
        sectionId: 'know-you',
        type: 'url',
        question: 'Drop the best link that explains your business.',
        hint: 'Website, Notion doc, pitch deck, app store, LinkedIn — anything that shows what you do.',
        placeholder: 'https://...',
        field: 'business.websiteUrl',
        inputType: 'url',
    },

    // 2) What business are you?
    {
        id: 'know-business-type',
        sectionId: 'know-you',
        type: 'radio-cards',
        question: 'What business are you?',
        hint: 'Pick the closest match.',
        field: 'business.businessType',
        required: true,
        options: [
            { value: 'saas', label: 'SaaS', description: 'Software as a service' },
            { value: 'agency', label: 'Agency', description: 'Services & consulting' },
            { value: 'd2c', label: 'D2C', description: 'Direct to consumer brand' },
            { value: 'local-service', label: 'Local Service', description: 'Geo-bound services' },
            { value: 'creator', label: 'Creator', description: 'Content, courses, community' },
            { value: 'marketplace', label: 'Marketplace', description: 'Platform connecting buyers/sellers' },
            { value: 'other', label: 'Other', description: 'Something else' },
        ],
    },

    // 3) What stage?
    {
        id: 'know-stage',
        sectionId: 'know-you',
        type: 'radio-cards',
        question: 'What stage is your business?',
        field: 'business.stage',
        required: true,
        options: [
            { value: 'idea', label: 'Idea', description: 'Still validating' },
            { value: 'pre-launch', label: 'Pre-launch', description: 'Building, not live yet' },
            { value: 'beta', label: 'Beta', description: 'Live with early users' },
            { value: 'live', label: 'Live', description: 'Public and selling' },
            { value: 'scaling', label: 'Scaling', description: 'Growing aggressively' },
        ],
    },

    // 4) Who do you sell to?
    {
        id: 'know-customer-type',
        sectionId: 'know-you',
        type: 'radio-cards',
        question: 'Who do you sell to?',
        hint: 'Your primary customer type.',
        field: 'cohorts.customerType',
        required: true,
        options: [
            { value: 'b2b', label: 'B2B', description: 'Businesses & companies' },
            { value: 'b2c', label: 'B2C', description: 'Individual consumers' },
            { value: 'b2g', label: 'B2G', description: 'Government entities' },
            { value: 'mixed', label: 'Mixed', description: 'Multiple types' },
        ],
    },

    // 5) Primary buyer role
    {
        id: 'know-buyer-role',
        sectionId: 'clarifiers',
        type: 'multi-select',
        question: 'Who holds the purchasing power?',
        hint: 'Select the roles that typically make the buying decision.',
        field: 'cohorts.buyerRoleChips',
        maxSelections: 3,
        options: [
            { value: 'founder', label: 'Founder / CEO' },
            { value: 'marketing', label: 'Marketing Lead' },
            { value: 'sales', label: 'Sales Lead' },
            { value: 'hr', label: 'HR' },
            { value: 'ops', label: 'Operations' },
            { value: 'finance', label: 'Finance / CFO' },
            { value: 'other', label: 'Other' },
        ],
    },

    // 6) What do you sell (one line)
    {
        id: 'know-offer',
        sectionId: 'know-you',
        type: 'text',
        question: 'What do you sell? (One line)',
        hint: 'Complete: "We help ___ achieve ___ without ___."',
        placeholder: 'We help founders get marketing under control without hiring an agency.',
        field: 'business.offerStatement',
    },

    // 6.5) Industry / Vertical
    {
        id: 'know-industry',
        sectionId: 'clarifiers',
        type: 'text',
        question: 'What industry are you in?',
        hint: 'e.g., Fintech, EdTech, Real Estate, Health & Wellness.',
        placeholder: 'SaaS / Marketing Tech',
        field: 'business.industry',
        autoComplete: 'organization-title', // close approximation
    },

    // 7) Pricing band
    {
        id: 'know-price',
        sectionId: 'clarifiers',
        type: 'radio-cards',
        question: 'What\'s your price range?',
        hint: 'Approximate ticket size per deal/sale.',
        field: 'business.priceBand',
        options: [
            { value: 'free', label: 'Free', description: 'Freemium or free tier' },
            { value: 'under-5k', label: '< ₹5k', description: 'Low ticket' },
            { value: '5k-25k', label: '₹5k – ₹25k', description: 'Mid ticket' },
            { value: '25k-1l', label: '₹25k – ₹1L', description: 'High ticket' },
            { value: '1l-plus', label: '₹1L+', description: 'Enterprise / Premium' },
        ],
    },

    // 8) Sales motion
    {
        id: 'know-motion',
        sectionId: 'clarifiers',
        type: 'radio-cards',
        question: 'How do customers buy from you?',
        field: 'business.salesMotion',
        options: [
            { value: 'self-serve', label: 'Self-serve', description: 'They buy directly, no sales call' },
            { value: 'demo-led', label: 'Demo-led', description: 'Sales calls or demos required' },
            { value: 'hybrid', label: 'Hybrid', description: 'Mix of both' },
        ],
    },

    // 9) Best customers (Critical for ICP generation)
    {
        id: 'know-best-customers',
        sectionId: 'deep-dive',
        type: 'text-list',
        question: 'Describe your 3 best customers',
        hint: 'Industry + size + role + why they\'re your best. Be specific.',
        field: 'customerInsights.bestCustomers',
        listCount: 3,
        listPlaceholders: [
            'e.g., Algolia - 150 employees, VP Marketing - 150% NRR',
            'e.g., Intercom - SaaS, Marketing team of 8 - Fast adoption',
            'e.g., Stripe - Enterprise, Head of Growth - Case study ready',
        ],
    },

    // 10) Trigger events (What makes them buy now)
    {
        id: 'know-triggers',
        sectionId: 'deep-dive',
        type: 'multi-select',
        question: 'What makes them say "we need this NOW"?',
        hint: 'The moment they start actively looking.',
        field: 'customerInsights.triggerEvents',
        maxSelections: 4,
        options: [
            { value: 'hiring-surge', label: 'Hiring surge' },
            { value: 'funding-round', label: 'Funding round' },
            { value: 'missed-target', label: 'Missed target' },
            { value: 'compliance-change', label: 'Compliance change' },
            { value: 'competitor-threat', label: 'Competitor threat' },
            { value: 'tech-migration', label: 'Tech migration' },
            { value: 'team-expansion', label: 'Team expansion' },
            { value: 'churn-spike', label: 'Churn spike' },
            { value: 'reorg', label: 'Reorg / restructure' },
            { value: 'new-leadership', label: 'New leadership' },
            { value: 'budget-approval', label: 'New budget approved' },
            { value: 'seasonal-peak', label: 'Seasonal peak' },
        ],
    },

    // 11) Current alternatives (What they used before)
    {
        id: 'know-alternatives',
        sectionId: 'deep-dive',
        type: 'multi-select',
        question: 'What did they use before you?',
        hint: 'Current alternatives they\'re switching from.',
        field: 'customerInsights.alternatives',
        options: [
            { value: 'spreadsheets', label: 'Spreadsheets / Excel' },
            { value: 'notion', label: 'Notion / Docs' },
            { value: 'hubspot', label: 'HubSpot' },
            { value: 'marketo', label: 'Marketo' },
            { value: 'agencies', label: 'Marketing agencies' },
            { value: 'freelancers', label: 'Freelancers' },
            { value: 'zapier-glue', label: 'Zapier + tools cobbled together' },
            { value: 'internal-team', label: 'Internal team / DIY' },
            { value: 'nothing', label: 'Nothing (greenfield)' },
        ],
    },

    // 12) Pain ranking (Drag to reorder)
    {
        id: 'know-pains',
        sectionId: 'deep-dive',
        type: 'drag-ranker',
        question: 'Rank their biggest pains',
        hint: 'Drag to reorder. #1 = most painful.',
        field: 'customerInsights.painRanking',
        options: [
            { value: 'leads-inconsistent', label: 'Leads are inconsistent' },
            { value: 'cant-prove-roi', label: 'Can\'t prove marketing ROI' },
            { value: 'content-not-converting', label: 'Content doesn\'t convert' },
            { value: 'too-many-tools', label: 'Too many disconnected tools' },
            { value: 'no-positioning-clarity', label: 'No positioning clarity' },
            { value: 'scaling-without-hiring', label: 'Scaling without hiring' },
        ],
    },

    // 13) Primary regions
    {
        id: 'know-regions',
        sectionId: 'clarifiers',
        type: 'multi-select',
        question: 'Where can you actually sell?',
        hint: 'Select your primary markets.',
        field: 'cohorts.primaryRegions',
        options: [
            { value: 'india', label: 'India' },
            { value: 'us', label: 'United States' },
            { value: 'eu', label: 'Europe' },
            { value: 'global', label: 'Global' },
            { value: 'other', label: 'Other regions' },
        ],
    },

    // 10) Languages
    {
        id: 'know-languages',
        sectionId: 'clarifiers',
        type: 'multi-select',
        question: 'What languages do you market in?',
        field: 'cohorts.languages',
        options: [
            { value: 'english', label: 'English' },
            { value: 'hinglish', label: 'Hinglish' },
            { value: 'hindi', label: 'Hindi' },
            { value: 'tamil', label: 'Tamil' },
            { value: 'other', label: 'Other' },
        ],
    },

    // 11) 90-day goal
    {
        id: 'know-goal',
        sectionId: 'know-you',
        type: 'radio-cards',
        question: 'What\'s your #1 goal for the next 90 days?',
        hint: 'This sets the compass for your entire strategy.',
        field: 'goals.primaryGoal',
        required: true,
        options: [
            { value: 'leads', label: 'Get Leads', description: 'Fill the pipeline' },
            { value: 'close-deals', label: 'Close Deals', description: 'Convert pipeline to revenue' },
            { value: 'increase-conversion', label: 'Increase Conversion', description: 'Optimize what\'s working' },
            { value: 'content-engine', label: 'Content Engine', description: 'Build consistent output' },
            { value: 'launch', label: 'Launch', description: 'Go to market' },
            { value: 'retention', label: 'Retention', description: 'Keep existing customers' },
        ],
    },

    // 12) Constraints
    {
        id: 'know-constraints',
        sectionId: 'clarifiers',
        type: 'multi-select',
        question: 'What are your biggest constraints?',
        hint: 'Select up to 2.',
        field: 'goals.constraints',
        maxSelections: 2,
        options: [
            { value: 'low-budget', label: 'Low budget' },
            { value: 'no-time', label: 'No time' },
            { value: 'no-design', label: 'No design team' },
            { value: 'compliance', label: 'Compliance-sensitive' },
            { value: 'no-audience', label: 'No audience yet' },
        ],
    },

    // 13) Current channels
    {
        id: 'know-channels',
        sectionId: 'clarifiers',
        type: 'multi-select',
        question: 'Which channels are you using today?',
        hint: 'Select your top 2 active channels.',
        field: 'reality.currentChannels',
        maxSelections: 3,
        options: [
            { value: 'linkedin', label: 'LinkedIn' },
            { value: 'instagram', label: 'Instagram' },
            { value: 'whatsapp', label: 'WhatsApp' },
            { value: 'email', label: 'Email' },
            { value: 'youtube', label: 'YouTube' },
            { value: 'seo', label: 'SEO / Blog' },
            { value: 'ads', label: 'Paid Ads' },
            { value: 'offline', label: 'Offline / Events' },
        ],
    },

    // 14) Current tools
    {
        id: 'know-tools',
        sectionId: 'clarifiers',
        type: 'multi-select',
        question: 'What tools are you using for marketing?',
        field: 'reality.currentTools',
        options: [
            { value: 'none', label: 'None' },
            { value: 'sheets', label: 'Sheets / Excel' },
            { value: 'notion', label: 'Notion' },
            { value: 'hubspot', label: 'HubSpot' },
            { value: 'zoho', label: 'Zoho' },
            { value: 'pipedrive', label: 'Pipedrive' },
            { value: 'mailchimp', label: 'Mailchimp' },
            { value: 'klaviyo', label: 'Klaviyo' },
            { value: 'other', label: 'Other' },
        ],
    },

    // 15) Proof inventory
    {
        id: 'know-proof',
        sectionId: 'clarifiers',
        type: 'multi-select',
        question: 'What proof do you have?',
        hint: 'This helps us avoid fluff in your messaging.',
        field: 'proof.proofTypes',
        options: [
            { value: 'testimonials', label: 'Testimonials' },
            { value: 'case-study', label: 'Case studies' },
            { value: 'metrics', label: 'Numbers / Metrics' },
            { value: 'logos', label: 'Client logos' },
            { value: 'none', label: 'None yet' },
        ],
    },

    // 16) Voice preference
    {
        id: 'know-voice',
        sectionId: 'know-you',
        type: 'radio-cards',
        question: 'How should your brand sound?',
        hint: 'This shapes all generated content.',
        field: 'messaging.voicePreference',
        required: true,
        options: [
            { value: 'calm-premium', label: 'Calm & Premium', description: 'Luxury, understated confidence' },
            { value: 'direct-punchy', label: 'Direct & Punchy', description: 'No fluff, straight talk' },
            { value: 'friendly-warm', label: 'Friendly & Warm', description: 'Approachable, human' },
            { value: 'technical-precise', label: 'Technical & Precise', description: 'Data-driven, expert' },
            { value: 'bold-contrarian', label: 'Bold & Contrarian', description: 'Challenge the status quo' },
        ],
    },

    // ===== CLARIFIERS SECTION (Conditional Smart Follow-ups) =====

    // B2B: Company size
    {
        id: 'clarify-company-size',
        sectionId: 'clarifiers',
        type: 'radio-cards',
        question: 'What size companies do you target?',
        field: 'cohorts.companySize',
        condition: (data: FoundationData) => {
            const ct = data.cohorts?.customerType;
            return ct === 'b2b' || (Array.isArray(ct) && ct.includes('b2b'));
        },
        options: [
            { value: '1-10', label: '1–10', description: 'Micro/Solo' },
            { value: '10-50', label: '10–50', description: 'Small' },
            { value: '50-200', label: '50–200', description: 'Mid-market' },
            { value: '200+', label: '200+', description: 'Enterprise' },
        ],
    },

    // B2B: Sales cycle
    {
        id: 'clarify-sales-cycle',
        sectionId: 'clarifiers',
        type: 'radio-cards',
        question: 'How long is your typical sales cycle?',
        field: 'cohorts.salesCycle',
        condition: (data: FoundationData) => {
            const ct = data.cohorts?.customerType;
            return ct === 'b2b' || (Array.isArray(ct) && ct.includes('b2b'));
        },
        options: [
            { value: 'same-day', label: 'Same day', description: 'Instant decisions' },
            { value: '1-2-weeks', label: '1–2 weeks', description: 'Quick turnaround' },
            { value: '1-3-months', label: '1–3 months', description: 'Standard B2B' },
            { value: '3-plus-months', label: '3+ months', description: 'Enterprise deals' },
        ],
    },

    // D2C: Average order value
    {
        id: 'clarify-aov',
        sectionId: 'clarifiers',
        type: 'radio-cards',
        question: 'What\'s your average order value?',
        field: 'cohorts.averageOrderValue',
        condition: (data: FoundationData) => {
            const bt = data.business?.businessType;
            return bt === 'd2c';
        },
        options: [
            { value: 'under-500', label: '< ₹500' },
            { value: '500-2k', label: '₹500 – ₹2k' },
            { value: '2k-10k', label: '₹2k – ₹10k' },
            { value: '10k-plus', label: '₹10k+' },
        ],
    },

    // Business name (needed for personalization)
    {
        id: 'clarify-name',
        sectionId: 'clarifiers',
        type: 'text',
        question: 'What\'s your business name?',
        hint: 'We\'ll use this to personalize your dashboard.',
        placeholder: 'Acme Corp',
        field: 'business.name',
        required: true,
        autoComplete: 'organization',
        showSuccess: true,
    },

    // ===== DEEP DIVE SECTION (Optional Confession Questions) =====

    {
        id: 'deepdive-expensive',
        sectionId: 'deep-dive',
        type: 'textarea',
        question: 'What expensive problem are you trying to solve that might just need different words?',
        hint: 'Eurostar spent £6B to speed up trains. They could have added Wi-Fi so time passes faster. What\'s your version?',
        placeholder: 'Type your answer...',
        field: 'confession.expensiveProblem',
    },
    {
        id: 'deepdive-embarrassing',
        sectionId: 'deep-dive',
        type: 'textarea',
        question: 'What are your customers embarrassed to admit about why they buy?',
        hint: 'People buy hybrids to look like they care about the planet, not just to save it.',
        placeholder: 'Type your answer...',
        field: 'confession.embarrassingTruth',
    },
    {
        id: 'deepdive-signaling',
        sectionId: 'deep-dive',
        type: 'textarea',
        question: 'What does your product signal to peers, bosses, or neighbors?',
        hint: 'Beyond the utility—what status, competence, or taste does buying you communicate?',
        placeholder: 'Type your answer...',
        field: 'confession.signaling',
    },
];

// =====================================
// Utility Functions
// =====================================

export function getSectionQuestions(sectionId: string): Question[] {
    return QUESTIONS.filter(q => q.sectionId === sectionId);
}

export function getQuestionSection(questionId: string): Section | undefined {
    const question = QUESTIONS.find(q => q.id === questionId);
    if (!question) return undefined;
    return SECTIONS.find(s => s.id === question.sectionId);
}

export function getQuestionIndex(questionId: string): number {
    return QUESTIONS.findIndex(q => q.id === questionId);
}

export function getSectionForQuestionIndex(index: number): Section | undefined {
    const question = QUESTIONS[index];
    if (!question) return undefined;
    return SECTIONS.find(s => s.id === question.sectionId);
}

export function isFirstQuestionOfSection(index: number): boolean {
    if (index === 0) return true;
    const currentQuestion = QUESTIONS[index];
    const prevQuestion = QUESTIONS[index - 1];
    return currentQuestion?.sectionId !== prevQuestion?.sectionId;
}

export function getTotalQuestions(): number {
    return QUESTIONS.length;
}

export function getSectionProgress(sectionId: string, currentIndex: number): { current: number; total: number } {
    const sectionQuestions = getSectionQuestions(sectionId);
    const currentQuestion = QUESTIONS[currentIndex];

    if (currentQuestion?.sectionId !== sectionId) {
        return { current: 0, total: sectionQuestions.length };
    }

    const sectionStartIndex = QUESTIONS.findIndex(q => q.sectionId === sectionId);
    const current = currentIndex - sectionStartIndex + 1;

    return { current, total: sectionQuestions.length };
}

// Helper to filter valid questions based on condition
export function getValidQuestions(data: FoundationData): Question[] {
    return QUESTIONS.filter(q => !q.condition || q.condition(data));
}

// Get count of visible questions (for progress display)
export function getVisibleQuestionCount(data: FoundationData): number {
    return getValidQuestions(data).length;
}
