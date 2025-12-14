import { create } from 'zustand'
import { persist } from 'zustand/middleware'

/**
 * RaptorFlow Onboarding Store v2.0
 * 
 * Based on the 6D Intelligence Dimensions ICP Framework:
 * 1. Firmographics - Who the company is
 * 2. Technographics - What tech stack they use
 * 3. Psychographics - Why and how they buy (motivations, triggers)
 * 4. Behavioral Triggers - Signals they're in-market
 * 5. Buying Committee - Key personas and decision makers
 * 6. Category Context - Market and competitive landscape
 * 
 * Plus: Strategy Profile (Goal, Demand Source, Persuasion Axis)
 */

const initialState = {
  // ============================================
  // STEP 1: Positioning Extraction
  // ============================================
  positioning: {
    // Dan Kennedy Question
    danKennedy: '',
    // April Dunford "Better when?"
    dunford: '',
    // AI-derived fields (populated by agents)
    derived: {
      primaryTarget: '',
      primaryProblem: '',
      primaryOutcome: '',
      mainAlternatives: [],
      positioningType: '', // 'head-to-head', 'niche-subcategory', 'create-new-category'
      valueProposition: '',
      clarityScore: 0, // 0-100
    }
  },

  // ============================================
  // STEP 2: Company Context (Firmographics)
  // ============================================
  company: {
    name: '',
    website: '',
    headquarters: '',
    city: '',
    country: '',
    employeeCount: '', // '1-10', '11-50', '51-200', '201-1000', '1000+'
    industry: '',
    industryOther: '',
    stage: '', // 'bootstrap', 'pre-seed', 'seed', 'series-a', 'series-b+', 'established-sme', 'enterprise'
    // Enriched data (from Clearbit/APIs)
    enriched: {
      annualRevenue: null,
      funding: null,
      foundedYear: null,
      linkedInUrl: '',
      techStack: [],
      hasConflict: false,
      conflictFlags: []
    }
  },

  // ============================================
  // STEP 3: Product & Offer Details
  // ============================================
  product: {
    name: '',
    type: '', // 'saas', 'service', 'hybrid', 'marketplace', 'other'
    typeOther: '',
    usedBy: [], // ['founder', 'marketer', 'sales', 'ops', 'developer', 'finance', 'other']
    mainJob: '', // The main job the product does
    pricingModel: '', // 'one-time', 'monthly', 'usage-based', 'hybrid'
    priceRange: '', // e.g., "300-800"
    hasTiers: false,
    tiers: [], // [{ name: '', forWho: '', price: '' }]
    // AI-derived
    derived: {
      jtbd: [], // Jobs to be done
      outcomeType: '', // 'money', 'time', 'risk', 'status'
      likelyACV: null,
      ticketSize: '', // 'low', 'mid', 'high'
      saleType: '' // 'high-touch', 'self-serve'
    }
  },

  // ============================================
  // STEP 4: Market & Competition (User View)
  // ============================================
  market: {
    // If not you, what would they do?
    alternativeAction: '', // 'competitor', 'hire-internal', 'diy-tools', 'nothing'
    namedCompetitors: [], // Competitor names
    realCompetition: '', // Free text - who they REALLY compete with
    pricePosition: 50, // 0-100 slider (Cheap to Premium)
    complexityPosition: 50, // 0-100 slider (Simple to Power-user)
    differentiation: '', // One sentence explanation
    // System-derived (from agents)
    systemView: {
      competitorProfiles: [], // { name, tagline, features, pricing }
      positioningGaps: [],
      wedges: [],
      mapCoordinates: { x: 50, y: 50 },
      competitorCoordinates: [] // { name, x, y }
    }
  },

  // ============================================
  // STEP 5: Strategic Trade-offs
  // ============================================
  strategy: {
    // Matrix 1: Goal Focus
    goalPrimary: '', // 'velocity', 'efficiency', 'penetration'
    goalSecondary: '',
    // Matrix 2: Demand Source
    demandSource: '', // 'capture', 'creation', 'expansion'
    // Matrix 3: Persuasion Lever
    persuasionAxis: '', // 'money', 'time', 'risk-image'
    // Derived
    impliedTradeoffs: [],
    recommendedProtocols: [] // ['A', 'B', 'C', etc.]
  },

  // ============================================
  // STEP 6: Generated ICPs (Output)
  // ============================================
  icps: [
    // {
    //   id: '',
    //   label: '', // e.g., 'Desperate Scaler'
    //   summary: '',
    //   firmographics: {},
    //   technographics: {},
    //   psychographics: { painPoints: [], motivations: [], triggers: [] },
    //   buyingCommittee: [],
    //   categoryContext: {},
    //   fitScore: 0,
    //   selected: true
    // }
  ],

  // ============================================
  // STEP 7: War Plan (Output)
  // ============================================
  warPlan: {
    generated: false,
    phases: [
      // {
      //   name: '',
      //   days: '',
      //   objectives: [],
      //   campaigns: [],
      //   moves: [],
      //   kpis: []
      // }
    ],
    protocols: {
      A: { name: 'Authority Blitz', active: false },
      B: { name: 'Trust Anchor', active: false },
      C: { name: 'Cost of Inaction', active: false },
      D: { name: 'Facilitator Nudge', active: false },
      E: { name: 'Champions Armory', active: false },
      F: { name: 'Churn Intercept', active: false }
    },
    skeleton: null
  },

  // ============================================
  // UI & Meta State
  // ============================================
  currentStep: 1,
  totalSteps: 8,
  isSaved: true,
  isProcessing: false,
  lastSaved: null,
  completedSteps: [],
  
  // Onboarding mode
  mode: 'self-service', // 'self-service' or 'sales-assisted'
  salesRepId: null,
  salesRepName: '',
  
  // Plan selection (happens after onboarding)
  selectedPlan: null, // 'ascent', 'glide', 'soar'
  paymentStatus: 'pending', // 'pending', 'processing', 'completed', 'failed'
  
  // For sales-assisted: shareable link token
  shareToken: null,
  sharedAt: null,
}

const useOnboardingStore = create(
  persist(
    (set, get) => ({
      ...initialState,

      // ============================================
      // NAVIGATION
      // ============================================
      setStep: (step) => set({ currentStep: step }),
      nextStep: () => {
        const { currentStep, totalSteps, completedSteps } = get()
        if (currentStep < totalSteps) {
          const newCompleted = [...new Set([...completedSteps, currentStep])]
          set({ 
            currentStep: currentStep + 1,
            completedSteps: newCompleted 
          })
        }
      },
      prevStep: () => {
        const { currentStep } = get()
        if (currentStep > 1) {
          set({ currentStep: currentStep - 1 })
        }
      },

      // ============================================
      // POSITIONING UPDATES
      // ============================================
      updatePositioning: (data) => {
        set((state) => ({
          positioning: { ...state.positioning, ...data },
          isSaved: false
        }))
        get().autoSave()
      },

      // ============================================
      // COMPANY UPDATES
      // ============================================
      updateCompany: (data) => {
        set((state) => ({
          company: { ...state.company, ...data },
          isSaved: false
        }))
        get().autoSave()
      },

      setEnrichedData: (enriched) => {
        set((state) => ({
          company: {
            ...state.company,
            enriched: { ...state.company.enriched, ...enriched }
          }
        }))
      },

      // ============================================
      // PRODUCT UPDATES
      // ============================================
      updateProduct: (data) => {
        set((state) => ({
          product: { ...state.product, ...data },
          isSaved: false
        }))
        get().autoSave()
      },

      addTier: (tier) => {
        set((state) => ({
          product: {
            ...state.product,
            tiers: [...state.product.tiers, tier]
          },
          isSaved: false
        }))
        get().autoSave()
      },

      removeTier: (index) => {
        set((state) => ({
          product: {
            ...state.product,
            tiers: state.product.tiers.filter((_, i) => i !== index)
          },
          isSaved: false
        }))
        get().autoSave()
      },

      // ============================================
      // MARKET UPDATES
      // ============================================
      updateMarket: (data) => {
        set((state) => ({
          market: { ...state.market, ...data },
          isSaved: false
        }))
        get().autoSave()
      },

      addCompetitor: (name) => {
        const { market } = get()
        if (!market.namedCompetitors.includes(name)) {
          set((state) => ({
            market: {
              ...state.market,
              namedCompetitors: [...state.market.namedCompetitors, name]
            },
            isSaved: false
          }))
          get().autoSave()
        }
      },

      removeCompetitor: (name) => {
        set((state) => ({
          market: {
            ...state.market,
            namedCompetitors: state.market.namedCompetitors.filter(c => c !== name)
          },
          isSaved: false
        }))
        get().autoSave()
      },

      // ============================================
      // STRATEGY UPDATES
      // ============================================
      updateStrategy: (data) => {
        set((state) => ({
          strategy: { ...state.strategy, ...data },
          isSaved: false
        }))
        get().autoSave()
      },

      // ============================================
      // ICP UPDATES
      // ============================================
      setICPs: (icps) => {
        set({ icps })
      },

      toggleICP: (icpId, selected) => {
        set((state) => ({
          icps: state.icps.map(icp => 
            icp.id === icpId ? { ...icp, selected } : icp
          )
        }))
      },

      // ============================================
      // WAR PLAN UPDATES
      // ============================================
      setWarPlan: (warPlan) => {
        set({ warPlan })
      },

      toggleProtocol: (protocolKey, active) => {
        set((state) => ({
          warPlan: {
            ...state.warPlan,
            protocols: {
              ...state.warPlan.protocols,
              [protocolKey]: { ...state.warPlan.protocols[protocolKey], active }
            }
          }
        }))
      },

      // ============================================
      // PLAN SELECTION
      // ============================================
      selectPlan: (plan) => {
        set({ selectedPlan: plan })
      },

      setPaymentStatus: (status) => {
        set({ paymentStatus: status })
      },

      // ============================================
      // MODE & SALES REP
      // ============================================
      setMode: (mode) => {
        set({ mode })
      },

      setSalesRep: (id, name) => {
        set({ 
          mode: 'sales-assisted',
          salesRepId: id, 
          salesRepName: name 
        })
      },

      generateShareToken: () => {
        const token = `RF_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`
        set({ 
          shareToken: token,
          sharedAt: new Date().toISOString()
        })
        return token
      },

      // ============================================
      // UTILITY
      // ============================================
      autoSave: () => {
        // Debounced save indicator
        setTimeout(() => {
          set({ 
            isSaved: true,
            lastSaved: new Date().toISOString()
          })
        }, 500)
      },

      setProcessing: (isProcessing) => {
        set({ isProcessing })
      },

      // Get completion percentage
      getProgress: () => {
        const state = get()
        const checks = [
          // Positioning complete
          state.positioning.danKennedy.length > 50 && state.positioning.dunford.length > 50,
          // Company complete
          state.company.name && state.company.website && state.company.employeeCount && state.company.industry,
          // Product complete
          state.product.name && state.product.type && state.product.usedBy.length > 0 && state.product.mainJob,
          // Market complete
          state.market.alternativeAction && state.market.differentiation,
          // Strategy complete
          state.strategy.goalPrimary && state.strategy.demandSource && state.strategy.persuasionAxis,
        ]
        const completed = checks.filter(Boolean).length
        return Math.round((completed / checks.length) * 100)
      },

      // Get all data for export/PDF
      getExportData: () => {
        const state = get()
        return {
          positioning: state.positioning,
          company: state.company,
          product: state.product,
          market: state.market,
          strategy: state.strategy,
          icps: state.icps,
          warPlan: state.warPlan,
          selectedPlan: state.selectedPlan,
          mode: state.mode,
          salesRepName: state.salesRepName,
          generatedAt: new Date().toISOString()
        }
      },

      // Reset entire onboarding
      resetOnboarding: () => set(initialState),

      // Reset to specific step
      resetFrom: (step) => {
        const state = get()
        const resetData = {}
        
        if (step <= 1) resetData.positioning = initialState.positioning
        if (step <= 2) resetData.company = initialState.company
        if (step <= 3) resetData.product = initialState.product
        if (step <= 4) resetData.market = initialState.market
        if (step <= 5) resetData.strategy = initialState.strategy
        if (step <= 6) resetData.icps = initialState.icps
        if (step <= 7) resetData.warPlan = initialState.warPlan
        
        set({
          ...resetData,
          currentStep: step,
          completedSteps: state.completedSteps.filter(s => s < step)
        })
      }
    }),
    {
      name: 'raptorflow-onboarding-v2',
      version: 2,
      partialize: (state) => ({
        positioning: state.positioning,
        company: state.company,
        product: state.product,
        market: state.market,
        strategy: state.strategy,
        icps: state.icps,
        warPlan: state.warPlan,
        currentStep: state.currentStep,
        completedSteps: state.completedSteps,
        mode: state.mode,
        salesRepId: state.salesRepId,
        salesRepName: state.salesRepName,
        selectedPlan: state.selectedPlan,
        shareToken: state.shareToken,
        sharedAt: state.sharedAt,
      })
    }
  )
)

export default useOnboardingStore
