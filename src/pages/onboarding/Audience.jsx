import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import OnboardingLayout from '../../components/onboarding/OnboardingLayout'
import Button from '../../components/Button'
import ChipGroup from '../../components/onboarding/ChipGroup'
import Textarea from '../../components/onboarding/Textarea'
import Input from '../../components/Input'
import useOnboardingStore from '../../store/onboardingStore'

export default function Audience() {
    const navigate = useNavigate()
    const { audience, updateAudience } = useOnboardingStore()
    const [errors, setErrors] = useState({})

    const handleNext = () => {
        const newErrors = {}
        if (!audience.idealCustomer) newErrors.idealCustomer = 'Please describe your ideal customer'
        if (!audience.businessType) newErrors.businessType = 'Please select a business type'
        if (!audience.biggestHeadache) newErrors.biggestHeadache = 'Please describe their headache'
        if (audience.whereTheyHangout.length === 0) newErrors.whereTheyHangout = 'Please select at least one channel'

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors)
            return
        }

        navigate('/onboarding/positioning')
    }

    return (
        <OnboardingLayout
            overline="STEP 2 OF 4"
            heading="Who are we hunting?"
            description="The clearer the avatar, the easier the messaging. Don't try to sell to everyone."
            quote={`"The riches are in the niches, but the fortune is in the follow-up."`}
        >
            <div className="space-y-8">
                {/* Multiple Segments Toggle - Moved to top */}
                <div className="bg-white/40 p-4 rounded-lg border border-line flex items-center gap-3">
                    <input
                        type="checkbox"
                        id="segments"
                        checked={audience.hasMultipleSegments}
                        onChange={(e) => updateAudience({ hasMultipleSegments: e.target.checked })}
                        className="rounded border-line text-aubergine focus:ring-aubergine"
                    />
                    <label htmlFor="segments" className="text-sm text-charcoal cursor-pointer select-none">
                        <strong>Do you serve multiple customer segments?</strong>
                        <span className="block text-xs text-charcoal/60 mt-0.5">
                            (e.g. You sell to both Agencies and In-house teams)
                        </span>
                    </label>
                </div>

                {/* Ideal Customer */}
                <section>
                    <Input
                        label="Ideal Customer Profile (ICP)"
                        placeholder="e.g. Marketing Directors at Series B SaaS companies"
                        value={audience.idealCustomer}
                        onChange={(e) => {
                            updateAudience({ idealCustomer: e.target.value })
                            if (e.target.value) setErrors(prev => ({ ...prev, idealCustomer: null }))
                        }}
                        error={errors.idealCustomer}
                    />
                </section>

                {/* Business Type */}
                <section>
                    <h3 className="font-serif text-xl mb-4">Business Type</h3>
                    <p className="text-xs text-charcoal/60 mb-3">
                        This helps us recommend the right channels.
                    </p>
                    <ChipGroup
                        options={[
                            { value: 'b2b_saas', label: 'B2B SaaS' },
                            { value: 'b2c_saas', label: 'B2C App' },
                            { value: 'agency', label: 'Agency / Service' },
                            { value: 'ecommerce', label: 'E-commerce' },
                            { value: 'creator', label: 'Creator / Info' }
                        ]}
                        value={audience.businessType}
                        onChange={(val) => {
                            updateAudience({ businessType: val })
                            if (val) setErrors(prev => ({ ...prev, businessType: null }))
                        }}
                        error={errors.businessType}
                    />
                </section>

                {/* Biggest Headache */}
                <section>
                    <Textarea
                        label="What is their biggest headache right now?"
                        placeholder="e.g. They are drowning in manual data entry and can't trust their reports."
                        value={audience.biggestHeadache}
                        onChange={(e) => {
                            updateAudience({ biggestHeadache: e.target.value })
                            if (e.target.value) setErrors(prev => ({ ...prev, biggestHeadache: null }))
                        }}
                        rows={3}
                        error={errors.biggestHeadache}
                    />
                </section>

                {/* Where they hangout */}
                <section>
                    <h3 className="font-serif text-xl mb-4">Where do they hang out?</h3>
                    <ChipGroup
                        multiple
                        options={[
                            { value: 'linkedin', label: 'LinkedIn' },
                            { value: 'twitter', label: 'X / Twitter' },
                            { value: 'instagram', label: 'Instagram' },
                            { value: 'youtube', label: 'YouTube' },
                            { value: 'reddit', label: 'Reddit / Communities' },
                            { value: 'email', label: 'Email / Newsletters' }
                        ]}
                        value={audience.whereTheyHangout}
                        onChange={(val) => {
                            updateAudience({ whereTheyHangout: val })
                            if (val.length > 0) setErrors(prev => ({ ...prev, whereTheyHangout: null }))
                        }}
                        error={errors.whereTheyHangout}
                    />
                </section>

                <div className="pt-8 flex justify-between items-center">
                    <Button
                        variant="secondary"
                        onClick={() => navigate('/onboarding/goals')}
                    >
                        Back
                    </Button>
                    <Button
                        variant="primary"
                        onClick={handleNext}
                    >
                        Next Step
                    </Button>
                </div>
            </div>
        </OnboardingLayout >
    )
}
