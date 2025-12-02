import React from 'react'
import { useNavigate } from 'react-router-dom'
import OnboardingLayout from '../../components/onboarding/OnboardingLayout'
import Card from '../../components/Card'
import Button from '../../components/Button'

export default function Intro() {
    const navigate = useNavigate()

    return (
        <OnboardingLayout
            overline="NEW WAR PLAN · ~10 MINUTES"
            heading={
                <>
                    We're going to build your first <span className="italic text-aubergine">90-day outline.</span>
                </>
            }
            description="This is a structured conversation about your business, audience, and goals. We'll show you a preview before we ever ask for payment."
            quote={'"Most founders don\'t need more tactics. They need a plan they can actually execute."'}
        >
            <Card hover={false}>
                <h3 className="font-serif text-xl mb-4">What's coming</h3>
                <ul className="space-y-3 mb-8">
                    <li className="flex items-start gap-3">
                        <span className="text-gold mt-1">→</span>
                        <span className="text-sm text-charcoal/70">
                            <strong className="text-charcoal">Goals & Success:</strong> What you're trying to achieve
                        </span>
                    </li>
                    <li className="flex items-start gap-3">
                        <span className="text-gold mt-1">→</span>
                        <span className="text-sm text-charcoal/70">
                            <strong className="text-charcoal">Audience & Buyer:</strong> Who you're selling to
                        </span>
                    </li>
                    <li className="flex items-start gap-3">
                        <span className="text-gold mt-1">→</span>
                        <span className="text-sm text-charcoal/70">
                            <strong className="text-charcoal">Positioning:</strong> How you stand out
                        </span>
                    </li>
                    <li className="flex items-start gap-3">
                        <span className="text-gold mt-1">→</span>
                        <span className="text-sm text-charcoal/70">
                            <strong className="text-charcoal">Execution Reality:</strong> Who's doing the work
                        </span>
                    </li>
                    <li className="flex items-start gap-3">
                        <span className="text-gold mt-1">→</span>
                        <span className="text-sm text-charcoal/70">
                            <strong className="text-charcoal">Preview:</strong> See your plan before you pay
                        </span>
                    </li>
                </ul>

                <Button
                    variant="primary"
                    onClick={() => navigate('/onboarding/goals')}
                    className="w-full"
                >
                    Begin intake
                </Button>
            </Card>
        </OnboardingLayout >
    )
}
