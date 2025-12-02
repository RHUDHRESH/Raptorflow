import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import OnboardingLayout from '../../components/onboarding/OnboardingLayout'
import Button from '../../components/Button'
import ChipGroup from '../../components/onboarding/ChipGroup'
import Textarea from '../../components/onboarding/Textarea'
import useOnboardingStore from '../../store/onboardingStore'

export default function Execution() {
    const navigate = useNavigate()
    const { execution, updateExecution } = useOnboardingStore()
    const [errors, setErrors] = useState({})

    const handleNext = () => {
        const newErrors = {}
        if (!execution.whoExecutes) newErrors.whoExecutes = 'Please select who executes'
        if (Object.keys(execution.channelsUsed || {}).length === 0) newErrors.channelsUsed = 'Please select at least one channel'
        if (!execution.timePerWeek) newErrors.timePerWeek = 'Please select time commitment'

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors)
            return
        }

        navigate('/onboarding/review')
    }

    const channelOptions = [
        'Cold email',
        'LinkedIn',
        'Instagram',
        'YouTube/long-form',
        'Email newsletter',
        'Website forms',
        'Events/offline'
    ]

    const handleChannelToggle = (channel) => {
        const currentChannels = execution.channelsUsed || {}
        const newChannels = { ...currentChannels }

        if (newChannels[channel]) {
            delete newChannels[channel]
        } else {
            newChannels[channel] = 'Active' // Default to active, simplified from Dead/Warming/Active
        }

        updateExecution({ channelsUsed: newChannels })
        if (Object.keys(newChannels).length > 0) setErrors(prev => ({ ...prev, channelsUsed: null }))
    }

    return (
        <OnboardingLayout
            overline="STEP 4 OF 4"
            heading={
                <>
                    Let's talk <span className="italic text-aubergine">execution reality.</span>
                </>
            }
            description="The best plan is the one you can actually execute. Be honest about your constraints."
        >
            <div className="space-y-8">
                {/* Who Executes */}
                <section>
                    <h3 className="font-serif text-xl mb-4">Who's actually going to execute this?</h3>
                    <ChipGroup
                        options={[
                            { value: 'Just me', label: 'Just me' },
                            { value: 'Small team (<5)', label: 'Small team (<5)' },
                            { value: 'We have a marketing person', label: 'We have a marketing person' },
                            { value: 'Agency/freelancers', label: 'Agency/freelancers' }
                        ]}
                        value={execution.whoExecutes}
                        onChange={(val) => {
                            updateExecution({ whoExecutes: val })
                            if (val) setErrors(prev => ({ ...prev, whoExecutes: null }))
                        }}
                        error={errors.whoExecutes}
                    />
                </section>

                {/* Channels Used */}
                <section>
                    <h3 className="font-serif text-xl mb-4">Which channels do you already use?</h3>
                    <div className="space-y-3">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {channelOptions.map((channel) => (
                                <div
                                    key={channel}
                                    onClick={() => handleChannelToggle(channel)}
                                    className={`
                                        cursor-pointer p-4 rounded-lg border transition-all duration-200 flex items-center gap-3
                                        ${execution.channelsUsed?.[channel]
                                            ? 'bg-aubergine text-canvas border-aubergine'
                                            : 'bg-white/40 text-charcoal border-line hover:border-charcoal/30 hover:bg-white/60'}
                                    `}
                                >
                                    <div className={`
                                        w-4 h-4 rounded-full border flex items-center justify-center
                                        ${execution.channelsUsed?.[channel] ? 'border-canvas' : 'border-charcoal/30'}
                                    `}>
                                        {execution.channelsUsed?.[channel] && <div className="w-2 h-2 rounded-full bg-canvas" />}
                                    </div>
                                    <span className="text-sm font-medium">{channel}</span>
                                </div>
                            ))}
                        </div>
                        {errors.channelsUsed && (
                            <p className="text-xs text-red-500">{errors.channelsUsed}</p>
                        )}
                    </div>
                </section>

                {/* Time Per Week */}
                <section>
                    <h3 className="font-serif text-xl mb-4">Time Commitment</h3>
                    <ChipGroup
                        options={[
                            { value: '< 3 hours', label: '< 3 hours/week' },
                            { value: '3–7 hours', label: '3–7 hours/week' },
                            { value: '1–2 days', label: '1–2 days/week' },
                            { value: 'Full-time focus', label: 'Full-time focus' }
                        ]}
                        value={execution.timePerWeek}
                        onChange={(val) => {
                            updateExecution({ timePerWeek: val })
                            if (val) setErrors(prev => ({ ...prev, timePerWeek: null }))
                        }}
                        error={errors.timePerWeek}
                    />
                </section>

                {/* Do Not Want */}
                <section>
                    <Textarea
                        label="Anything you absolutely do NOT want to do?"
                        placeholder="e.g., 'No cold calling. I hate being on camera.'"
                        value={execution.doNotWant}
                        onChange={(e) => updateExecution({ doNotWant: e.target.value })}
                        rows={2}
                    />
                </section>

                <div className="pt-8 flex justify-between items-center">
                    <Button
                        variant="secondary"
                        onClick={() => navigate('/onboarding/positioning')}
                    >
                        Back
                    </Button>
                    <Button
                        variant="primary"
                        onClick={handleNext}
                    >
                        Review Plan
                    </Button>
                </div>
            </div>
        </OnboardingLayout>
    )
}
