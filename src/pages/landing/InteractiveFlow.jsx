import React, { useRef, useState } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import { 
  MessageSquare, 
  Brain, 
  Rocket, 
  BarChart3,
  ArrowRight,
  CheckCircle2,
  Play
} from 'lucide-react'

// Step connector with animation
const StepConnector = ({ active }) => (
  <div className="hidden lg:flex items-center justify-center w-24 relative">
    <motion.div 
      className="h-px w-full bg-white/10"
      initial={{ scaleX: 0 }}
      animate={{ scaleX: 1 }}
      transition={{ duration: 0.6, delay: 0.3 }}
    />
    <motion.div 
      className={`absolute h-px bg-gradient-to-r from-amber-500 to-yellow-500 left-0 right-0`}
      initial={{ scaleX: 0 }}
      animate={{ scaleX: active ? 1 : 0 }}
      transition={{ duration: 0.8 }}
      style={{ transformOrigin: 'left' }}
    />
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: active ? 1 : 0.3, x: 0 }}
      transition={{ delay: 0.5 }}
      className="absolute"
    >
      <ArrowRight className={`w-4 h-4 ${active ? 'text-amber-400' : 'text-white/20'}`} />
    </motion.div>
  </div>
)

// Interactive step card
const StepCard = ({ step, index, isActive, onClick }) => {
  const Icon = step.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.15, duration: 0.6 }}
      onClick={onClick}
      className={`
        relative flex-1 min-w-[250px] cursor-pointer group
        ${isActive ? 'z-10' : 'z-0'}
      `}
    >
      {/* Card */}
      <motion.div
        animate={{ 
          scale: isActive ? 1.02 : 1,
          y: isActive ? -8 : 0
        }}
        transition={{ type: "spring", stiffness: 300, damping: 20 }}
        className={`
          relative p-6 rounded-2xl border transition-all duration-300
          ${isActive 
            ? 'bg-gradient-to-br from-amber-500/10 to-yellow-500/5 border-amber-500/30' 
            : 'bg-white/5 border-white/10 hover:border-white/20'
          }
        `}
      >
        {/* Step number */}
        <div className={`
          absolute -top-3 -left-3 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
          ${isActive 
            ? 'bg-gradient-to-br from-amber-500 to-yellow-500 text-black' 
            : 'bg-zinc-800 text-white/60 border border-white/10'
          }
        `}>
          {index + 1}
        </div>

        {/* Icon */}
        <div className={`
          w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-colors
          ${isActive 
            ? 'bg-amber-500/20' 
            : 'bg-white/5 group-hover:bg-white/10'
          }
        `}>
          <Icon className={`w-6 h-6 ${isActive ? 'text-amber-400' : 'text-white/40'}`} />
        </div>

        {/* Content */}
        <h3 className={`text-lg font-medium mb-2 ${isActive ? 'text-white' : 'text-white/80'}`}>
          {step.title}
        </h3>
        <p className={`text-sm leading-relaxed ${isActive ? 'text-white/60' : 'text-white/40'}`}>
          {step.description}
        </p>

        {/* Duration badge */}
        <div className={`
          mt-4 inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs
          ${isActive 
            ? 'bg-amber-500/20 text-amber-300' 
            : 'bg-white/5 text-white/40'
          }
        `}>
          <Play className="w-3 h-3" />
          {step.duration}
        </div>

        {/* Active glow */}
        {isActive && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 rounded-2xl bg-gradient-to-r from-amber-500/10 via-transparent to-yellow-500/10 blur-xl -z-10"
          />
        )}
      </motion.div>
    </motion.div>
  )
}

// Detail panel that appears below
const DetailPanel = ({ step }) => (
  <motion.div
    initial={{ opacity: 0, height: 0 }}
    animate={{ opacity: 1, height: 'auto' }}
    exit={{ opacity: 0, height: 0 }}
    transition={{ duration: 0.4 }}
    className="overflow-hidden"
  >
    <div className="pt-8 pb-4">
      <div className="max-w-3xl mx-auto bg-zinc-900/50 border border-white/10 rounded-2xl p-8">
        <div className="flex items-start gap-6">
          <div className="flex-1">
            <h4 className="text-xl font-medium text-white mb-4">{step.detailTitle}</h4>
            <p className="text-white/50 leading-relaxed mb-6">{step.detailDescription}</p>
            
            {/* Deliverables */}
            <div className="space-y-3">
              <span className="text-xs uppercase tracking-wider text-amber-400/60">What you get:</span>
              {step.deliverables.map((item, i) => (
                <div key={i} className="flex items-center gap-3 text-sm text-white/60">
                  <CheckCircle2 className="w-4 h-4 text-amber-400/60 flex-shrink-0" />
                  {item}
                </div>
              ))}
            </div>
          </div>

          {/* Visual */}
          <div className="hidden md:block w-64 h-48 bg-gradient-to-br from-amber-500/10 to-transparent rounded-xl border border-white/10 flex items-center justify-center">
            <step.icon className="w-16 h-16 text-amber-400/20" />
          </div>
        </div>
      </div>
    </div>
  </motion.div>
)

// Main InteractiveFlow component
const InteractiveFlow = () => {
  const sectionRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, margin: "-100px" })
  const [activeStep, setActiveStep] = useState(0)

  const steps = [
    {
      icon: MessageSquare,
      title: "Intake & Discovery",
      description: "Answer strategic questions. We extract your positioning, ICPs, and market context.",
      duration: "15 minutes",
      detailTitle: "The Strategic Intake",
      detailDescription: "Our AI-powered intake process asks the right questions to understand your business deeply. Positioning frameworks from Dan Kennedy and April Dunford. Market analysis. Competitor landscape. All synthesized into actionable intelligence.",
      deliverables: [
        "Positioning statement with clarity score",
        "3 distinct ICP profiles with fit scores",
        "Barrier classification for each ICP",
        "Protocol recommendations"
      ]
    },
    {
      icon: Brain,
      title: "AI Strategy Build",
      description: "Our agents analyze, score, and generate your complete GTM battle plan.",
      duration: "Instant",
      detailTitle: "The Intelligence Layer",
      detailDescription: "Multiple AI agents work in concert: ICPBuildAgent creates detailed profiles. BarrierEngine classifies obstacles. StrategyProfile recommends protocols. All using tiered Gemini models for optimal reasoning.",
      deliverables: [
        "Complete campaign architecture",
        "Move templates pre-loaded",
        "Asset briefs ready for Muse",
        "Metrics framework configured"
      ]
    },
    {
      icon: Rocket,
      title: "Launch Your Spike",
      description: "Activate your 30-day GTM sprint with guardrails and kill switches in place.",
      duration: "30 days",
      detailTitle: "The Execution Phase",
      detailDescription: "Your Spike is a focused 30-day GTM implant. Protocols activate. Moves execute. Assets deploy. All with automated guardrails that pause spend if metrics breach thresholds. No runaway budgets. No wasteful experiments.",
      deliverables: [
        "Weekly RAG status reviews",
        "Automated kill switch protection",
        "Revenue simulation tracking",
        "Real-time campaign adjustments"
      ]
    },
    {
      icon: BarChart3,
      title: "Measure & Iterate",
      description: "Track RAG metrics. Review performance. Learn and improve continuously.",
      duration: "Ongoing",
      detailTitle: "The Feedback Loop",
      detailDescription: "Every metric flows into your Matrix dashboard. See what's working, what's not, and why. The Pattern Library captures successful moves. Your next Spike starts smarter than the last.",
      deliverables: [
        "Comprehensive performance report",
        "Win/loss pattern analysis",
        "Updated ICP refinements",
        "Next Spike recommendations"
      ]
    }
  ]

  return (
    <section 
      ref={sectionRef}
      className="relative py-32 bg-black overflow-hidden"
    >
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
      </div>

      <div className="max-w-7xl mx-auto px-6 relative z-10">
        {/* Section header */}
        <div className="text-center mb-16">
          <motion.span
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            className="text-[10px] uppercase tracking-[0.4em] text-amber-400/60"
          >
            The Process
          </motion.span>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1, duration: 0.6 }}
            className="mt-6 text-4xl md:text-5xl font-light text-white"
          >
            From chaos to{' '}
            <span className="italic font-normal bg-gradient-to-r from-amber-200 via-yellow-100 to-amber-200 bg-clip-text text-transparent">
              command
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="mt-6 text-lg text-white/40 max-w-2xl mx-auto"
          >
            Four phases. One outcome: GTM clarity you can actually execute.
          </motion.p>
        </div>

        {/* Steps row */}
        <div className="flex flex-col lg:flex-row items-stretch justify-center gap-4 lg:gap-0">
          {steps.map((step, index) => (
            <React.Fragment key={index}>
              <StepCard
                step={step}
                index={index}
                isActive={activeStep === index}
                onClick={() => setActiveStep(index)}
              />
              {index < steps.length - 1 && (
                <StepConnector active={activeStep > index} />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Detail panel */}
        <AnimatePresence mode="wait">
          <DetailPanel key={activeStep} step={steps[activeStep]} />
        </AnimatePresence>

        {/* Progress indicator */}
        <div className="flex justify-center gap-2 mt-8">
          {steps.map((_, index) => (
            <button
              key={index}
              onClick={() => setActiveStep(index)}
              className={`
                w-2 h-2 rounded-full transition-all duration-300
                ${activeStep === index 
                  ? 'w-8 bg-amber-400' 
                  : 'bg-white/20 hover:bg-white/40'
                }
              `}
            />
          ))}
        </div>
      </div>
    </section>
  )
}

export default InteractiveFlow

