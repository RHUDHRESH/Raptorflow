import React from 'react'
import { clsx } from 'clsx'
import { useLocation } from 'react-router-dom'
import useOnboardingStore from '../../store/onboardingStore'

/**
 * OnboardingLayout Component
 * Two-column editorial layout for onboarding pages
 * Left: Editorial content (overline, heading, description, quote)
 * Right: Form content
 */
export default function OnboardingLayout({
    overline,
    heading,
    description,
    quote,
    children,
    className = ''
}) {
    const { isSaved } = useOnboardingStore()
    const location = useLocation()

    // Calculate progress based on current route
    const getProgress = () => {
        const path = location.pathname
        if (path.includes('/intro')) return 0
        if (path.includes('/goals')) return 20
        if (path.includes('/audience')) return 40
        if (path.includes('/positioning')) return 60
        if (path.includes('/execution')) return 80
        if (path.includes('/review')) return 100
        return 0
    }

    const progress = getProgress()

    return (
        <div className="min-h-screen bg-canvas antialiased selection:bg-gold selection:text-white font-sans flex flex-col">
            {/* Progress Bar */}
            <div className="w-full h-1 bg-line fixed top-0 left-0 z-50">
                <div
                    className="h-full bg-aubergine transition-all duration-500 ease-out"
                    style={{ width: `${progress}%` }}
                />
            </div>

            {/* Top Bar with Save Status */}
            <div className="fixed top-4 right-6 z-40 flex items-center gap-2">
                <div className={clsx(
                    "w-2 h-2 rounded-full transition-colors duration-300",
                    isSaved ? "bg-green-500" : "bg-gold animate-pulse"
                )} />
                <span className="text-[10px] uppercase tracking-[0.2em] text-charcoal/40 font-medium">
                    {isSaved ? "Draft Saved" : "Saving..."}
                </span>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-12 md:py-20 w-full flex-grow">
                {/* Brand */}
                <div className="flex items-center gap-3 mb-16">
                    <div className="w-9 h-9 rounded-full border border-charcoal/20 flex items-center justify-center">
                        <span className="font-serif italic text-sm text-aubergine">Rf</span>
                    </div>
                    <div className="font-serif text-2xl font-semibold tracking-tight text-aubergine italic">
                        Raptor<span className="not-italic text-charcoal">flow</span>
                    </div>
                </div>

                {/* Two-column layout */}
                <div className={clsx('grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20', className)}>
                    {/* Left Editorial Column */}
                    <div className="flex flex-col justify-between">
                        <div>
                            {overline && (
                                <p className="text-[11px] tracking-[0.28em] uppercase text-gold mb-4">
                                    {overline}
                                </p>
                            )}
                            {heading && (
                                <h1 className="font-serif text-[2.5rem] md:text-[3.5rem] leading-[0.95] mb-6">
                                    {heading}
                                </h1>
                            )}
                            {description && (
                                <p className="text-sm md:text-base text-charcoal/70 leading-relaxed">
                                    {description}
                                </p>
                            )}
                        </div>

                        {/* Bottom Quote (desktop only) */}
                        {quote && (
                            <div className="hidden lg:block mt-12">
                                <p className="font-serif italic text-charcoal/60 text-sm">
                                    {quote}
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Right Form Column */}
                    <div>
                        {children}
                    </div>
                </div>
            </div>
        </div>
    )
}
