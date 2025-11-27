import React from 'react'
import { motion } from 'framer-motion'
import { LuxeHeading } from '../ui/PremiumUI'

const Testimonial = ({ quote, author, role }) => (
    <div className="flex flex-col gap-6">
        <h3 className="font-serif text-3xl md:text-4xl leading-tight font-light">
            "{quote}"
        </h3>
        <div>
            <div className="font-bold text-sm tracking-wide uppercase">{author}</div>
            <div className="text-neutral-500 text-sm font-light">{role}</div>
        </div>
    </div>
)

export const TestimonialsInfinite = () => {
    return (
        <section className="py-32 bg-neutral-50 border-t border-black/5">
            <div className="mx-auto max-w-[1400px] px-6 md:px-12">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-20 items-center">
                    <div>
                        <span className="font-mono text-xs uppercase tracking-widest text-neutral-400 mb-4 block">Endorsements</span>
                        <LuxeHeading level={2} className="mb-8">
                            Trusted by the <br />
                            <span className="italic font-light text-neutral-500">Visionaries.</span>
                        </LuxeHeading>
                    </div>

                    <div className="space-y-20">
                        <Testimonial
                            quote="RaptorFlow stripped away the noise. Now we just execute."
                            author="Sarah Jenkins"
                            role="CEO, GrowthAgency"
                        />
                        <div className="h-px w-full bg-black/10" />
                        <Testimonial
                            quote="The most elegant piece of software we use. Period."
                            author="Michael Chen"
                            role="Founder, TechStart"
                        />
                    </div>
                </div>
            </div>
        </section>
    )
}
