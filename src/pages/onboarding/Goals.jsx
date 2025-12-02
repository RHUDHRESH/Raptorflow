import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import OnboardingLayout from '../../components/onboarding/OnboardingLayout'
import Card from '../../components/Card'
import Button from '../../components/Button'
import ChipGroup from '../../components/onboarding/ChipGroup'
import Textarea from '../../components/onboarding/Textarea'
import Input from '../../components/Input'
import useOnboardingStore from '../../store/onboardingStore'

export default function Goals() {
    const navigate = useNavigate()
    const { goals, updateGoals } = useOnboardingStore()
    const [errors, setErrors] = useState({})

    const handleNext = () => {
        // Validation
        const newErrors = {}
        if (!goals.primaryObjective) newErrors.primaryObjective = 'Please select a primary objective'
        if (!goals.successDefinition || goals.successDefinition.length < 10) {
            newErrors.successDefinition = 'Please describe your success (min 10 chars)'
        }
        if (goals.metrics.length === 0) newErrors.metrics = 'Please select at least one metric'
        if (!goals.monthlyBudget) newErrors.monthlyBudget = 'Please select a budget range'

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors)
            return
        }

        navigate('/onboarding/audience')
    }

    return (
        <OnboardingLayout
            overline="STEP 1 OF 4"
            heading="Define the target."
            description="We need to know exactly what you're aiming for. Vague goals lead to vague results."
            quote={`"If you don't know where you are going, you'll end up someplace else."`}
        >
            <div className="space-y-8">
                {/* Primary Objective */}
                <section>
                    <h3 className="font-serif text-xl mb-4">Primary Objective</h3>
                    <ChipGroup
                        options={[
                            { value: 'first_customers', label: 'Get first paying customers' },
                            { value: 'scale_revenue', label: 'Scale existing revenue' },
                            { value: 'launch_product', label: 'Launch a new product' },
                            { value: 'build_audience', label: 'Build an audience' }
                        ]}
                        value={goals.primaryObjective}
                        onChange={(val) => {
                            updateGoals({ primaryObjective: val })
                            if (val) setErrors(prev => ({ ...prev, primaryObjective: null }))
                        }}
                        error={errors.primaryObjective}
                    />
                </section>

                {/* Success Definition */}
                <section>
                    <Textarea
                        label="What does winning look like?"
                        placeholder="e.g. I want to hit $10k MRR by the end of Q1 so I can quit my day job."
                        value={goals.successDefinition}
                        onChange={(e) => {
                            updateGoals({ successDefinition: e.target.value })
                            if (e.target.value.length >= 10) setErrors(prev => ({ ...prev, successDefinition: null }))
                        }}
                        maxLength={280}
                        error={errors.successDefinition}
                    />
                    <p className="text-xs text-charcoal/50 mt-2 italic">
                        Example: "10 new qualified leads per week" or "Launch MVP to 500 waitlist members"
                    </p>
                </section>

                {/* Metrics */}
                <section>
                    <h3 className="font-serif text-xl mb-4">Key Metrics (KPIs)</h3>
                    <ChipGroup
                        multiple
                        options={[
                            { value: 'revenue', label: 'Revenue / MRR' },
                            { value: 'leads', label: 'Qualified Leads' },
                            { value: 'traffic', label: 'Website Traffic' },
                            { value: 'users', label: 'Active Users' },
                            { value: 'engagement', label: 'Social Engagement' }
                        ]}
                        value={goals.metrics}
                        onChange={(val) => {
                            updateGoals({ metrics: val })
                            if (val.length > 0) setErrors(prev => ({ ...prev, metrics: null }))
                        }}
                        error={errors.metrics}
                    />
                </section>

                {/* Budget */}
                <section>
                    <h3 className="font-serif text-xl mb-4">Monthly Budget</h3>
                    <ChipGroup
                        options={[
                            { value: 'bootstrap', label: '< ₹25k' },
                            { value: 'low', label: '₹25k - ₹1L' },
                            { value: 'medium', label: '₹1L - ₹5L' },
                            { value: 'high', label: '₹5L+' }
                        ]}
                        value={goals.monthlyBudget}
                        onChange={(val) => {
                            updateGoals({ monthlyBudget: val })
                            if (val) setErrors(prev => ({ ...prev, monthlyBudget: null }))
                        }}
                        error={errors.monthlyBudget}
                    />
                </section>

                <div className="pt-8 flex justify-between items-center">
                    <Button
                        variant="secondary"
                        onClick={() => navigate('/onboarding/intro')}
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
