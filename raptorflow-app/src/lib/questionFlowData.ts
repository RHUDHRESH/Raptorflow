'use client';

import { FoundationData, Phase1Discovery } from './foundation';

// =====================================
// Question Flow Data Types
// =====================================

export type QuestionType =
  | 'text'
  | 'textarea'
  | 'textarea-prompted'
  | 'radio-cards'
  | 'choice-cards'
  | 'multi-select'
  | 'multi-select-with-custom'
  | 'text-large'
  | 'positioning-builder'
  | 'file-upload'
  | 'url'
  | 'text-list'
  | 'drag-ranker'
  | 'step-builder'
  | 'artifact-selector'
  | 'tried-before'
  | 'proof-panel'
  | 'bullet-text'
  | 'pricing-builder'
  | 'region-geo'
  | 'company-url'; // NEW: Combined company + website

export interface MicroPrompt {
  text: string;
}

export interface QuestionOption {
  value: string;
  label: string;
  description?: string;
  icon?: string;
}

export interface Question {
  id: string;
  sectionId: string;
  type: QuestionType;
  question: string;
  hint?: string;
  placeholder?: string;
  field: string;
  options?: QuestionOption[];
  maxSelections?: number;
  required?: boolean;
  condition?: (data: FoundationData) => boolean;
  inputType?: 'text' | 'email' | 'url' | 'tel' | 'number';
  autoComplete?: string;
  showSuccess?: boolean;
  microPrompts?: MicroPrompt[];
  listCount?: number;
  listPlaceholders?: string[];
  bulletCount?: number;
  bulletLabels?: string[];
}

export interface Section {
  id: string;
  name: string;
  title: string;
  subtitle: string;
}

// =====================================
// Sections — Streamlined (4 sections)
// =====================================

export const SECTIONS: Section[] = [
  {
    id: 'warm-up',
    name: 'About You',
    title: "Let's Get Acquainted",
    subtitle: 'Quick setup — under 2 minutes.',
  },
  {
    id: 'outcomes',
    name: 'Outcomes',
    title: 'Define Success',
    subtitle: 'What does winning look like?',
  },
  {
    id: 'offer',
    name: 'Offer',
    title: 'What You Sell',
    subtitle: 'Value, pricing, and your edge.',
  },
  {
    id: 'people',
    name: 'People',
    title: 'Your Customers',
    subtitle: 'Who uses it, who buys it.',
  },
  {
    id: 'review',
    name: 'Review',
    title: 'Your Foundation',
    subtitle: 'Review and launch.',
  },
];

// =====================================
// Questions — Streamlined (11 questions)
// =====================================

export const QUESTIONS: Question[] = [
  // ===== SECTION A: WARM-UP (3 questions) =====

  // Q1: Name
  {
    id: 'q1-name',
    sectionId: 'warm-up',
    type: 'text',
    question: 'What should we call you?',
    hint: 'Personalizes your workspace.',
    placeholder: 'Your name',
    field: 'phase1.identity.name',
    autoComplete: 'name',
    showSuccess: true,
    required: true,
  },

  // Q2: Company + Website (merged)
  {
    id: 'q2-company',
    sectionId: 'warm-up',
    type: 'company-url',
    question: "What's your company called?",
    hint: "Website is optional — we'll use it for context if available.",
    placeholder: 'Acme Inc',
    field: 'phase1.identity.company',
    autoComplete: 'organization',
    required: true,
  },

  // Q3: Origin story (simplified)
  {
    id: 'q3-origin',
    sectionId: 'warm-up',
    type: 'textarea',
    question: 'In one sentence: what are you building and why?',
    hint: 'Your "why" powers your messaging.',
    placeholder: "We're building X because Y...",
    field: 'phase1.origin.narrative',
    required: true,
  },

  // ===== SECTION B: OUTCOMES (2 questions) =====

  // Q4: ONE metric to brag about
  {
    id: 'q4-brag-metric',
    sectionId: 'outcomes',
    type: 'radio-cards',
    question: "Pick the ONE metric you'd brag about.",
    hint: 'Your north star metric.',
    field: 'phase1.success.bragMetric',
    required: true,
    options: [
      { value: 'revenue', label: 'Revenue', description: 'Top-line growth' },
      {
        value: 'leads',
        label: 'Qualified Leads',
        description: 'Pipeline volume',
      },
      { value: 'cac', label: 'CAC', description: 'Acquisition cost' },
      { value: 'roas', label: 'ROAS', description: 'Ad spend return' },
      {
        value: 'activation',
        label: 'Activation',
        description: 'User engagement',
      },
      {
        value: 'retention',
        label: 'Retention',
        description: 'Churn prevention',
      },
      { value: 'nps', label: 'NPS', description: 'Customer love' },
    ],
  },

  // Q5: What are you optimizing for?
  {
    id: 'q5-optimizing',
    sectionId: 'outcomes',
    type: 'choice-cards',
    question: 'What are you optimizing for right now?',
    hint: 'Pick the stage that needs the most attention.',
    field: 'phase1.success.optimizingFor',
    required: true,
    options: [
      { value: 'acquire', label: 'Acquire', description: 'Get new customers' },
      {
        value: 'activate',
        label: 'Activate',
        description: 'Turn signups into users',
      },
      {
        value: 'retain',
        label: 'Retain',
        description: 'Keep them coming back',
      },
      {
        value: 'monetize',
        label: 'Monetize',
        description: 'Convert to revenue',
      },
      {
        value: 'expand',
        label: 'Expand',
        description: 'Upsell & grow accounts',
      },
    ],
  },

  // ===== SECTION C: OFFER (4 questions) =====

  // Q6: What are you selling?
  {
    id: 'q6-offer-type',
    sectionId: 'offer',
    type: 'radio-cards',
    question: 'What are you selling?',
    hint: 'Pick your primary offering.',
    field: 'phase1.offer.primaryType',
    required: true,
    options: [
      { value: 'saas', label: 'SaaS', description: 'Software subscription' },
      {
        value: 'service',
        label: 'Service',
        description: 'Human-delivered work',
      },
      { value: 'course', label: 'Course', description: 'Education / training' },
      {
        value: 'marketplace',
        label: 'Marketplace',
        description: 'Connecting buyers/sellers',
      },
      { value: 'app', label: 'App', description: 'Mobile or web app' },
      { value: 'hardware', label: 'Hardware', description: 'Physical product' },
    ],
  },

  // Q6b: Service delivery mode (conditional)
  {
    id: 'q6b-delivery',
    sectionId: 'offer',
    type: 'radio-cards',
    question: 'How do you deliver the service?',
    field: 'phase1.offer.deliveryMode',
    condition: (data: FoundationData) =>
      data.phase1?.offer?.primaryType === 'service',
    options: [
      {
        value: 'done-for-you',
        label: 'Done-for-you',
        description: 'Full execution',
      },
      {
        value: 'done-with-you',
        label: 'Done-with-you',
        description: 'Collaborative',
      },
      { value: 'coaching', label: 'Coaching', description: 'Advisory only' },
    ],
  },

  // Q7: Pricing
  {
    id: 'q7-pricing',
    sectionId: 'offer',
    type: 'pricing-builder',
    question: 'How do you charge?',
    hint: 'Pricing model and typical range.',
    field: 'phase1.value',
    options: [
      { value: 'monthly', label: 'Monthly' },
      { value: 'annual', label: 'Annual' },
      { value: 'per-seat', label: 'Per-seat' },
      { value: 'per-usage', label: 'Per-usage' },
      { value: 'one-time', label: 'One-time' },
      { value: 'performance', label: 'Performance-based' },
    ],
  },

  // Q8: Unfair advantage (reworked - single textarea)
  {
    id: 'q8-unfair',
    sectionId: 'offer',
    type: 'textarea',
    question: "What's your unfair advantage?",
    hint: "Why do you win vs. competitors? What can't they copy?",
    placeholder: 'We win because...',
    field: 'phase1.offer.unfairAdvantage',
    required: true,
  },

  // ===== SECTION D: PEOPLE (2 questions) =====

  // Q9: Who uses this?
  {
    id: 'q9-users',
    sectionId: 'people',
    type: 'multi-select',
    question: 'Who uses this day-to-day?',
    hint: 'The people who actually use the product.',
    field: 'phase1.buyerUser.userRoles',
    maxSelections: 3,
    options: [
      { value: 'founder', label: 'Founder / CEO' },
      { value: 'marketing', label: 'Marketing Lead' },
      { value: 'ops', label: 'Operations' },
      { value: 'sales', label: 'Sales' },
      { value: 'creator', label: 'Creator / Content' },
      { value: 'coach', label: 'Coach / Consultant' },
      { value: 'developer', label: 'Developer' },
      { value: 'other', label: 'Other', description: 'Someone else' },
    ],
  },

  // Q10: Who writes the check? (NEW)
  {
    id: 'q10-buyer',
    sectionId: 'people',
    type: 'radio-cards',
    question: 'Who writes the check?',
    hint: 'The person who approves purchase.',
    field: 'phase1.buyerUser.buyerRole',
    required: true,
    options: [
      { value: 'same', label: 'Same Person', description: 'User = buyer' },
      { value: 'founder', label: 'Founder / CEO' },
      { value: 'manager', label: 'Team Manager' },
      { value: 'procurement', label: 'Procurement / Finance' },
      { value: 'committee', label: 'Buying Committee' },
    ],
  },
];

// =====================================
// Utility Functions
// =====================================

export function getSectionQuestions(sectionId: string): Question[] {
  return QUESTIONS.filter((q) => q.sectionId === sectionId);
}

export function getQuestionSection(questionId: string): Section | undefined {
  const question = QUESTIONS.find((q) => q.id === questionId);
  if (!question) return undefined;
  return SECTIONS.find((s) => s.id === question.sectionId);
}

export function getQuestionIndex(questionId: string): number {
  return QUESTIONS.findIndex((q) => q.id === questionId);
}

export function getSectionForQuestionIndex(index: number): Section | undefined {
  const question = QUESTIONS[index];
  if (!question) return undefined;
  return SECTIONS.find((s) => s.id === question.sectionId);
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

export function getSectionProgress(
  sectionId: string,
  currentIndex: number
): { current: number; total: number } {
  const sectionQuestions = getSectionQuestions(sectionId);
  const currentQuestion = QUESTIONS[currentIndex];

  if (currentQuestion?.sectionId !== sectionId) {
    return { current: 0, total: sectionQuestions.length };
  }

  const sectionStartIndex = QUESTIONS.findIndex(
    (q) => q.sectionId === sectionId
  );
  const current = currentIndex - sectionStartIndex + 1;

  return { current, total: sectionQuestions.length };
}

export function getValidQuestions(data: FoundationData): Question[] {
  return QUESTIONS.filter((q) => !q.condition || q.condition(data));
}

export function getVisibleQuestionCount(data: FoundationData): number {
  return getValidQuestions(data).length;
}
