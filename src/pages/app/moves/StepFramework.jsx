import { useMemo, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    PROBLEM_TYPES,
    getFrameworkRecommendations
} from '../../../data/frameworkConfigs'
import { BrandIcon } from '@/components/brand/BrandSystem'
import { ChevronRight, Clock, FileText, Check, AlertTriangle, Target } from 'lucide-react'

/**
 * Step 3: Recommended Modes (Frameworks)
 */

const FrameworkCard = ({ framework, rank, isSelected, onSelect, onPreview }) => {
    const fitScore = framework.fitScore || 0
    const fitLevel = fitScore >= 80 ? 'excellent' : fitScore >= 60 ? 'good' : 'okay'

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: rank * 0.1 }}
            className={`
        relative p-5 rounded-2xl border transition-all duration-200 flex flex-col h-full
        ${isSelected
                    ? 'border-primary bg-primary/5 shadow-md ring-1 ring-primary/20'
                    : 'border-border hover:border-primary/30 bg-card hover:bg-muted/20'
                }
      `}
        >
            {/* Clickable Area Overlay for Selection */}
            <div className="absolute inset-0 z-0 cursor-pointer rounded-2xl" onClick={onSelect} />

            {/* Rank badge */}
            {rank === 0 && (
                <div className="absolute -top-2.5 left-4 px-2.5 py-0.5 bg-primary text-primary-foreground text-[10px] font-bold rounded-full uppercase tracking-wider z-10">
                    Best Match
                </div>
            )}

            {/* Selected check */}
            {isSelected && (
                <div className="absolute top-3 right-3 z-10">
                    <div className="w-5 h-5 bg-primary rounded-full flex items-center justify-center">
                        <Check className="w-3 h-3 text-primary-foreground" strokeWidth={3} />
                    </div>
                </div>
            )}

            {/* Header */}
            <div className="flex items-center gap-3 mb-3 z-10 pointer-events-none">
                <div className={`
          w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0
          ${isSelected ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'}
        `}>
                    <BrandIcon name="speed" size={20} />
                </div>

                <div className="min-w-0">
                    <h3 className="font-serif text-lg font-medium text-foreground leading-tight">
                        {framework.name}
                    </h3>
                    <div className={`
                        inline-flex items-center gap-1 text-xs font-medium mt-0.5
                        ${fitLevel === 'excellent' ? 'text-emerald-600' : 'text-amber-600'}
                    `}>
                        {fitScore}% Fit
                    </div>
                </div>
            </div>

            <p className="text-sm text-muted-foreground mb-4 line-clamp-2 min-h-[40px] z-10 pointer-events-none">
                {framework.subtitle}
            </p>

            {/* Meta info */}
            <div className="flex items-center gap-4 py-3 border-t border-border mt-auto z-10 pointer-events-none">
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Clock className="w-3.5 h-3.5" />
                    {framework.defaultDuration}d
                </div>
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Target className="w-3.5 h-3.5" />
                    <span className="truncate max-w-[80px]">{framework.metrics.primary.name}</span>
                </div>
            </div>

            {/* Actions */}
            <div className="mt-3 flex gap-2 z-10 relative">
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        onPreview();
                    }}
                    className="flex-1 flex items-center justify-center gap-1 py-2 rounded-lg bg-muted/50 hover:bg-muted text-xs font-medium transition-colors"
                >
                    View Details
                </button>
            </div>
        </motion.div>
    )
}

// Preview drawer
const PreviewDrawer = ({ framework, open, onClose, onSelect }) => {
    if (!framework) return null

    return (
        <AnimatePresence>
            {open && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/40 z-50 backdrop-blur-sm"
                    />

                    {/* Drawer */}
                    <motion.div
                        initial={{ x: '100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '100%' }}
                        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                        className="fixed right-0 top-0 bottom-0 w-full max-w-lg bg-background border-l border-border z-50 overflow-y-auto shadow-2xl"
                    >
                        <div className="p-6 md:p-8">
                            <div className="flex items-center justify-between mb-8">
                                <div>
                                    <h2 className="font-serif text-2xl text-foreground mb-1">
                                        {framework.name}
                                    </h2>
                                    <p className="text-muted-foreground">{framework.expert}</p>
                                </div>
                                <button
                                    onClick={onClose}
                                    className="p-2 text-muted-foreground hover:bg-muted rounded-full transition-colors"
                                >
                                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>

                            {/* Why this fits */}
                            <div className="mb-8 p-4 bg-emerald-500/5 rounded-xl border border-emerald-500/10">
                                <h4 className="text-xs font-bold text-emerald-600 uppercase tracking-wide mb-3 flex items-center gap-2">
                                    <Check className="w-4 h-4" /> Why this is a match
                                </h4>
                                <ul className="space-y-2">
                                    {getWhyFits(framework).map((reason, idx) => (
                                        <li key={idx} className="flex items-start gap-2 text-sm text-foreground">
                                            <span>•</span>
                                            {reason}
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            {/* Duration and timeline */}
                            <section className="mb-8">
                                <h3 className="text-sm font-bold text-foreground uppercase tracking-wide mb-4">Timeline</h3>
                                <div className="p-0 rounded-xl">
                                    <div className="space-y-3 pl-2 border-l-2 border-muted">
                                        {framework.dailyActions.templates.slice(0, 14).map((action, idx) => (
                                            <div key={idx} className="relative flex items-start gap-4 text-sm group">
                                                <div className="absolute -left-[13px] top-1.5 w-2 h-2 rounded-full bg-muted group-hover:bg-primary transition-colors" />
                                                <span className="w-8 font-medium text-muted-foreground shrink-0 pt-0.5">D{action.day}</span>
                                                <span className="text-foreground leading-relaxed">{action.task}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </section>

                            <div className="grid grid-cols-2 gap-8 mb-8">
                                {/* Deliverables */}
                                <section>
                                    <h3 className="text-sm font-bold text-foreground uppercase tracking-wide mb-4">Deliverables</h3>
                                    <div className="space-y-2">
                                        {framework.outputs.deliverables.map((deliverable) => (
                                            <div
                                                key={deliverable.id}
                                                className="flex items-center gap-2 p-2 rounded-lg bg-muted/30 border border-border/50 text-sm"
                                            >
                                                <FileText className="w-3.5 h-3.5 text-muted-foreground" />
                                                <span className="text-foreground truncate">{deliverable.name}</span>
                                            </div>
                                        ))}
                                    </div>
                                </section>

                                {/* Rules */}
                                <section>
                                    <h3 className="text-sm font-bold text-foreground uppercase tracking-wide mb-4">Critical Rules</h3>
                                    <div className="space-y-2">
                                        {framework.rules.required.map((rule) => (
                                            <div
                                                key={rule.id}
                                                className="flex items-center gap-2 p-2 rounded-lg bg-muted/30 border border-border/50 text-sm"
                                            >
                                                <Check className="w-3.5 h-3.5 text-primary" />
                                                <span className="text-foreground truncate">{rule.label}</span>
                                            </div>
                                        ))}
                                    </div>
                                </section>
                            </div>

                            {/* Tradeoffs */}
                            <div className="mb-8">
                                <h4 className="text-xs font-bold text-amber-600 uppercase tracking-wide mb-3 flex items-center gap-2">
                                    <AlertTriangle className="w-4 h-4" /> Tradeoffs
                                </h4>
                                <ul className="space-y-2">
                                    {getTradeoffs(framework).map((tradeoff, idx) => (
                                        <li key={idx} className="flex items-start gap-2 text-sm text-muted-foreground">
                                            <span>•</span>
                                            {tradeoff}
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <button
                                onClick={() => {
                                    onSelect(); // Selects the framework
                                    onClose(); // Closes drawer
                                }}
                                className="w-full py-4 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-90 transition-opacity"
                            >
                                Select {framework.name} Framework
                            </button>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    )
}

// Helper functions for why fits / tradeoffs
const getWhyFits = (framework) => {
    const reasons = []

    if (framework.defaultDuration <= 7) {
        reasons.push('Fast results in just 7 days')
    }
    if (framework.channels.recommended.includes('linkedin')) {
        reasons.push('Works great on LinkedIn')
    }
    if (framework.outputs.deliverables.length <= 4) {
        reasons.push('Focused output, not overwhelming')
    }
    if (framework.metrics.primary.type === 'percentage') {
        reasons.push('Clear, measurable outcomes')
    }

    // Add framework-specific reasons
    switch (framework.id) {
        case 'kennedy':
            reasons.push('Direct response for fast conversions')
            reasons.push('Perfect for warm audience')
            break
        case 'ogilvy':
            reasons.push('Builds long-term credibility')
            reasons.push('Research-backed authority')
            break
        case 'godin':
            reasons.push('Ideal for standing out')
            reasons.push('Organic word-of-mouth growth')
            break
        default:
            reasons.push('Proven framework with clear steps')
    }

    return reasons.slice(0, 4)
}

const getTradeoffs = (framework) => {
    const tradeoffs = []

    if (framework.defaultDuration <= 7) {
        tradeoffs.push('Requires intense focus for 7 days')
    }
    if (framework.rules.required.some(r => r.id.includes('urgency'))) {
        tradeoffs.push('May feel salesy to some audiences')
    }
    if (framework.defaultDuration >= 14) {
        tradeoffs.push('Requires patience')
    }

    // Add framework-specific tradeoffs
    switch (framework.id) {
        case 'kennedy':
            tradeoffs.push('Aggressive approach not for everyone')
            break
        case 'ogilvy':
            tradeoffs.push('Needs significant research time')
            break
        case 'godin':
            tradeoffs.push('Must be truly remarkable to spread')
            break
        default:
            tradeoffs.push('Requires commitment to the process')
    }

    return tradeoffs.slice(0, 2)
}

const StepFramework = ({ data, updateData }) => {
    const [previewFramework, setPreviewFramework] = useState(null)

    // Get recommendations based on problem + situation
    const recommendations = useMemo(() => {
        if (!data.problemType) return []
        return getFrameworkRecommendations(data.problemType, data.situation, 4)
    }, [data.problemType, data.situation])

    const problemInfo = data.problemType ? PROBLEM_TYPES[data.problemType] : null

    return (
        <div className="max-w-6xl mx-auto pb-12">
            {/* Header */}
            <div className="text-center mb-8">
                <h1 className="font-serif text-2xl text-foreground mb-2">
                    Choose your approach
                </h1>
                <p className="text-sm text-muted-foreground max-w-lg mx-auto">
                    We found {recommendations.length} frameworks that match your situation.
                </p>
            </div>

            {/* Framework cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-fr">
                {recommendations.map((framework, index) => (
                    <FrameworkCard
                        key={framework.id}
                        framework={framework}
                        rank={index}
                        isSelected={data.selectedFramework?.id === framework.id}
                        onSelect={() => updateData('selectedFramework', framework)}
                        onPreview={() => setPreviewFramework(framework)}
                    />
                ))}
            </div>

            {/* Empty state */}
            {recommendations.length === 0 && (
                <div className="text-center py-12">
                    <p className="text-muted-foreground">
                        Please select a problem type first.
                    </p>
                </div>
            )}

            {/* Preview drawer */}
            <PreviewDrawer
                framework={previewFramework}
                open={!!previewFramework}
                onClose={() => setPreviewFramework(null)}
                onSelect={() => updateData('selectedFramework', previewFramework)}
            />
        </div>
    )
}

export default StepFramework
