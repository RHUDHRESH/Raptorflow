// Route configuration for RaptorFlow
export const routes = {
    // Public routes
    landing: '/',
    login: '/login',
    register: '/register',
    privacy: '/privacy',
    terms: '/terms',

    // Protected routes
    dashboard: '/dashboard',

    // Strategy routes
    strategy: '/strategy',
    strategyArchitect: '/strategy/architect',
    strategyCognition: '/strategy/cognition',
    strategyStrategos: '/strategy/strategos',
    strategyAesthete: '/strategy/aesthete',
    strategySeer: '/strategy/seer',
    strategyArbiter: '/strategy/arbiter',
    strategyHerald: '/strategy/herald',
    positioning: '/strategy/positioning',
    campaignBuilder: '/strategy/campaigns',
    cohorts: '/strategy/cohorts',
    cohortDetail: '/strategy/cohorts/:id',

    // Cohorts routes
    cohortsMain: '/cohorts',

    // Campaigns routes
    campaigns: '/campaigns',

    // Moves routes
    moves: '/moves',
    moveDetail: '/moves/:id',

    // Muse routes
    muse: '/muse',
    museWorkspace: '/muse/workspace',
    museRepurpose: '/muse/repurpose',
    museHooks: '/muse/hooks',
    museAsset: '/muse/assets/:id',

    // Matrix routes
    matrix: '/matrix',

    // Admin routes
    admin: '/admin',
    settings: '/settings',
    account: '/account',
    billing: '/billing',

    // Auth routes
    auth: '/auth',
    onboarding: '/onboarding',

    // Support routes
    support: '/support',
    history: '/history',
}

export default routes
