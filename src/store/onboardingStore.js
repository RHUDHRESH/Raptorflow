import { create } from 'zustand'
import { persist } from 'zustand/middleware'

/**
 * Onboarding Store
 * Manages state for the entire onboarding flow with localStorage persistence
 */
const useOnboardingStore = create(
    persist(
        (set) => ({
            // UI State
            isSaved: true,
            setIsSaved: (status) => set({ isSaved: status }),

            // Goals Section
            goals: {
                primaryObjective: '',
                primaryObjectiveOther: '',
                successDefinition: '',
                metrics: [],
                monthlyBudget: ''
            },

            // Audience Section
            audience: {
                idealCustomer: '',
                businessType: '',
                biggestHeadache: '',
                whereTheyHangout: [],
                hasMultipleSegments: false,
                multipleSegmentsDetails: ''
            },

            // Positioning Section
            positioning: {
                comparedTo: '',
                whyChooseYou: '',
                seenAs: '',
                complaints: '',
                proof: {
                    caseStudies: false,
                    testimonials: false,
                    screenshots: false,
                    logos: false,
                    founderTrack: false,
                    noneYet: false
                },
                proofLinks: {
                    caseStudies: '',
                    testimonials: '',
                    screenshots: '',
                    logos: '',
                    founderTrack: ''
                }
            },

            // Execution Section
            execution: {
                whoExecutes: '',
                channelsUsed: {},
                timePerWeek: '',
                doNotWant: ''
            },

            // Actions
            updateGoals: (data) => {
                set((state) => ({ goals: { ...state.goals, ...data }, isSaved: false }))
                setTimeout(() => set({ isSaved: true }), 1000)
            },

            updateAudience: (data) => {
                set((state) => ({ audience: { ...state.audience, ...data }, isSaved: false }))
                setTimeout(() => set({ isSaved: true }), 1000)
            },

            updatePositioning: (data) => {
                set((state) => ({ positioning: { ...state.positioning, ...data }, isSaved: false }))
                setTimeout(() => set({ isSaved: true }), 1000)
            },

            updateExecution: (data) => {
                set((state) => ({ execution: { ...state.execution, ...data }, isSaved: false }))
                setTimeout(() => set({ isSaved: true }), 1000)
            },

            resetOnboarding: () => set({
                isSaved: true,
                goals: {
                    primaryObjective: '',
                    primaryObjectiveOther: '',
                    successDefinition: '',
                    metrics: [],
                    monthlyBudget: ''
                },
                audience: {
                    idealCustomer: '',
                    businessType: '',
                    biggestHeadache: '',
                    whereTheyHangout: [],
                    hasMultipleSegments: false,
                    multipleSegmentsDetails: ''
                },
                positioning: {
                    comparedTo: '',
                    whyChooseYou: '',
                    seenAs: '',
                    complaints: '',
                    proof: {
                        caseStudies: false,
                        testimonials: false,
                        screenshots: false,
                        logos: false,
                        founderTrack: false,
                        noneYet: false
                    },
                    proofLinks: {
                        caseStudies: '',
                        testimonials: '',
                        screenshots: '',
                        logos: '',
                        founderTrack: ''
                    }
                },
                execution: {
                    whoExecutes: '',
                    channelsUsed: {},
                    timePerWeek: '',
                    doNotWant: ''
                }
            })
        }),
        {
            name: 'raptorflow-onboarding',
            version: 1
        }
    )
)

export default useOnboardingStore
