import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    Check,
    Lock,
    Calendar,
    FileText,
    Share2,
    BarChart3,
    ChevronRight,
    Clock,
    Plus,
    Trash2,
    GripVertical,
    Target
} from 'lucide-react'

// --- Shared Components ---

const InputField = ({ field, value, onChange }) => {
    const commonClasses = "w-full px-5 py-4 bg-muted/20 border border-border rounded-2xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all duration-200"

    switch (field.type) {
        case 'text':
        case 'number':
            return (
                <input
                    type={field.type}
                    value={value || ''}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={field.placeholder}
                    className={commonClasses}
                />
            )
        case 'textarea':
            return (
                <textarea
                    value={value || ''}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={field.placeholder}
                    rows={4}
                    className={`${commonClasses} resize-none`}
                />
            )
        case 'select':
            return (
                <div className="relative">
                    <select
                        value={value || ''}
                        onChange={(e) => onChange(e.target.value)}
                        className={`${commonClasses} appearance-none cursor-pointer`}
                    >
                        <option value="">Select...</option>
                        {field.options?.map((opt) => (
                            <option key={opt} value={opt}>{opt}</option>
                        ))}
                    </select>
                    <ChevronRight className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground rotate-90 pointer-events-none" />
                </div>
            )
        default:
            return null
    }
}

// --- Specific Slots ---

const SlotInputs = ({ framework, slots, updateSlots }) => {
    if (!framework) return null
    const inputs = slots.inputs || {}

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center mb-8">
                <p className="text-muted-foreground max-w-lg mx-auto">
                    Configure the starting parameters for the {framework.name} framework.
                </p>
            </div>

            <div className="grid gap-6">
                {framework.inputs.fields.map((field, idx) => (
                    <motion.div
                        key={field.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                    >
                        <label className="block text-sm font-medium text-foreground mb-2 pl-1">
                            {field.label}
                            {field.required && <span className="text-red-500 ml-1">*</span>}
                        </label>
                        <InputField
                            field={field}
                            value={inputs[field.id]}
                            onChange={(v) => updateSlots('inputs', { ...inputs, [field.id]: v })}
                        />
                    </motion.div>
                ))}
            </div>
        </div>
    )
}

const SlotRules = ({ framework, slots, updateSlots }) => {
    if (!framework) return null
    const rules = slots.rules || {}

    const handleToggle = (ruleId, checked) => {
        updateSlots('rules', { ...rules, [ruleId]: checked })
    }

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center mb-8">
                <p className="text-muted-foreground max-w-lg mx-auto">
                    These constraints ensure the system works as designed.
                </p>
            </div>

            {/* Required rules */}
            <div>
                <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-4 pl-1">
                    Non-Negotiables
                </h3>
                <div className="space-y-3">
                    {framework.rules.required.map((rule) => (
                        <div
                            key={rule.id}
                            className="flex items-start gap-4 p-4 rounded-xl bg-muted/30 border border-border/50"
                        >
                            <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                                <Lock className="w-3.5 h-3.5 text-primary" strokeWidth={2} />
                            </div>
                            <div>
                                <span className="text-sm font-medium text-foreground block mb-0.5">{rule.label}</span>
                                <span className="text-xs text-primary font-medium">Required</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Optional rules */}
            {framework.rules.optional?.length > 0 && (
                <div>
                    <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-4 mt-8 pl-1">
                        Optional Constraints
                    </h3>
                    <div className="space-y-3">
                        {framework.rules.optional.map((rule) => (
                            <button
                                key={rule.id}
                                onClick={() => handleToggle(rule.id, !rules[rule.id])}
                                className={`
                  w-full flex items-center gap-4 p-4 rounded-xl border text-left transition-all duration-200 group
                  ${rules[rule.id]
                                        ? 'border-primary bg-primary/5 shadow-sm ring-1 ring-primary/20'
                                        : 'border-border hover:border-primary/30 bg-card hover:bg-muted/30'
                                    }
                `}
                            >
                                <div className={`
                  w-6 h-6 rounded-md border flex items-center justify-center flex-shrink-0 transition-colors
                  ${rules[rule.id] ? 'border-primary bg-primary text-primary-foreground' : 'border-muted-foreground/30 text-transparent group-hover:border-primary/50'}
                `}>
                                    <Check className="w-4 h-4" strokeWidth={3} />
                                </div>
                                <span className="text-sm font-medium text-foreground">{rule.label}</span>
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}

const SlotActions = ({ framework, slots, updateSlots }) => {
    if (!framework) return null
    const actions = slots.dailyActions?.length > 0
        ? slots.dailyActions
        : framework.dailyActions.templates.map(t => ({
            id: `task_${t.day}_${Date.now()}`,
            day: t.day,
            text: t.task,
            duration: t.duration,
            enabled: true
        }))

    if (slots.dailyActions?.length === 0) {
        updateSlots('dailyActions', actions)
    }

    const handleToggleTask = (taskId) => {
        updateSlots('dailyActions', actions.map(a =>
            a.id === taskId ? { ...a, enabled: !a.enabled } : a
        ))
    }

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center mb-6">
                <p className="text-muted-foreground max-w-lg mx-auto">
                    Your generated daily schedule. Disabled items won't appear in your daily tasks.
                </p>
            </div>

            <div className="space-y-2">
                {actions.map((action, idx) => (
                    <motion.div
                        key={action.id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        className={`
                            flex items-center gap-4 p-4 rounded-xl border transition-all duration-200
                            ${action.enabled
                                ? 'bg-card border-border hover:border-primary/30'
                                : 'bg-muted/20 border-border/50 opacity-60'
                            }
                        `}
                    >
                        <button
                            onClick={() => handleToggleTask(action.id)}
                            className={`
                                w-6 h-6 rounded-lg border flex items-center justify-center flex-shrink-0 transition-colors
                                ${action.enabled ? 'border-primary bg-primary text-primary-foreground' : 'border-muted-foreground/40 hover:border-primary/50'}
                            `}
                        >
                            {action.enabled && <Check className="w-4 h-4" strokeWidth={3} />}
                        </button>

                        <div className="flex-1 min-w-0">
                            <div className={`text-sm font-medium ${action.enabled ? 'text-foreground' : 'text-muted-foreground'}`}>
                                {action.text}
                            </div>
                            <div className="flex items-center gap-4 mt-1">
                                <span className="text-xs text-muted-foreground flex items-center gap-1.5 font-medium">
                                    <span className="w-1.5 h-1.5 rounded-full bg-primary/40"></span>
                                    Day {action.day}
                                </span>
                                <span className="text-xs text-muted-foreground flex items-center gap-1.5">
                                    <Clock className="w-3 h-3" />
                                    {action.duration} min
                                </span>
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    )
}

const SlotOutputs = ({ framework, slots, updateSlots }) => {
    if (!framework) return null
    const outputs = slots.outputs?.length > 0
        ? slots.outputs
        : framework.outputs.deliverables.map(d => ({ ...d, status: 'not_started' }))

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center mb-6">
                <p className="text-muted-foreground max-w-lg mx-auto">
                    The concrete assets you will produce by the end of this Move.
                </p>
            </div>

            <div className="grid gap-4">
                {outputs.map((output, idx) => (
                    <motion.div
                        key={output.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="flex items-center gap-5 p-5 rounded-2xl bg-card border border-border hover:border-primary/30 transition-colors"
                    >
                        <div className="w-12 h-12 rounded-xl bg-orange-500/10 text-orange-500 flex items-center justify-center flex-shrink-0">
                            <FileText className="w-6 h-6" strokeWidth={1.5} />
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="text-base font-medium text-foreground mb-1">{output.name}</div>
                            <div className="flex items-center gap-2">
                                <span className="text-xs font-medium px-2 py-0.5 rounded-md bg-muted text-muted-foreground uppercase tracking-wide">
                                    {output.type}
                                </span>
                                {output.required && (
                                    <span className="text-xs font-medium px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-600 uppercase tracking-wide">
                                        Required
                                    </span>
                                )}
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    )
}

const SlotChannels = ({ framework, slots, updateSlots }) => {
    if (!framework) return null
    const selectedChannels = slots.channels || framework.channels.recommended

    const handleToggleChannel = (channel) => {
        const updated = selectedChannels.includes(channel)
            ? selectedChannels.filter(c => c !== channel)
            : [...selectedChannels, channel]
        updateSlots('channels', updated)
    }

    const sections = [
        { title: 'Highly Effective', items: framework.channels.recommended, status: 'recommended' },
        { title: 'Also Compatible', items: framework.channels.optional || [], status: 'optional' },
        { title: 'Not Recommended', items: framework.channels.notRecommended, status: 'not_recommended' }
    ]

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center mb-6">
                <p className="text-muted-foreground max-w-lg mx-auto">
                    Select where to publish. Focus on 1-2 channels for maximum impact.
                </p>
            </div>

            <div className="space-y-8">
                {sections.map((section) => (
                    section.items.length > 0 && (
                        <div key={section.title}>
                            <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-4 pl-1">
                                {section.title}
                            </h3>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                {section.items.map((channelId) => {
                                    const isSelected = selectedChannels.includes(channelId)
                                    return (
                                        <button
                                            key={channelId}
                                            onClick={() => handleToggleChannel(channelId)}
                                            className={`
                                                relative p-4 rounded-xl border text-left transition-all duration-200 group flex items-center gap-4
                                                ${isSelected
                                                    ? `border-primary bg-primary/5 shadow-sm ring-1 ring-primary/20`
                                                    : 'border-border hover:border-primary/30 bg-card hover:bg-muted/30'
                                                }
                                                ${section.status === 'not_recommended' ? 'opacity-75 grayscale hover:grayscale-0' : ''}
                                            `}
                                        >
                                            <div className={`
                                                w-10 h-10 rounded-lg flex items-center justify-center transition-colors
                                                ${isSelected ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary'}
                                             `}>
                                                <Share2 size={20} />
                                            </div>

                                            <div className="flex-1">
                                                <span className="block text-sm font-medium capitalize">{channelId.replace('_', ' ')}</span>
                                            </div>

                                            {isSelected && (
                                                <div className="absolute top-3 right-3 w-5 h-5 rounded-full bg-primary flex items-center justify-center">
                                                    <Check className="w-3 h-3 text-primary-foreground" strokeWidth={3} />
                                                </div>
                                            )}
                                        </button>
                                    )
                                })}
                            </div>
                        </div>
                    )
                ))}
            </div>

            {selectedChannels.length > 2 && (
                <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-700 dark:text-amber-400 text-sm">
                    <Target className="w-5 h-5 flex-shrink-0" />
                    <p>Focus Warning: You've selected {selectedChannels.length} channels. Spreading too thin usually reduces results.</p>
                </div>
            )}
        </div>
    )
}

const SlotMetrics = ({ framework, slots, updateSlots }) => {
    if (!framework) return null
    const metrics = slots.metrics || {
        primary: framework.metrics.primary.name,
        target: '',
        baseline: '',
        leading: framework.metrics.leading.map(l => l.name)
    }

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center mb-6">
                <p className="text-muted-foreground max-w-lg mx-auto">
                    Define what success looks like. Be specific.
                </p>
            </div>

            <div className="p-6 rounded-2xl bg-gradient-to-br from-primary/5 via-transparent to-transparent border border-primary/20">
                <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                        <Target className="w-6 h-6" />
                    </div>
                    <div>
                        <h3 className="text-base font-bold text-foreground">Primary Win Condition</h3>
                        <p className="text-xs text-muted-foreground">The one number that matters most</p>
                    </div>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-xs font-bold text-muted-foreground mb-1.5 uppercase tracking-wide">Metric Name</label>
                        <div className="px-5 py-4 bg-background/80 backdrop-blur-sm border border-border rounded-xl text-foreground font-medium shadow-sm">
                            {framework.metrics.primary.name}
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-xs font-bold text-muted-foreground mb-1.5 uppercase tracking-wide">Baseline</label>
                            <input
                                type="text"
                                value={metrics.baseline || ''}
                                onChange={(e) => updateSlots('metrics', { ...metrics, baseline: e.target.value })}
                                placeholder="0"
                                className="w-full px-5 py-4 bg-background/80 backdrop-blur-sm border border-border rounded-xl text-foreground focus:ring-2 focus:ring-primary/20 outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-muted-foreground mb-1.5 uppercase tracking-wide">Goal Target</label>
                            <input
                                type="text"
                                value={metrics.target || ''}
                                onChange={(e) => updateSlots('metrics', { ...metrics, target: e.target.value })}
                                placeholder={framework.metrics.primary.target}
                                className="w-full px-5 py-4 bg-background/80 backdrop-blur-sm border border-border rounded-xl text-foreground font-bold text-primary focus:ring-2 focus:ring-primary/20 outline-none"
                            />
                        </div>
                    </div>
                </div>
            </div>

            <div className="space-y-3">
                <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest pl-1">
                    Leading Indicators (Daily Signals)
                </h3>
                {framework.metrics.leading.map((indicator, idx) => (
                    <div key={idx} className="flex items-center justify-between p-4 rounded-xl border border-border bg-muted/20">
                        <span className="text-sm font-medium text-foreground">{indicator.name}</span>
                        <div className="text-xs font-medium px-2 py-1 bg-background border border-border rounded-lg text-muted-foreground">
                            Target: {indicator.target}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

const StepBuild = ({ data, updateData, slot = 'inputs' }) => {
    const framework = data.selectedFramework

    const updateSlots = (slotName, slotData) => {
        updateData('slots', {
            ...data.slots,
            [slotName]: slotData
        })
    }

    if (!framework) return <div className="text-center py-20 text-muted-foreground">Please select a framework first.</div>

    return (
        <div className="max-w-2xl mx-auto pb-20">
            <div className="mb-8 text-center">
                <h1 className="font-serif text-3xl text-foreground">
                    {slot === 'inputs' && "What are you working with?"}
                    {slot === 'rules' && "Rules of Engagement"}
                    {slot === 'actions' && "Your Daily Plan"}
                    {slot === 'outputs' && "Required Deliverables"}
                    {slot === 'channels' && "Distribution Channels"}
                    {slot === 'metrics' && "Measuring Success"}
                </h1>
            </div>

            <motion.div
                key={slot}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="bg-card/50 backdrop-blur-sm md:border md:border-border/50 md:shadow-sm md:rounded-3xl md:p-8"
            >
                {slot === 'inputs' && <SlotInputs framework={framework} slots={data.slots} updateSlots={updateSlots} />}
                {slot === 'rules' && <SlotRules framework={framework} slots={data.slots} updateSlots={updateSlots} />}
                {slot === 'actions' && <SlotActions framework={framework} slots={data.slots} updateSlots={updateSlots} />}
                {slot === 'outputs' && <SlotOutputs framework={framework} slots={data.slots} updateSlots={updateSlots} />}
                {slot === 'channels' && <SlotChannels framework={framework} slots={data.slots} updateSlots={updateSlots} />}
                {slot === 'metrics' && <SlotMetrics framework={framework} slots={data.slots} updateSlots={updateSlots} />}
            </motion.div>
        </div>
    )
}

export default StepBuild
