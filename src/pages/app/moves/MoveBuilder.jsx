import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, ArrowRight } from 'lucide-react'
import StepProblem from './StepProblem'
import StepSituation from './StepSituation'
import StepFramework from './StepFramework'
import StepBuild from './StepBuild'
import StepPreflight from './StepPreflight'
import StepStart from './StepStart'

/**
 * MoveBuilder - 11-step wizard for creating problem-driven Moves
 * 
 * Flow:
 * 1. Pick Problem
 * 2. Situation
 * 3. Framework
 * 4-9. Build (Inputs, Rules, Actions, Outputs, Channels, Metrics)
 * 10. Preflight
 * 11. Launch
 */

const STEPS = [
    { id: 1, name: 'Problem', description: 'What challenge are you facing?' },
    { id: 2, name: 'Situation', description: 'Tell us about your context' },
    { id: 3, name: 'Mode', description: 'Choose your approach' },
    { id: 4, name: 'Inputs', description: 'Starting resources' },
    { id: 5, name: 'Rules', description: 'Constraints' },
    { id: 6, name: 'Actions', description: 'Daily tasks' },
    { id: 7, name: 'Outputs', description: 'Deliverables' },
    { id: 8, name: 'Channels', description: 'Where to post' },
    { id: 9, name: 'Metrics', description: 'Success criteria' },
    { id: 10, name: 'Preflight', description: 'Final checks' },
    { id: 11, name: 'Launch', description: 'Start your move' }
]

const MoveBuilder = () => {
    const navigate = useNavigate()
    const { step: urlStep } = useParams()

    // Current step
    const [currentStep, setCurrentStep] = useState(parseInt(urlStep) || 1)

    // Wizard state
    const [wizardData, setWizardData] = useState({
        // Step 1: Problem
        problemType: null,

        // Step 2: Situation
        situation: {
            speedNeeded: '14',
            timeBudget: '8h',
            salesMotion: 'calls',
            trafficLevel: 'medium',
            customerResults: 'some',
            clearOffer: 'okay',
            paidBudget: false,
            primaryChannel: 'linkedin'
        },

        // Step 3: Framework
        selectedFramework: null,

        // Build Steps (Slots)
        slots: {
            inputs: {},
            rules: {},
            dailyActions: [],
            outputs: [],
            channels: [],
            metrics: {}
        },

        // Step 10: Preflight
        preflightPassed: false,

        // Step 11: Start
        moveName: '',
        startDate: new Date().toISOString().split('T')[0],
        campaignId: null,
        runMode: 'solo',
        owner: null
    })

    // Update URL when step changes
    useEffect(() => {
        const newPath = `/app/moves/new/${currentStep}`
        if (window.location.pathname !== newPath) {
            navigate(newPath, { replace: true })
        }
    }, [currentStep, navigate])

    // Update data for a specific step
    const updateData = (key, value) => {
        setWizardData(prev => ({
            ...prev,
            [key]: value
        }))
    }

    // Navigation logic
    const canGoNext = () => {
        switch (currentStep) {
            case 1: return !!wizardData.problemType
            case 2: return true
            case 3: return !!wizardData.selectedFramework
            case 4: return true // Inputs
            case 5: return true // Rules
            case 6: return true // Actions
            case 7: return true // Outputs
            case 8: return true // Channels
            case 9: return true // Metrics
            case 10: return wizardData.preflightPassed
            case 11: return !!wizardData.moveName
            default: return false
        }
    }

    const goNext = () => {
        if (canGoNext() && currentStep < 11) {
            setCurrentStep(prev => prev + 1)
        }
    }

    const goPrev = () => {
        if (currentStep > 1) {
            setCurrentStep(prev => prev - 1)
        } else {
            navigate('/app/moves')
        }
    }

    const goToStep = (step) => {
        if (step >= 1 && step <= 11) {
            setCurrentStep(step)
        }
    }

    // Render current step
    const renderStep = () => {
        const commonProps = {
            data: wizardData,
            updateData,
            onNext: goNext,
            onPrev: goPrev,
            goToStep
        }

        switch (currentStep) {
            case 1:
                return <StepProblem {...commonProps} />
            case 2:
                return <StepSituation {...commonProps} />
            case 3:
                return <StepFramework {...commonProps} />
            case 4:
                return <StepBuild {...commonProps} slot="inputs" />
            case 5:
                return <StepBuild {...commonProps} slot="rules" />
            case 6:
                return <StepBuild {...commonProps} slot="actions" />
            case 7:
                return <StepBuild {...commonProps} slot="outputs" />
            case 8:
                return <StepBuild {...commonProps} slot="channels" />
            case 9:
                return <StepBuild {...commonProps} slot="metrics" />
            case 10:
                return <StepPreflight {...commonProps} />
            case 11:
                return <StepStart {...commonProps} />
            default:
                return null
        }
    }

    return (
        <div className="min-h-screen bg-background">
            {/* Header with progress */}
            <header className="sticky top-0 z-10 bg-background/95 backdrop-blur border-b border-border">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
                    <div className="flex items-center justify-between mb-4">
                        <button
                            onClick={goPrev}
                            className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors group"
                        >
                            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" strokeWidth={1.5} />
                            <span className="text-sm font-medium">
                                {currentStep === 1 ? 'Back to Moves' : 'Back'}
                            </span>
                        </button>

                        <div className="text-sm font-medium text-muted-foreground">
                            Step {currentStep} of {STEPS.length}
                        </div>
                    </div>

                    {/* Simple Progress Bar */}
                    <div className="h-1 bg-muted rounded-full overflow-hidden">
                        <motion.div
                            className="h-full bg-primary"
                            initial={{ width: 0 }}
                            animate={{ width: `${(currentStep / STEPS.length) * 100}%` }}
                            transition={{ duration: 0.3 }}
                        />
                    </div>
                </div>
            </header>

            {/* Step content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={currentStep}
                        initial={{ opacity: 0, x: 10 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -10 }}
                        transition={{ duration: 0.2 }}
                    >
                        {renderStep()}
                    </motion.div>
                </AnimatePresence>
            </main>

            {/* Footer with navigation */}
            <footer className="fixed bottom-0 left-0 right-0 bg-background/90 backdrop-blur-md border-t border-border z-20">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="text-sm text-muted-foreground hidden md:block font-medium">
                            {STEPS[currentStep - 1].description}
                        </div>

                        <div className="flex items-center gap-3 ml-auto">
                            {currentStep > 1 && (
                                <button
                                    onClick={goPrev}
                                    className="px-4 py-2.5 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                                >
                                    Previous
                                </button>
                            )}

                            {currentStep < 11 ? (
                                <button
                                    onClick={goNext}
                                    disabled={!canGoNext()}
                                    className="flex items-center gap-2 px-6 py-2.5 bg-primary text-primary-foreground rounded-xl text-sm font-bold hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:shadow-md hover:translate-y-[-1px] active:translate-y-[0px]"
                                >
                                    Continue
                                    <ArrowRight className="w-4 h-4" strokeWidth={2} />
                                </button>
                            ) : null
                                /* Step 11 has its own Start button in the component */
                            }
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    )
}

export default MoveBuilder
