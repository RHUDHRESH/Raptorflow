/**
 * Creative Brief Card
 * 
 * Displays auto-generated creative briefs from Moves with full strategic context.
 * Shows positioning, cohort intelligence, journey context, and asset requirements.
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    FileText,
    Target,
    Users,
    TrendingUp,
    Sparkles,
    Download,
    Copy,
    ChevronDown,
    ChevronUp,
    CheckCircle2,
    AlertCircle,
    Zap
} from 'lucide-react';
import { cn } from '../../../utils/cn';

export function CreativeBriefCard({ brief, onUseForAsset }) {
    const [isExpanded, setIsExpanded] = useState(false);
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        // Copy brief as markdown
        const markdown = generateMarkdown(brief);
        await navigator.clipboard.writeText(markdown);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handleDownload = () => {
        const markdown = generateMarkdown(brief);
        const blob = new Blob([markdown], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `creative-brief-${brief.move_id}.md`;
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-2xl border border-neutral-200 bg-white shadow-sm overflow-hidden"
        >
            {/* Header */}
            <div className="p-6 border-b border-neutral-100">
                <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-100">
                            <FileText className="w-5 h-5 text-purple-600" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-neutral-900">Creative Brief</h3>
                            <p className="text-xs text-neutral-500">
                                {brief.campaign_context?.name || 'From Move'}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        <button
                            onClick={handleCopy}
                            className="p-2 text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors"
                            title="Copy as markdown"
                        >
                            {copied ? (
                                <CheckCircle2 className="w-4 h-4 text-green-600" />
                            ) : (
                                <Copy className="w-4 h-4" />
                            )}
                        </button>
                        <button
                            onClick={handleDownload}
                            className="p-2 text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors"
                            title="Download brief"
                        >
                            <Download className="w-4 h-4" />
                        </button>
                        <button
                            onClick={() => setIsExpanded(!isExpanded)}
                            className="p-2 text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors"
                        >
                            {isExpanded ? (
                                <ChevronUp className="w-4 h-4" />
                            ) : (
                                <ChevronDown className="w-4 h-4" />
                            )}
                        </button>
                    </div>
                </div>

                {/* Single-Minded Proposition */}
                <div className="bg-neutral-50 rounded-xl p-4 border border-neutral-200">
                    <div className="flex items-center gap-2 mb-2">
                        <Target className="w-4 h-4 text-neutral-600" />
                        <span className="text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                            Single-Minded Proposition
                        </span>
                    </div>
                    <p className="text-lg font-semibold text-neutral-900 leading-relaxed">
                        {brief.single_minded_proposition}
                    </p>
                </div>

                {/* Key Message */}
                <div className="mt-4">
                    <p className="text-sm text-neutral-600 mb-1">Key Message</p>
                    <p className="text-sm text-neutral-900 font-medium">
                        {brief.key_message}
                    </p>
                </div>

                {/* Journey Context */}
                <div className="mt-4 flex items-center gap-2 text-xs text-neutral-600">
                    <TrendingUp className="w-4 h-4" />
                    <span>
                        {brief.journey_context.from_stage} → {brief.journey_context.to_stage}
                    </span>
                </div>
            </div>

            {/* Expanded Content */}
            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                    >
                        <div className="p-6 space-y-6">
                            {/* Target Audience */}
                            <div>
                                <div className="flex items-center gap-2 mb-3">
                                    <Users className="w-4 h-4 text-neutral-600" />
                                    <h4 className="font-semibold text-neutral-900">Target Audience</h4>
                                </div>
                                <div className="bg-neutral-50 rounded-xl p-4 space-y-3">
                                    <div>
                                        <p className="text-sm font-semibold text-neutral-900">
                                            {brief.target_cohort_context.name}
                                        </p>
                                        <p className="text-xs text-neutral-600 mt-1">
                                            {brief.target_cohort_context.description}
                                        </p>
                                    </div>

                                    {/* Decision Criteria */}
                                    {brief.target_cohort_context.decision_criteria?.length > 0 && (
                                        <div>
                                            <p className="text-xs font-semibold text-neutral-700 mb-2">
                                                What They Care About:
                                            </p>
                                            <div className="space-y-1">
                                                {brief.target_cohort_context.decision_criteria
                                                    .sort((a, b) => b.weight - a.weight)
                                                    .slice(0, 3)
                                                    .map((criterion, i) => (
                                                        <div key={i} className="flex items-center gap-2">
                                                            <div className="w-12 h-1.5 bg-neutral-200 rounded-full overflow-hidden">
                                                                <div
                                                                    className="h-full bg-purple-500 rounded-full"
                                                                    style={{ width: `${criterion.weight * 100}%` }}
                                                                />
                                                            </div>
                                                            <span className="text-xs text-neutral-700">
                                                                {criterion.criterion}
                                                            </span>
                                                            {criterion.deal_breaker && (
                                                                <AlertCircle className="w-3 h-3 text-red-500" />
                                                            )}
                                                        </div>
                                                    ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Objections */}
                                    {brief.target_cohort_context.objection_map?.length > 0 && (
                                        <div>
                                            <p className="text-xs font-semibold text-neutral-700 mb-2">
                                                Objections to Address:
                                            </p>
                                            <div className="space-y-2">
                                                {brief.target_cohort_context.objection_map.slice(0, 2).map((obj, i) => (
                                                    <div key={i} className="text-xs">
                                                        <p className="text-neutral-900 font-medium">
                                                            "{obj.objection}"
                                                        </p>
                                                        <p className="text-neutral-600 mt-1">
                                                            → {obj.response}
                                                        </p>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Tone and Manner */}
                            <div>
                                <h4 className="font-semibold text-neutral-900 mb-2">Tone & Manner</h4>
                                <p className="text-sm text-neutral-700 bg-neutral-50 rounded-xl p-4">
                                    {brief.tone_and_manner}
                                </p>
                            </div>

                            {/* Mandatories & No-Gos */}
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <div className="flex items-center gap-2 mb-2">
                                        <CheckCircle2 className="w-4 h-4 text-green-600" />
                                        <h4 className="font-semibold text-neutral-900">Mandatories</h4>
                                    </div>
                                    <ul className="space-y-1">
                                        {brief.mandatories.map((item, i) => (
                                            <li key={i} className="text-xs text-neutral-700 flex items-start gap-2">
                                                <span className="text-green-600 mt-0.5">✓</span>
                                                {item}
                                            </li>
                                        ))}
                                    </ul>
                                </div>

                                <div>
                                    <div className="flex items-center gap-2 mb-2">
                                        <AlertCircle className="w-4 h-4 text-red-600" />
                                        <h4 className="font-semibold text-neutral-900">No-Gos</h4>
                                    </div>
                                    <ul className="space-y-1">
                                        {brief.no_gos.map((item, i) => (
                                            <li key={i} className="text-xs text-neutral-700 flex items-start gap-2">
                                                <span className="text-red-600 mt-0.5">✗</span>
                                                {item}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>

                            {/* Asset Requirements */}
                            {brief.asset_requirements && Object.keys(brief.asset_requirements).length > 0 && (
                                <div>
                                    <h4 className="font-semibold text-neutral-900 mb-2">Asset Requirements</h4>
                                    <div className="bg-neutral-50 rounded-xl p-4 space-y-2">
                                        <div className="flex items-center gap-2 text-xs">
                                            <span className="font-semibold text-neutral-700">Channels:</span>
                                            <div className="flex gap-1">
                                                {brief.channels.map((ch, i) => (
                                                    <span key={i} className="px-2 py-1 bg-white border border-neutral-200 rounded text-neutral-700">
                                                        {ch}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2 text-xs">
                                            <span className="font-semibold text-neutral-700">Intensity:</span>
                                            <span className={cn(
                                                "px-2 py-1 rounded capitalize",
                                                brief.intensity === 'aggressive' ? "bg-red-100 text-red-700" :
                                                    brief.intensity === 'light' ? "bg-blue-100 text-blue-700" :
                                                        "bg-neutral-100 text-neutral-700"
                                            )}>
                                                {brief.intensity}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Success Definition */}
                            <div>
                                <div className="flex items-center gap-2 mb-2">
                                    <Zap className="w-4 h-4 text-amber-600" />
                                    <h4 className="font-semibold text-neutral-900">Success Definition</h4>
                                </div>
                                <p className="text-sm text-neutral-700 bg-amber-50 border border-amber-200 rounded-xl p-4">
                                    {brief.success_definition}
                                </p>
                            </div>

                            {/* CTA */}
                            <button
                                onClick={() => onUseForAsset?.(brief)}
                                className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-neutral-900 text-white rounded-lg font-medium hover:bg-neutral-800 transition-colors"
                            >
                                <Sparkles className="w-5 h-5" />
                                Create Asset from Brief
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Collapsed CTA */}
            {!isExpanded && (
                <div className="p-4 border-t border-neutral-100">
                    <button
                        onClick={() => onUseForAsset?.(brief)}
                        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-neutral-900 text-white rounded-lg text-sm font-medium hover:bg-neutral-800 transition-colors"
                    >
                        <Sparkles className="w-4 h-4" />
                        Use Brief
                    </button>
                </div>
            )}
        </motion.div>
    );
}

// Helper function to generate markdown
function generateMarkdown(brief) {
    return `# Creative Brief

## Single-Minded Proposition
${brief.single_minded_proposition}

## Key Message
${brief.key_message}

## Target Audience
**Cohort:** ${brief.target_cohort_context.name}
**Description:** ${brief.target_cohort_context.description}

### Decision Criteria
${brief.target_cohort_context.decision_criteria?.map(c =>
        `- ${c.criterion} (${Math.round(c.weight * 100)}%)${c.deal_breaker ? ' [DEAL-BREAKER]' : ''}`
    ).join('\n') || 'N/A'}

### Objections to Address
${brief.target_cohort_context.objection_map?.map(o =>
        `- "${o.objection}" → ${o.response}`
    ).join('\n') || 'N/A'}

## Journey Context
**From:** ${brief.journey_context.from_stage}  
**To:** ${brief.journey_context.to_stage}  
**Objective:** ${brief.journey_context.objective}

## Tone and Manner
${brief.tone_and_manner}

## Mandatories
${brief.mandatories.map(m => `- ${m}`).join('\n')}

## No-Gos
${brief.no_gos.map(n => `- ${n}`).join('\n')}

## Success Definition
${brief.success_definition}

## Asset Requirements
**Channels:** ${brief.channels.join(', ')}  
**Intensity:** ${brief.intensity}

---

*Generated: ${brief.generated_at}*
`;
}
