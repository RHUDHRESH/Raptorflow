'use client';

import {
    BusinessStage,
    BusinessType,
    RevenueModel,
    TeamSize,
    CustomerType,
    SCARFDriver,
    DecisionStyle,
    RiskTolerance,
    PriceBand,
    SalesMotion,
    BuyerRoleChip,
    RegionCode,
    LanguageCode,
    PrimaryGoal,
    Constraint,
    Channel,
    ToolOption,
    ProofType,
    VoicePreference,
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
    | 'url'; // NEW: URL input type

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
        sectionId: 'know-you',
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

    // 7) Pricing band
    {
        id: 'know-price',
        sectionId: 'know-you',
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
        sectionId: 'know-you',
        type: 'radio-cards',
        question: 'How do customers buy from you?',
        field: 'business.salesMotion',
        options: [
            { value: 'self-serve', label: 'Self-serve', description: 'They buy directly, no sales call' },
            { value: 'demo-led', label: 'Demo-led', description: 'Sales calls or demos required' },
            { value: 'hybrid', label: 'Hybrid', description: 'Mix of both' },
        ],
    },

    // 9) Primary regions
    {
        id: 'know-regions',
        sectionId: 'know-you',
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
        sectionId: 'know-you',
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
        sectionId: 'know-you',
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
        sectionId: 'know-you',
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
        sectionId: 'know-you',
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
        sectionId: 'know-you',
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
