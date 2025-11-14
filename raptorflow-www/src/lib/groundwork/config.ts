import { SectionConfig } from './types';

export const SECTIONS: SectionConfig[] = [
  {
    id: 'business-identity',
    title: 'Business Identity',
    question: "What's your product or service, in 1–2 sentences?",
    description: 'Tell us about your business and where you operate.',
  },
  {
    id: 'audience-icp',
    title: 'Audience & ICP',
    question: 'Who are your real customers, not personas?',
    description: 'Describe the people who buy and use your product.',
  },
  {
    id: 'goals-constraints',
    title: 'Goals & Constraints',
    question: 'What does success look like in the next 30 days?',
    description: 'Define your marketing objectives and limitations.',
  },
  {
    id: 'assets-visuals',
    title: 'Assets & Visuals',
    question: 'Want to upload your logo, pitch deck, landing page, or brand doc?',
    description: 'Share your existing brand assets and materials.',
  },
  {
    id: 'brand-energy',
    title: 'Brand Energy',
    question: 'What energy should your brand carry?',
    description: 'Define your brand personality and voice.',
  },
];

export const INITIAL_SECTION_STATE = {
  completed: false,
  data: null,
  agentQuestions: [],
};

