import React from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '../Button'

/**
 * StepNavigation Component
 * Navigation footer with Back/Next buttons and step indicator
 */
export default function StepNavigation({
    currentStep,
    totalSteps,
    onBack,
    onNext,
    backPath,
    nextPath,
    nextDisabled = false,
    nextLabel = 'Next'
}) {
    const navigate = useNavigate()

    const handleBack = () => {
        if (onBack) {
            onBack()
        } else if (backPath) {
            navigate(backPath)
        }
    }

    const handleNext = () => {
        if (onNext) {
            onNext()
        } else if (nextPath) {
            navigate(nextPath)
        }
    }

    return (
        <div className="flex items-center justify-between pt-8 mt-8 border-t border-line">
            {/* Back Button */}
            <Button
                variant="secondary"
                onClick={handleBack}
                className="text-charcoal/60 hover:text-charcoal"
            >
                ← Back
            </Button>

            {/* Step Indicator */}
            {currentStep && totalSteps && (
                <p className="text-[11px] uppercase tracking-[0.22em] text-charcoal/40">
                    Step {currentStep} of {totalSteps}
                </p>
            )}

            {/* Next Button */}
            <Button
                variant="primary"
                onClick={handleNext}
                disabled={nextDisabled}
            >
                {nextLabel} →
            </Button>
        </div>
    )
}
