'use client';

import {
    BusinessStage,
    RevenueModel,
    TeamSize,
    CustomerType,
    SCARFDriver,
    DecisionStyle,
    RiskTolerance
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
    | 'positioning-builder';

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
}

export interface Section {
    id: string;
    name: string;
    title: string; // Cinematic title
    subtitle: string;
}

// =====================================
// Sections Definition
// =====================================

export const SECTIONS: Section[] = [
    {
        id: 'business',
        name: 'Business Basics',
        title: 'Tell Us About Your Business',
        subtitle: 'The foundation of your marketing strategy.',
    },
    {
        id: 'confession',
        name: 'The Confession',
        title: 'The Confession',
        subtitle: 'The real reasons people buy—and won\'t admit.',
    },
    {
        id: 'cohorts',
        name: 'Who You Serve',
        title: 'Who You Serve',
        subtitle: 'Psychological segmentation, not demographics.',
    },
    {
        id: 'positioning',
        name: 'What You Own',
        title: 'What You Own',
        subtitle: 'Change the frame, change the value.',
    },
    {
        id: 'messaging',
        name: 'How You Speak',
        title: 'How You Speak',
        subtitle: 'Create heuristics that shut down objections.',
    },
    {
        id: 'review',
        name: 'Review',
        title: 'Your Foundation',
        subtitle: 'Review and launch your marketing foundation.',
    },
];

// =====================================
// Questions Definition
// =====================================

export const QUESTIONS: Question[] = [
    // ===== BUSINESS SECTION =====
    {
        id: 'business-name',
        sectionId: 'business',
        type: 'text',
        question: 'What\'s your business name?',
        hint: 'This is how we\'ll refer to your company throughout RaptorFlow.',
        placeholder: 'Acme Corp',
        field: 'business.name',
        required: true,
    },
    {
        id: 'business-industry',
        sectionId: 'business',
        type: 'text',
        question: 'What industry are you in?',
        hint: 'Be specific—"Marketing Tech" is better than just "Tech".',
        placeholder: 'e.g., Marketing Tech, Healthcare, Fintech',
        field: 'business.industry',
    },
    {
        id: 'business-stage',
        sectionId: 'business',
        type: 'radio-cards',
        question: 'What stage is your business at?',
        hint: 'This helps us calibrate recommendations to your reality.',
        field: 'business.stage',
        options: [
            { value: 'idea', label: 'Idea Stage', description: 'Still validating the concept' },
            { value: 'early', label: 'Early', description: 'Pre-revenue or <$100k ARR' },
            { value: 'growth', label: 'Growth', description: '$100k - $1M ARR' },
            { value: 'scaling', label: 'Scaling', description: '$1M+ ARR' },
        ],
    },
    {
        id: 'business-revenue',
        sectionId: 'business',
        type: 'radio-cards',
        question: 'How do you make money?',
        field: 'business.revenueModel',
        options: [
            { value: 'saas', label: 'SaaS / Subscriptions' },
            { value: 'services', label: 'Services / Consulting' },
            { value: 'product', label: 'Physical Products' },
            { value: 'marketplace', label: 'Marketplace / Platform' },
            { value: 'other', label: 'Other' },
        ],
    },
    {
        id: 'business-team',
        sectionId: 'business',
        type: 'radio-cards',
        question: 'How big is your team?',
        field: 'business.teamSize',
        options: [
            { value: 'solo', label: 'Solo Founder' },
            { value: '2-5', label: '2-5 people' },
            { value: '6-20', label: '6-20 people' },
            { value: '20+', label: '20+ people' },
        ],
    },

    // ===== CONFESSION SECTION =====
    {
        id: 'confession-expensive',
        sectionId: 'confession',
        type: 'textarea',
        question: 'What expensive problem are you trying to solve that might just need different words?',
        hint: 'Eurostar spent £6B to speed up trains. They could have added Wi-Fi so time passes faster. What\'s your version?',
        placeholder: 'Type your answer...',
        field: 'confession.expensiveProblem',
    },
    {
        id: 'confession-embarrassing',
        sectionId: 'confession',
        type: 'textarea',
        question: 'What are your customers embarrassed to admit about why they buy?',
        hint: 'People buy hybrids to look like they care about the planet, not just to save it.',
        placeholder: 'Type your answer...',
        field: 'confession.embarrassingTruth',
    },
    {
        id: 'confession-stupid',
        sectionId: 'confession',
        type: 'textarea',
        question: 'What "stupid" thing could work because nobody is doing it?',
        hint: 'Red Bull tastes terrible and is expensive. Every logical rule says it should fail. What\'s your counterintuitive idea?',
        placeholder: 'Type your answer...',
        field: 'confession.stupidIdea',
    },
    {
        id: 'confession-signaling',
        sectionId: 'confession',
        type: 'textarea',
        question: 'What does your product signal to peers, bosses, or neighbors?',
        hint: 'Beyond the utility—what status, competence, or taste does buying you communicate?',
        placeholder: 'Type your answer...',
        field: 'confession.signaling',
    },
    {
        id: 'confession-friction',
        sectionId: 'confession',
        type: 'textarea',
        question: 'Where is the friction—and should you add some?',
        hint: 'Cake mix was too easy ("just add water"). General Mills had to add "add an egg" so people felt like cooking.',
        placeholder: 'Type your answer...',
        field: 'confession.friction',
    },

    // ===== COHORTS SECTION =====
    {
        id: 'cohorts-type',
        sectionId: 'cohorts',
        type: 'radio-cards',
        question: 'Who are your primary customers?',
        field: 'cohorts.customerType',
        options: [
            { value: 'b2b', label: 'B2B', description: 'You sell to businesses' },
            { value: 'b2c', label: 'B2C', description: 'You sell to consumers' },
            { value: 'b2g', label: 'B2G', description: 'You sell to government' },
            { value: 'mixed', label: 'Mixed', description: 'Multiple customer types' },
        ],
    },
    {
        id: 'cohorts-buyer',
        sectionId: 'cohorts',
        type: 'text',
        question: 'Who is the actual buyer?',
        hint: 'The person who signs the check, not just the user.',
        placeholder: 'e.g., Marketing Director, Founder, Head of Ops',
        field: 'cohorts.buyerRole',
    },
    {
        id: 'cohorts-drivers',
        sectionId: 'cohorts',
        type: 'multi-select',
        question: 'What motivates your best customers?',
        hint: 'Select 2-3 primary psychological drivers.',
        field: 'cohorts.primaryDrivers',
        maxSelections: 3,
        options: [
            { value: 'status', label: 'Status', description: 'They want to look competent or successful' },
            { value: 'certainty', label: 'Certainty', description: 'They want predictability and guarantees' },
            { value: 'autonomy', label: 'Autonomy', description: 'They want control and freedom to decide' },
            { value: 'relatedness', label: 'Relatedness', description: 'They want to belong to a tribe' },
            { value: 'fairness', label: 'Fairness', description: 'They care about transparency and justice' },
        ],
    },
    {
        id: 'cohorts-decision',
        sectionId: 'cohorts',
        type: 'choice-cards',
        question: 'How do they decide?',
        field: 'cohorts.decisionStyle',
        options: [
            { value: 'satisficer', label: 'Satisficers', description: 'Quick decision, "good enough" works' },
            { value: 'maximizer', label: 'Maximizers', description: 'Research for days, want the best' },
        ],
    },
    {
        id: 'cohorts-risk',
        sectionId: 'cohorts',
        type: 'choice-cards',
        question: 'What\'s their risk tolerance?',
        field: 'cohorts.riskTolerance',
        options: [
            { value: 'regret-minimizer', label: 'Regret Minimizers', description: 'Don\'t want to get blamed or look stupid' },
            { value: 'opportunity-seeker', label: 'Opportunity Seekers', description: 'Willing to take risks for upside' },
        ],
    },

    // ===== POSITIONING SECTION =====
    {
        id: 'positioning-category',
        sectionId: 'positioning',
        type: 'text',
        question: 'What category do you compete in?',
        hint: 'Complete: "We are the _____ for..."',
        placeholder: 'e.g., marketing operating system, project management tool',
        field: 'positioning.category',
    },
    {
        id: 'positioning-audience',
        sectionId: 'positioning',
        type: 'text',
        question: 'Who specifically is this for?',
        hint: 'Complete: "We are the category for _____ who want..."',
        placeholder: 'e.g., founders, lean marketing teams',
        field: 'positioning.targetAudience',
    },
    {
        id: 'positioning-outcome',
        sectionId: 'positioning',
        type: 'text',
        question: 'What psychological outcome do they seek?',
        hint: 'Not features—the feeling or state they\'re really after.',
        placeholder: 'e.g., control, confidence, clarity',
        field: 'positioning.psychologicalOutcome',
    },
    {
        id: 'positioning-owned',
        sectionId: 'positioning',
        type: 'textarea',
        question: 'What\'s one thing you could own completely that no one else is claiming?',
        hint: 'The specific territory, belief, or approach you can exclusively own.',
        placeholder: 'Type your answer...',
        field: 'positioning.ownedPosition',
    },
    {
        id: 'positioning-reframe',
        sectionId: 'positioning',
        type: 'radio-cards',
        question: 'What weakness could you reframe as a strength?',
        hint: 'Guinness reframed "slow pour" as "good things come to those who wait."',
        field: 'positioning.reframedWeakness',
        options: [
            { value: 'slow-crafted', label: 'Slow → Masterpiece', description: 'We take the time others won\'t to deliver quality they can\'t.' },
            { value: 'expensive-serious', label: 'Expensive → Investment', description: 'Price is a filter for customers who are serious about results.' },
            { value: 'new-unburdened', label: 'New → Modern', description: 'Built for today\'s reality, not weighed down by yesterday\'s legacy.' },
            { value: 'complex-powerful', label: 'Complex → Powerful', description: 'Simple tools solve simple problems. We solve the hard ones.' },
            { value: 'niche-specialized', label: 'Niche → Specialist', description: 'We don\'t serve everyone. We serve you perfectly.' },
            { value: 'custom', label: 'Custom reframe...', description: 'Turn your specific disadvantage into a superpower.' },
        ],
    },

    // ===== MESSAGING SECTION =====
    {
        id: 'messaging-heuristic',
        sectionId: 'messaging',
        type: 'text-large',
        question: 'What\'s your primary heuristic?',
        hint: 'A 3-6 word phrase that removes fear, grants permission, and shuts down debate.',
        placeholder: 'e.g., Marketing. Finally under control.',
        field: 'messaging.primaryHeuristic',
    },
    {
        id: 'messaging-belief',
        sectionId: 'messaging',
        type: 'textarea',
        question: 'What do you believe that others don\'t?',
        hint: 'Complete: "We believe..."',
        placeholder: 'Type your belief...',
        field: 'messaging.beliefPillar',
    },
    {
        id: 'messaging-promise',
        sectionId: 'messaging',
        type: 'textarea',
        question: 'What transformation do you promise?',
        hint: 'Complete: "We promise..."',
        placeholder: 'Type your promise...',
        field: 'messaging.promisePillar',
    },
    {
        id: 'messaging-proof',
        sectionId: 'messaging',
        type: 'textarea',
        question: 'What proves your belief and promise are true?',
        hint: 'Complete: "Here\'s evidence..."',
        placeholder: 'Type your proof...',
        field: 'messaging.proofPillar',
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
