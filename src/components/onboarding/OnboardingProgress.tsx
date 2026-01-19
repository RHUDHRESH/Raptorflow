'use client'

interface OnboardingProgressProps {
  currentStep: number
  totalSteps: number
}

export function OnboardingProgress({ currentStep, totalSteps }: OnboardingProgressProps) {
  return (
    <div className="flex items-center justify-center space-x-2">
      {Array.from({ length: totalSteps }, (_, i) => (
        <div
          key={i}
          className={`h-2 w-2 rounded-full transition-colors ${
            i < currentStep
              ? 'bg-blue-600'
              : i === currentStep
              ? 'bg-blue-400'
              : 'bg-gray-300'
          }`}
        />
      ))}
    </div>
  )
}
