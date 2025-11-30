export const routes = {
  // Public
  landing: '/',
  login: '/login',
  register: '/register',
  auth: '/auth',
  privacy: '/privacy',
  terms: '/terms',

  // Onboarding
  onboarding: '/onboarding',
  onboardingNew: '/onboarding-new', // The new Luxe flow
  onboardingPricing: '/onboarding-pricing',

  // Dashboard / Core
  dashboard: '/dashboard',
  today: '/today',
  dailySweep: '/daily-sweep',

  // Moves
  moves: '/moves',
  moveDetail: (id: string) => `/moves/${id}`,

  // Quests
  quests: '/quests',

  // Campaigns
  campaigns: '/campaigns',
  campaignNew: '/campaigns/new',
  campaignEdit: (id: string) => `/campaigns/${id}/edit`,
  campaignDetail: (id: string) => `/campaigns/${id}`,

  // Strategy
  strategy: '/strategy',
  strategyWizard: '/strategy/wizard',

  // Cohorts
  cohorts: '/cohorts-moves', // TODO: Rename route to /cohorts in App.jsx?

  // Muse
  muse: '/muse',
  museWorkspace: '/muse/workspace',
  museRepurpose: '/muse/repurpose',
  museHooks: '/muse/hooks',
  museAsset: (id: string) => `/muse/assets/${id}`,

  // Matrix
  matrix: '/matrix',

  // Settings & Account
  settings: '/settings',
  account: '/account',
  billing: '/billing',
  history: '/history',
  support: '/support',

  // Workspace
  workspace: '/workspace',
  workspaceCreate: '/workspace/create',

  // Positioning
  positioning: '/positioning',
};
