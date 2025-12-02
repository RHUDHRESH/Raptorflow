import React from 'react'
import { useNavigate } from 'react-router-dom'
import OnboardingLayout from '../../components/onboarding/OnboardingLayout'
import Card from '../../components/Card'
import Button from '../../components/Button'
import useOnboardingStore from '../../store/onboardingStore'

export default function Review() {
    const navigate = useNavigate()
    const { goals, audience, positioning, execution } = useOnboardingStore()

    // Helper to check if section is complete
    const isSectionComplete = (section) => {
        switch (section) {
            case 'goals':
                return goals.primaryObjective && goals.successDefinition && goals.metrics?.length > 0 && goals.monthlyBudget
            case 'audience':
                return audience.idealCustomer && audience.businessType && audience.biggestHeadache && audience.whereTheyHangout?.length > 0
            case 'positioning':
                return positioning.whyChooseYou && positioning.seenAs
            case 'execution':
                return execution.whoExecutes && Object.keys(execution.channelsUsed || {}).length > 0 && execution.timePerWeek
            default:
                return false
        }
    }

    const sections = [
        {
            id: 'goals',
            title: 'Goals & Success',
            summary: goals.primaryObjective || 'Not specified',
            path: '/onboarding/goals',
            details: [
                goals.successDefinition && `"${goals.successDefinition.slice(0, 80)}${goals.successDefinition.length > 80 ? '...' : ''}"`,
                goals.metrics?.length > 0 && `Tracking: ${goals.metrics.slice(0, 2).join(', ')}`,
                goals.monthlyBudget && `Budget: ${goals.monthlyBudget}`
            ].filter(Boolean)
        },
        {
            id: 'audience',
            title: 'Audience & Buyer',
            summary: audience.idealCustomer || 'Not specified',
            path: '/onboarding/audience',
            details: [
                audience.businessType && `Type: ${audience.businessType}`,
                audience.whereTheyHangout?.length > 0 && `Channels: ${audience.whereTheyHangout.slice(0, 2).join(', ')}`
            ].filter(Boolean)
        },
        {
            id: 'positioning',
            title: 'Positioning & Competition',
            summary: positioning.whyChooseYou || 'Not specified',
            path: '/onboarding/positioning',
            details: [
                positioning.seenAs && `Seen as: ${positioning.seenAs}`,
                positioning.comparedTo && `vs. ${positioning.comparedTo}`
            ].filter(Boolean)
        },
        {
            id: 'execution',
            title: 'Execution Reality',
            summary: execution.whoExecutes || 'Not specified',
            path: '/onboarding/execution',
            details: [
                execution.timePerWeek && `Time: ${execution.timePerWeek}`,
                Object.keys(execution.channelsUsed || {}).length > 0 && `Channels: ${Object.keys(execution.channelsUsed).slice(0, 2).join(', ')}`
            ].filter(Boolean)
        }
    ]

    const allComplete = sections.every(s => isSectionComplete(s.id))

    return (
        <OnboardingLayout
            overline="REVIEW YOUR ANSWERS"
            heading={
                <>
                    Ready to build your <span className="italic text-aubergine">90-day plan.</span>
                </>
            }
            description="Take a moment to review what you've shared. You can edit any section before we generate your outline."
        >
            <div className="space-y-6">
                {/* Summary Cards */}
                <div className="space-y-4">
                    {sections.map((section) => {
                        const isComplete = isSectionComplete(section.id)
                        return (
                            <Card key={section.id} hover={false} className="relative">
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-2">
                                            <h3 className="font-serif text-lg text-charcoal">
                                                {section.title}
                                            </h3>
                                            {isComplete && (
                                                <div className="w-5 h-5 rounded-full bg-green-500 flex items-center justify-center">
                                                    <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                                    </svg>
                                                </div>
                                            )}
                                        </div>
                                        <p className="text-sm text-charcoal mb-2">
                                            {section.summary}
                                        </p>
                                        {section.details.length > 0 && (
                                            <div className="space-y-1">
                                                {section.details.map((detail, i) => (
                                                    <p key={i} className="text-xs text-charcoal/60 italic">
                                                        {detail}
                                                    </p>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                    <button
                                        onClick={() => navigate(section.path)}
                                        className="flex items-center gap-2 px-4 py-2 rounded-lg border border-line hover:border-aubergine hover:bg-aubergine/5 transition-all group"
                                    >
                                        <svg className="w-4 h-4 text-charcoal/60 group-hover:text-aubergine transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                        </svg>
                                        <span className="text-xs font-medium text-charcoal/70 group-hover:text-aubergine transition-colors">
                                            Edit
                                        </span>
                                    </button>
                                </div>
                            </Card>
                        )
                    })}
                </div>

                {/* CTA */}
                <Card hover={false} className="bg-gradient-to-br from-aubergine/5 to-gold/5 border-aubergine/20">
                    <div className="text-center space-y-4">
                        <div>
                            <h3 className="font-serif text-xl text-charcoal mb-2">
                                {allComplete ? 'Everything looks great!' : 'Almost there...'}
                            </h3>
                            <p className="text-sm text-charcoal/60">
                                {allComplete
                                    ? 'Your answers are complete. Ready to generate your custom 90-day plan.'
                                    : 'Some sections are incomplete. You can still generate, but more details = better results.'}
                            </p>
                        </div>
                        <Button
                            variant="primary"
                            onClick={() => navigate('/onboarding/generating')}
                            className="w-full md:w-auto px-12"
                        >
                            Generate my 90-day outline →
                        </Button>
                        <p className="text-xs text-charcoal/50">
                            This will take ~30 seconds. You'll see a preview before payment.
                        </p>
                    </div>
                </Card>
            </div>
        </OnboardingLayout>
    )
}
