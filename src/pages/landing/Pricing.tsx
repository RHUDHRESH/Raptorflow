import React, { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import { ArrowRight, Check, X } from 'lucide-react'

/* ═══════════════════════════════════════════════════════════════════════════
   PRICING - "WAR ROOM" EDITION (DARK MODE)
   Tactical, high-contrast, premium glassmorphism.
   ═══════════════════════════════════════════════════════════════════════════ */

// Custom Premium Art for Plans (Nanobana Style - Dark Mode Inverted)

// 1. Sprouting Plant (Starter/Ascent)
const PlantIcon = ({ className = '' }) => (
  <svg viewBox="0 0 48 48" fill="none" className={className}>
    <path d="M24 44V20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    <path d="M24 38C24 38 34 36 34 26C34 19 28 18 24 24" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M24 32C24 32 14 30 14 20C14 13 20 12 24 18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M24 20C24 20 20 14 22 10C24 6 26 8 26 12C26 14 24 20 24 20Z" fill="currentColor" fillOpacity="0.1" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    <circle cx="20" cy="14" r="1.5" fill="currentColor" fillOpacity="0.8" />
    <path d="M16 42H32" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" opacity="0.3" />
    {/* Glow */}
    <circle cx="24" cy="20" r="12" fill="currentColor" fillOpacity="0.05" style={{ filter: 'blur(10px)' }} />
  </svg>
)

// 2. Mountain (Glide/Growth)
const MountainIcon = ({ className = '' }) => (
  <svg viewBox="0 0 48 48" fill="none" className={className}>
    <path d="M4 40L20 12L32 30" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M24 26L34 10L44 40" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M20 12L24 18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M4 40H44" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    <circle cx="34" cy="10" r="2" fill="currentColor" />
    <path d="M30 16L34 10L36 14" fill="currentColor" fillOpacity="0.2" />
    <circle cx="10" cy="8" r="1" fill="currentColor" fillOpacity="0.4" />
    {/* Summit glow */}
    <circle cx="34" cy="10" r="8" fill="currentColor" fillOpacity="0.1" />
  </svg>
)

// 3. Flying Rocket (Soar/Scale)
const RocketIcon = ({ className = '' }) => (
  <svg viewBox="0 0 48 48" fill="none" className={className}>
    <path d="M24 6C24 6 18 16 18 24C18 30 20 34 24 34C28 34 30 30 30 24C30 16 24 6 24 6Z" fill="currentColor" fillOpacity="0.1" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    <path d="M18 24L14 28V34L18 32" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M30 24L34 28V34L30 32" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M24 34V40" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    <path d="M24 40L22 44M24 40L26 44" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    <circle cx="24" cy="18" r="3" fill="currentColor" fillOpacity="0.3" />
    {/* Motion lines - stylized exhaust */}
    <path d="M24 44L24 54" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeDasharray="2 4" opacity="0.5" />
    {/* Engine glow */}
    <circle cx="24" cy="24" r="14" fill="currentColor" fillOpacity="0.05" />
  </svg>
)

const CheckIcon = ({ className = '' }) => (
  <svg viewBox="0 0 16 16" fill="none" className={className}>
    <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1" />
    <path d="M5 8L7 10L11 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

// Pricing Card Component
const PricingCard = ({ plan, index, onSelect, highlighted = false }) => {
  const ref = useRef(null)

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ delay: index * 0.1, duration: 0.5 }}
      className={`relative group h-full flex flex-col ${highlighted ? 'lg:-mt-4 lg:mb-4' : ''}`}
    >
      {highlighted && (
        <div className="absolute -inset-px bg-gradient-to-b from-zinc-900/15 to-zinc-900/5 rounded-2xl blur-md opacity-75 group-hover:opacity-100 transition-opacity" />
      )}

      {/* Card Content */}
      <div className={`
        relative h-full flex flex-col p-8 rounded-2xl border transition-all duration-300
        ${highlighted
          ? 'bg-card border-primary/40 shadow-xl shadow-primary/10'
          : 'bg-card/50 border-border hover:border-primary/50 hover:bg-card hover:shadow-lg'
        }
      `}>
        {/* Badge */}
        {plan.badge && (
          <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-zinc-900 text-white text-[10px] uppercase tracking-[0.15em] font-bold rounded-full shadow-lg">
            {plan.badge}
          </div>
        )}

        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <h3 className={`text-2xl font-medium mb-1 text-foreground`}>{plan.name}</h3>
            <p className="text-xs text-muted-foreground uppercase tracking-wider">{plan.tagline}</p>
          </div>
          <div className={`w-12 h-12 flex items-center justify-center rounded-xl bg-muted ${highlighted ? 'text-zinc-900' : 'text-muted-foreground'}`}>

            <plan.icon className="w-8 h-8" />
          </div>
        </div>

        {/* Price */}
        <div className="mb-8">
          <div className="flex items-baseline gap-1">
            <span className={`text-5xl font-light tracking-tight text-foreground`}>
              {plan.priceDisplay || `₹${plan.price.toLocaleString('en-IN')}`}
            </span>
            <span className="text-sm text-muted-foreground font-medium ml-2">/ month</span>
          </div>
        </div>

        {/* Divider */}
        <div className="h-px w-full bg-border mb-8" />

        {/* Features */}
        <ul className="space-y-4 mb-8 flex-grow">
          {plan.features.map((feature, i) => (
            <li key={i} className="flex items-start gap-3">
              <Check className={`w-4 h-4 mt-0.5 flex-shrink-0 ${highlighted ? 'text-zinc-700' : 'text-muted-foreground'}`} />
              <span className={`text-sm text-muted-foreground`}>{feature}</span>
            </li>
          ))}
        </ul>

        {/* CTA */}
        <button
          onClick={onSelect}
          className={`
            w-full py-4 text-sm font-bold uppercase tracking-wider rounded-xl flex items-center justify-center gap-2 group/btn transition-all
            ${highlighted
              ? 'bg-zinc-900 text-white hover:bg-black'
              : 'bg-muted text-muted-foreground border border-border hover:bg-muted/80 hover:text-foreground'
            }
          `}
        >
          <span>Select Plan</span>
          <ArrowRight className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
        </button>
      </div>
    </motion.div>
  )
}

import { PLANS, PLAN_ORDER, COMPARISON_FEATURES } from '@/config/plans'

const Pricing = () => {
  const navigate = useNavigate()
  const [showMatrix, setShowMatrix] = useState(false)

  // Map plan IDs to icons
  const planIcons = {
    ascent: PlantIcon,
    glide: MountainIcon,
    soar: RocketIcon
  }

  const plans = PLAN_ORDER.map(id => ({
    ...PLANS[id],
    icon: planIcons[id],
    highlighted: PLANS[id].recommended || false,
    badge: PLANS[id].recommended ? 'RECOMMENDED' : undefined
  }))

  return (
    <section id="pricing" className="relative py-32 overflow-hidden bg-background">

      {/* Light Tactical Background */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Grid */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(0,0,0,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(0,0,0,0.02)_1px,transparent_1px)] bg-[size:40px_40px]" />
      </div>

      <div className="container-editorial relative z-10 max-w-7xl mx-auto px-6">
        <div className="text-center mb-24">
          <h2 className="text-4xl md:text-6xl font-serif text-foreground mb-6">
            Simple <span className="text-zinc-900 font-medium">Growth</span> Pricing.
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            ROI measured in days, not quarters. Pick your engine and start scaling.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <PricingCard key={index} plan={plan} index={index} highlighted={plan.highlighted} onSelect={() => navigate('/app')} />
          ))}
        </div>

        {/* Feature Matrix Toggle */}
        <div className="mt-20 text-center">
          <button
            onClick={() => setShowMatrix(!showMatrix)}
            className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-zinc-900 transition-colors uppercase tracking-widest font-bold"
          >
            {showMatrix ? 'Hide Full Comparison' : 'View Full Comparison'}
            <ArrowRight className={`w-4 h-4 transition-transform ${showMatrix ? 'rotate-90' : ''}`} />
          </button>
        </div>

        {/* Animated Feature Matrix */}
        <AnimatePresence>
          {showMatrix && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-12 bg-card border border-border rounded-2xl p-8 shadow-sm overflow-x-auto">
                <table className="w-full text-left min-w-[600px]">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="pb-4 text-xs uppercase text-muted-foreground font-bold">Feature</th>
                      <th className="pb-4 text-center text-xs uppercase text-muted-foreground font-medium">Ascent</th>
                      <th className="pb-4 text-center text-xs uppercase text-zinc-900 font-bold">Glide</th>
                      <th className="pb-4 text-center text-xs uppercase text-muted-foreground font-medium">Soar</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {[
                      ['Matrix Access', true, true, true],
                      ['Active Campaigns', '3', '6', '9'],
                      ['Moves / month', '20', '60', '150'],
                      ['Muse Generations / mo', '60', '200', '700'],
                      ['Lab Duels / mo', '8', '25', '80'],
                      ['Radar Scans / day', '3', '6', '15'],
                      ['Team Seats', '1', '2', '5'],
                      ['Support Level', 'Email', 'Priority', 'Dedicated']
                    ].map((row, i) => (
                      <tr key={i} className="group hover:bg-muted/50 transition-colors">
                        <td className="py-4 text-foreground text-sm font-medium">{row[0]}</td>
                        <td className="py-4 text-center text-muted-foreground text-sm">
                          {typeof row[1] === 'boolean'
                            ? (row[1] ? <Check className="w-4 h-4 text-emerald-500 mx-auto" /> : <X className="w-4 h-4 text-muted-foreground mx-auto" opacity={0.3} />)
                            : row[1]}
                        </td>
                        <td className="py-4 text-center text-foreground text-sm font-bold">
                          {typeof row[2] === 'boolean'
                            ? (row[2] ? <Check className="w-4 h-4 text-zinc-900 mx-auto" /> : <X className="w-4 h-4 text-muted-foreground mx-auto" opacity={0.3} />)
                            : row[2]}
                        </td>
                        <td className="py-4 text-center text-muted-foreground text-sm">
                          {typeof row[3] === 'boolean'
                            ? (row[3] ? <Check className="w-4 h-4 text-zinc-600 mx-auto" /> : <X className="w-4 h-4 text-muted-foreground mx-auto" opacity={0.3} />)
                            : row[3]}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </section>
  )
}

export default Pricing

