import { useState, useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { Check, X } from 'lucide-react'
import useReducedMotion from '../hooks/useReducedMotion'
import { ANIMATION } from '../lib/animations'

/**
 * Tiered Pricing Component
 * Three-tier pricing with emphasized middle tier (Glide)
 */
export default function TieredPricing() {
    const prefersReducedMotion = useReducedMotion()

    const plans = [
        {
            name: 'Stumble',
            price: '0',
            desc: 'For those who want to try failing on their own first.',
            features: [
                '3 moves per week',
                '1 active cohort',
                'Basic strategy templates',
                'No community access'
            ],
            cta: 'Start Stumbling',
            popular: false,
            color: 'border-gray-200'
        },
        {
            name: 'Glide',
            price: '49',
            desc: 'The sweet spot. Enough constraints to actually ship.',
            features: [
                'Unlimited moves',
                '7 active cohorts',
                'Full strategy library',
                'Weekly accountability',
                'Priority support'
            ],
            cta: 'Start Gliding',
            popular: true,
            color: 'border-black'
        },
        {
            name: 'Soar',
            price: '199',
            desc: 'For agencies who need to manage multiple client workspaces.',
            features: [
                'Everything in Glide',
                '5 workspaces',
                'White-label reports',
                'Team permissions',
                'Dedicated account manager'
            ],
            cta: 'Start Soaring',
            popular: false,
            color: 'border-gray-200'
        }
    ]

    return (
        <div className="grid gap-8 lg:grid-cols-3 max-w-7xl mx-auto items-center">
            {plans.map((plan, i) => (
                <PricingCard key={i} plan={plan} index={i} prefersReducedMotion={prefersReducedMotion} />
            ))}
        </div>
    )
}

function PricingCard({ plan, index, prefersReducedMotion }) {
    const isPopular = plan.popular

    return (
        <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.1, duration: 0.5 }}
            whileHover={{
                y: isPopular ? -24 : -12,
                transition: { duration: 0.3 }
            }}
            className={`relative flex flex-col p-8 rounded-2xl bg-white border-2 transition-all duration-300 ${isPopular
                    ? 'border-black shadow-2xl z-10 lg:-my-8 lg:py-12'
                    : 'border-black/5 shadow-lg lg:py-8'
                }`}
        >
            {isPopular && (
                <div className="absolute -top-5 left-1/2 -translate-x-1/2">
                    <div className="relative">
                        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 blur opacity-70 animate-pulse" />
                        <span className="relative block px-4 py-1.5 rounded-full bg-black text-white text-xs font-bold uppercase tracking-widest">
                            Most Popular
                        </span>
                    </div>
                </div>
            )}

            <div className="mb-8">
                <h3 className="font-serif text-2xl font-bold mb-2">{plan.name}</h3>
                <p className="text-gray-500 text-sm min-h-[40px]">{plan.desc}</p>
            </div>

            <div className="mb-8 flex items-baseline gap-1">
                <span className="text-5xl font-black tracking-tight">${plan.price}</span>
                <span className="text-gray-500">/mo</span>
            </div>

            <ul className="space-y-4 mb-8 flex-1">
                {plan.features.map((feature, j) => (
                    <li key={j} className="flex items-start gap-3 text-sm">
                        <div className={`mt-0.5 flex h-5 w-5 items-center justify-center rounded-full ${isPopular ? 'bg-black text-white' : 'bg-gray-100 text-gray-500'}`}>
                            <Check className="h-3 w-3" strokeWidth={3} />
                        </div>
                        <span className="text-gray-700">{feature}</span>
                    </li>
                ))}
            </ul>

            <button
                className={`w-full py-4 rounded-xl font-bold transition-all duration-300 ${isPopular
                        ? 'bg-black text-white hover:bg-gray-800 hover:scale-[1.02] shadow-lg hover:shadow-xl'
                        : 'bg-gray-100 text-black hover:bg-gray-200'
                    }`}
            >
                {plan.cta}
            </button>
        </motion.div>
    )
}
