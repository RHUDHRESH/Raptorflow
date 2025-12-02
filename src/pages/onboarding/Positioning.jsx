import React from 'react'
import OnboardingLayout from '../../components/onboarding/OnboardingLayout'
import StepNavigation from '../../components/onboarding/StepNavigation'
import Card from '../../components/Card'
import Input from '../../components/Input'
import Textarea from '../../components/onboarding/Textarea'
import ChipGroup from '../../components/onboarding/ChipGroup'
import useOnboardingStore from '../../store/onboardingStore'

export default function Positioning() {
    const { positioning, updatePositioning } = useOnboardingStore()

    const seenAsOptions = [
        'Tool',
        'Service',
        'Hybrid',
        'Other'
    ]

    const proofOptions = [
        { value: 'caseStudies', label: 'Case studies' },
        { value: 'testimonials', label: 'Testimonials' },
        { value: 'screenshots', label: 'Screenshots/metrics' },
        { value: 'logos', label: 'Logos/named clients' },
        { value: 'founderTrack', label: 'Founder track record' },
        { value: 'noneYet', label: 'None yet' }
    ]

    const handleProofChange = (key) => {
        updatePositioning({
            proof: {
                ...positioning.proof,
                [key]: !positioning.proof[key]
            }
        })
    }

    const handleProofLinkChange = (key, value) => {
        updatePositioning({
            proofLinks: {
                ...positioning.proofLinks,
                [key]: value
            }
        })
    }

    return (
        <OnboardingLayout
            overline="STEP 3 OF 4"
            heading={
                <>
                    Why should someone <span className="italic text-aubergine">choose you?</span>
                </>
            }
            description="Positioning isn't about being perfect. It's about being clear on what makes you different."
        >
            <Card hover={false}>
                <form className="space-y-6">
                    {/* Compared To */}
                    <Textarea
                        label="What do buyers compare you to today?"
                        placeholder="e.g., 'Hiring a full-time marketer, or cobbling together freelancers'"
                        value={positioning.comparedTo}
                        onChange={(e) => updatePositioning({ comparedTo: e.target.value })}
                        rows={2}
                    />

                    {/* Why Choose You */}
                    <Textarea
                        label="One honest line: why should someone choose you instead?"
                        placeholder="e.g., 'We give you the strategic clarity of a CMO without the $200k salary'"
                        value={positioning.whyChooseYou}
                        onChange={(e) => updatePositioning({ whyChooseYou: e.target.value })}
                        rows={2}
                    />

                    {/* Seen As */}
                    <ChipGroup
                        label="You are mostly seen as:"
                        options={seenAsOptions}
                        value={positioning.seenAs}
                        onChange={(value) => updatePositioning({ seenAs: value })}
                    />

                    {/* Complaints */}
                    <Textarea
                        label="What do people complain about in existing options?"
                        placeholder="e.g., 'Agencies are too expensive and slow. Freelancers are inconsistent.'"
                        value={positioning.complaints}
                        onChange={(e) => updatePositioning({ complaints: e.target.value })}
                        rows={2}
                    />

                    {/* Proof */}
                    <div className="space-y-3">
                        <label className="block text-[11px] uppercase tracking-[0.22em] text-charcoal/60">
                            What proof do you already have?
                        </label>
                        <div className="space-y-3">
                            {proofOptions.map((option) => (
                                <div key={option.value}>
                                    <div className="flex items-center gap-3">
                                        <input
                                            type="checkbox"
                                            id={option.value}
                                            checked={positioning.proof[option.value]}
                                            onChange={() => handleProofChange(option.value)}
                                            className="w-4 h-4 rounded border-line text-charcoal focus:ring-aubergine"
                                        />
                                        <label
                                            htmlFor={option.value}
                                            className="text-sm text-charcoal/70 cursor-pointer"
                                        >
                                            {option.label}
                                        </label>
                                    </div>
                                    {/* Optional link input for selected proof types (except "None yet") */}
                                    {positioning.proof[option.value] && option.value !== 'noneYet' && (
                                        <div className="ml-7 mt-2">
                                            <Input
                                                placeholder="Optional: Add link"
                                                value={positioning.proofLinks[option.value] || ''}
                                                onChange={(e) => handleProofLinkChange(option.value, e.target.value)}
                                            />
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Navigation */}
                    <StepNavigation
                        currentStep={3}
                        totalSteps={4}
                        backPath="/onboarding/audience"
                        nextPath="/onboarding/execution"
                    />
                </form>
            </Card>
        </OnboardingLayout>
    )
}
