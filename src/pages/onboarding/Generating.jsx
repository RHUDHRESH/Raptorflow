import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import OnboardingLayout from '../../components/onboarding/OnboardingLayout'

export default function Generating() {
    const navigate = useNavigate()
    const [progress, setProgress] = useState(0)
    const [currentStep, setCurrentStep] = useState(0)

    const steps = [
        'Analyzing your goals...',
        'Mapping your audience...',
        'Crafting positioning strategy...',
        'Building execution plan...',
        'Generating 90-day timeline...',
        'Finalizing your outline...'
    ]

    useEffect(() => {
        // Simulate progress
        const progressInterval = setInterval(() => {
            setProgress(prev => {
                if (prev >= 100) {
                    clearInterval(progressInterval)
                    setTimeout(() => navigate('/preview'), 500)
                    return 100
                }
                return prev + 2
            })
        }, 100)

        // Update step text
        const stepInterval = setInterval(() => {
            setCurrentStep(prev => (prev + 1) % steps.length)
        }, 1000)

        return () => {
            clearInterval(progressInterval)
            clearInterval(stepInterval)
        }
    }, [navigate])

    return (
        <OnboardingLayout
            overline="GENERATING YOUR PLAN"
            heading={
                <>
                    Crafting your <span className="italic text-aubergine">custom strategy...</span>
                </>
            }
            description="This will take about 30 seconds. We're analyzing your answers and building a tailored 90-day plan."
        >
            <div className="space-y-8">
                {/* Progress Bar */}
                <div className="space-y-3">
                    <div className="h-2 bg-line rounded-full overflow-hidden">
                        <div
                            className="h-full bg-aubergine transition-all duration-300 ease-out"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                    <p className="text-sm text-charcoal/60 text-center">
                        {progress}% complete
                    </p>
                </div>

                {/* Current Step */}
                <div className="bg-white/40 p-8 rounded-lg border border-line text-center">
                    <div className="inline-block animate-pulse mb-4">
                        <div className="w-12 h-12 border-4 border-aubergine border-t-transparent rounded-full animate-spin" />
                    </div>
                    <p className="text-lg font-serif text-charcoal">
                        {steps[currentStep]}
                    </p>
                </div>

                {/* Steps List */}
                <div className="space-y-2">
                    {steps.map((step, index) => (
                        <div
                            key={step}
                            className={`flex items-center gap-3 p-3 rounded-lg transition-all ${index <= currentStep
                                    ? 'bg-aubergine/10 text-charcoal'
                                    : 'bg-white/20 text-charcoal/40'
                                }`}
                        >
                            <div className={`w-5 h-5 rounded-full flex items-center justify-center text-xs ${index < currentStep
                                    ? 'bg-aubergine text-canvas'
                                    : index === currentStep
                                        ? 'bg-gold text-canvas animate-pulse'
                                        : 'bg-line text-charcoal/40'
                                }`}>
                                {index < currentStep ? '✓' : index + 1}
                            </div>
                            <span className="text-sm">{step}</span>
                        </div>
                    ))}
                </div>
            </div>
        </OnboardingLayout>
    )
}
