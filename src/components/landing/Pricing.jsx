import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Check, Zap } from 'lucide-react'
import { LuxeHeading, LuxeButton } from '../ui/PremiumUI'

const PricingCard = ({ tier, price, features, recommended, delay }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5, delay }}
        className={`relative p-8 rounded-3xl border ${recommended
                ? 'border-neutral-900 bg-neutral-900 text-white shadow-2xl scale-105 z-10'
                : 'border-neutral-200 bg-white text-neutral-900 hover:border-neutral-300'
            } flex flex-col h-full`}
    >
        {recommended && (
            <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-amber-200 to-yellow-400 text-neutral-900 text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full flex items-center gap-1 shadow-lg">
                <Zap className="w-3 h-3 fill-neutral-900" /> Most Popular
            </div>
        )}

        <div className="mb-8">
            <h3 className={`font-serif text-2xl font-bold mb-2 ${recommended ? 'text-white' : 'text-neutral-900'}`}>{tier}</h3>
            <div className="flex items-baseline gap-1">
                <span className="text-4xl font-black tracking-tight">${price}</span>
                <span className={`text-sm ${recommended ? 'text-neutral-400' : 'text-neutral-500'}`}>/month</span>
            </div>
        </div>

        <ul className="space-y-4 mb-8 flex-1">
            {features.map((feature, i) => (
                <li key={i} className="flex items-start gap-3">
                    <div className={`mt-0.5 min-w-[20px] h-5 w-5 rounded-full flex items-center justify-center ${recommended ? 'bg-neutral-800 text-green-400' : 'bg-green-100 text-green-600'
                        }`}>
                        <Check className="w-3 h-3" />
                    </div>
                    <span className={`text-sm leading-relaxed ${recommended ? 'text-neutral-300' : 'text-neutral-600'}`}>
                        {feature}
                    </span>
                </li>
            ))}
        </ul>

        <LuxeButton
            variant={recommended ? 'secondary' : 'primary'}
            className="w-full justify-center"
        >
            Get Started
        </LuxeButton>
    </motion.div>
)

export const Pricing = () => {
    const [isAnnual, setIsAnnual] = useState(true)

    return (
        <section className="py-32 bg-neutral-50">
            <div className="mx-auto max-w-7xl px-6">
                <div className="text-center mb-12">
                    <LuxeHeading level={2} className="mb-6">
                        Simple, Transparent Pricing
                    </LuxeHeading>
                    <p className="text-xl text-neutral-600 mb-8">
                        Start free, upgrade as you grow. No hidden fees.
                    </p>

                    <div className="flex items-center justify-center gap-4 mb-12">
                        <span className={`text-sm font-medium ${!isAnnual ? 'text-neutral-900' : 'text-neutral-500'}`}>Monthly</span>
                        <button
                            onClick={() => setIsAnnual(!isAnnual)}
                            className="relative w-14 h-8 bg-neutral-200 rounded-full p-1 transition-colors duration-300 focus:outline-none"
                        >
                            <motion.div
                                animate={{ x: isAnnual ? 24 : 0 }}
                                className="w-6 h-6 bg-white rounded-full shadow-sm"
                            />
                        </button>
                        <span className={`text-sm font-medium ${isAnnual ? 'text-neutral-900' : 'text-neutral-500'}`}>
                            Annual <span className="text-green-600 font-bold ml-1">(Save 20%)</span>
                        </span>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                    <PricingCard
                        tier="Starter"
                        price={isAnnual ? "29" : "39"}
                        features={[
                            "Up to 1,000 active users",
                            "Basic Cohort Analysis",
                            "3 Active Campaigns",
                            "Email Support",
                            "1 Team Member"
                        ]}
                        delay={0.1}
                    />
                    <PricingCard
                        tier="Growth"
                        price={isAnnual ? "79" : "99"}
                        recommended={true}
                        features={[
                            "Up to 10,000 active users",
                            "Advanced Behavioral Cohorts",
                            "Unlimited Campaigns",
                            "Priority Support",
                            "5 Team Members",
                            "ROI Calculator",
                            "Custom Integrations"
                        ]}
                        delay={0.2}
                    />
                    <PricingCard
                        tier="Scale"
                        price={isAnnual ? "199" : "249"}
                        features={[
                            "Unlimited active users",
                            "Predictive AI Insights",
                            "Dedicated Success Manager",
                            "24/7 Phone Support",
                            "Unlimited Team Members",
                            "White-label Reports",
                            "API Access"
                        ]}
                        delay={0.3}
                    />
                </div>
            </div>
        </section>
    )
}
