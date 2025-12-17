import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
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
    GripVertical
} from 'lucide-react'
import { generateTasksFromFramework } from '../../../data/frameworkConfigs'

/**
 * Step 4: Build the Move (Fill 6 Slots)
 * 
 * 3-column power layout:
 * - Left rail: Stepper
 * - Main canvas: Dynamic form for current slot
 * - Right rail: Live preview (on large screens)
 */

const SLOT_STEPS = [
    { id: 'inputs', name: 'Inputs', icon: FileText, description: 'What you start with' },
    { id: 'rules', name: 'Rules', icon: Lock, description: 'Constraints you follow' },
    { id: 'actions', name: 'Daily Actions', icon: Calendar, description: 'What you do each day' },
    { id: 'outputs', name: 'Outputs', icon: FileText, description: 'What you make' },
    { id: 'channels', name: 'Channels', icon: Share2, description: 'Where you put it' },
    { id: 'metrics', name: 'Metrics', icon: BarChart3, description: 'How you measure' }
]

// Stepper component
const SlotStepper = ({ currentSlot, onSlotChange, completedSlots }) => (
    <div className="space-y-2">
        {SLOT_STEPS.map((slot, index) => {
            const isActive = currentSlot === slot.id
            const isCompleted = completedSlots.includes(slot.id)
            const Icon = slot.icon

            return (
                <button
                    key={slot.id}
                    onClick={() => onSlotChange(slot.id)}
                    className={`
            w-full flex items-center gap-3 p-3 rounded-xl text-left transition-all
            ${isActive
                            ? 'bg-primary/10 border border-primary/30'
                            : 'hover:bg-muted border border-transparent'
                        }
          `}
                >
                    <div className={`
            w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0
            ${isActive
                            ? 'bg-primary text-primary-foreground'
                            : isCompleted
                                ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400'
                                : 'bg-muted text-muted-foreground'
                        }
          `}>
                        {isCompleted && !isActive ? (
                            <Check className="w-4 h-4" strokeWidth={2} />
                        ) : (
                            <Icon className="w-4 h-4" strokeWidth={1.5} />
                        )}
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className={`text-sm font-medium ${isActive ? 'text-primary' : 'text-foreground'}`}>
                            {slot.name}
                        </div>
                        <div className="text-xs text-muted-foreground truncate">
                            {slot.description}
                        </div>
                    </div>
                    <ChevronRight className={`w-4 h-4 ${isActive ? 'text-primary' : 'text-muted-foreground'}`} strokeWidth={1.5} />
                </button>
            )
        })}
    </div>
)

// Input field renderer
const InputField = ({ field, value, onChange }) => {
    switch (field.type) {
        case 'text':
            return (
                <input
                    type="text"
                    value={value || ''}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={field.placeholder}
                    className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                />
            )
        case 'textarea':
            return (
                <textarea
                    value={value || ''}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={field.placeholder}
                    rows={4}
                    className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary resize-none"
                />
            )
        case 'select':
            return (
                <select
                    value={value || ''}
                    onChange={(e) => onChange(e.target.value)}
                    className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                >
                    <option value="">Select...</option>
                    {field.options?.map((opt) => (
                        <option key={opt} value={opt}>{opt}</option>
                    ))}
                </select>
            )
        case 'number':
            return (
                <input
                    type="number"
                    value={value || ''}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={field.placeholder}
                    className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                />
            )
        default:
            return null
    }
}

// Slot: Inputs
const SlotInputs = ({ framework, slots, updateSlots }) => {
    if (!framework) return null

    const inputs = slots.inputs || {}

    const handleChange = (fieldId, value) => {
        updateSlots('inputs', {
            ...inputs,
            [fieldId]: value
        })
    }

    return (
        <div className="space-y-6">
            <div className="mb-6">
                <h2 className="font-serif text-xl text-foreground mb-2">What you're starting with</h2>
                <p className="text-sm text-muted-foreground">
                    Fill in the inputs required for the {framework.name} framework.
                </p>
            </div>

            {framework.inputs.fields.map((field) => (
                <div key={field.id}>
                    <label className="block text-sm font-medium text-foreground mb-2">
                        {field.label}
                        {field.required && <span className="text-red-500 ml-1">*</span>}
                    </label>
                    <InputField
                        field={field}
                        value={inputs[field.id]}
                        onChange={(v) => handleChange(field.id, v)}
                    />
                </div>
            ))}
        </div>
    )
}

// Slot: Rules
const SlotRules = ({ framework, slots, updateSlots }) => {
    if (!framework) return null

    const rules = slots.rules || {}

    const handleToggle = (ruleId, checked) => {
        updateSlots('rules', {
            ...rules,
            [ruleId]: checked
        })
    }

    return (
        <div className="space-y-6">
            <div className="mb-6">
                <h2 className="font-serif text-xl text-foreground mb-2">Rules you can't break</h2>
                <p className="text-sm text-muted-foreground">
                    These constraints ensure the framework works as designed.
                </p>
            </div>

            {/* Required rules */}
            <div>
                <h3 className="text-sm font-medium text-foreground mb-3 flex items-center gap-2">
                    <Lock className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
                    Required Rules
                </h3>
                <div className="space-y-2">
                    {framework.rules.required.map((rule) => (
                        <div
                            key={rule.id}
                            className="flex items-center gap-3 p-4 rounded-xl bg-muted/50 border border-border"
                        >
                            <div className="w-5 h-5 rounded bg-primary/10 flex items-center justify-center flex-shrink-0">
                                <Check className="w-3 h-3 text-primary" strokeWidth={2} />
                            </div>
                            <span className="text-sm text-foreground flex-1">{rule.label}</span>
                            <span className="text-xs text-muted-foreground">Required</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Optional rules */}
            {framework.rules.optional?.length > 0 && (
                <div>
                    <h3 className="text-sm font-medium text-foreground mb-3">Optional Rules</h3>
                    <div className="space-y-2">
                        {framework.rules.optional.map((rule) => (
                            <button
                                key={rule.id}
                                onClick={() => handleToggle(rule.id, !rules[rule.id])}
                                className={`
                  w-full flex items-center gap-3 p-4 rounded-xl border-2 text-left transition-all
                  ${rules[rule.id]
                                        ? 'border-primary bg-primary/5'
                                        : 'border-border hover:border-primary/30 bg-card'
                                    }
                `}
                            >
                                <div className={`
                  w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-colors
                  ${rules[rule.id] ? 'border-primary bg-primary' : 'border-muted-foreground'}
                `}>
                                    {rules[rule.id] && <Check className="w-3 h-3 text-primary-foreground" strokeWidth={2} />}
                                </div>
                                <span className="text-sm text-foreground">{rule.label}</span>
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}

// Slot: Daily Actions
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

    // Initialize if empty
    if (slots.dailyActions?.length === 0) {
        updateSlots('dailyActions', actions)
    }

    const handleToggleTask = (taskId) => {
        updateSlots('dailyActions', actions.map(a =>
            a.id === taskId ? { ...a, enabled: !a.enabled } : a
        ))
    }

    return (
        <div className="space-y-6">
            <div className="mb-6">
                <h2 className="font-serif text-xl text-foreground mb-2">What you'll do each day</h2>
                <p className="text-sm text-muted-foreground">
                    These tasks are auto-generated from the framework. You can toggle or edit them.
                </p>
            </div>

            <div className="space-y-2">
                {actions.map((action) => (
                    <div
                        key={action.id}
                        className={`
              flex items-center gap-3 p-4 rounded-xl border transition-all
              ${action.enabled
                                ? 'bg-card border-border'
                                : 'bg-muted/30 border-border/50 opacity-60'
                            }
            `}
                    >
                        <button
                            onClick={() => handleToggleTask(action.id)}
                            className={`
                w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-colors
                ${action.enabled ? 'border-primary bg-primary' : 'border-muted-foreground'}
              `}
                        >
                            {action.enabled && <Check className="w-3 h-3 text-primary-foreground" strokeWidth={2} />}
                        </button>

                        <div className="flex-1 min-w-0">
                            <div className="text-sm text-foreground">{action.text}</div>
                            <div className="flex items-center gap-3 mt-1">
                                <span className="text-xs text-muted-foreground flex items-center gap-1">
                                    <Calendar className="w-3 h-3" strokeWidth={1.5} />
                                    Day {action.day}
                                </span>
                                <span className="text-xs text-muted-foreground flex items-center gap-1">
                                    <Clock className="w-3 h-3" strokeWidth={1.5} />
                                    {action.duration} min
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

// Slot: Outputs
const SlotOutputs = ({ framework, slots, updateSlots }) => {
    if (!framework) return null

    const outputs = slots.outputs?.length > 0
        ? slots.outputs
        : framework.outputs.deliverables.map(d => ({
            ...d,
            status: 'not_started'
        }))

    return (
        <div className="space-y-6">
            <div className="mb-6">
                <h2 className="font-serif text-xl text-foreground mb-2">What you'll make</h2>
                <p className="text-sm text-muted-foreground">
                    These are the deliverables you'll create during this Move.
                </p>
            </div>

            <div className="space-y-3">
                {outputs.map((output) => (
                    <div
                        key={output.id}
                        className="flex items-center gap-4 p-4 rounded-xl bg-card border border-border"
                    >
                        <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center flex-shrink-0">
                            <FileText className="w-5 h-5 text-muted-foreground" strokeWidth={1.5} />
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium text-foreground">{output.name}</div>
                            <div className="text-xs text-muted-foreground capitalize">{output.type}</div>
                        </div>
                        {output.required && (
                            <span className="text-xs text-primary font-medium">Required</span>
                        )}
                    </div>
                ))}
            </div>
        </div>
    )
}

// Slot: Channels
const SlotChannels = ({ framework, slots, updateSlots }) => {
    if (!framework) return null

    const selectedChannels = slots.channels || framework.channels.recommended

    const handleToggleChannel = (channel) => {
        const updated = selectedChannels.includes(channel)
            ? selectedChannels.filter(c => c !== channel)
            : [...selectedChannels, channel]
        updateSlots('channels', updated)
    }

    const allChannels = [
        ...framework.channels.recommended.map(c => ({ id: c, status: 'recommended' })),
        ...(framework.channels.optional || []).map(c => ({ id: c, status: 'optional' })),
        ...framework.channels.notRecommended.map(c => ({ id: c, status: 'not_recommended' }))
    ]

    return (
        <div className="space-y-6">
            <div className="mb-6">
                <h2 className="font-serif text-xl text-foreground mb-2">Where you'll put it</h2>
                <p className="text-sm text-muted-foreground">
                    Select the channels for your content. We recommend sticking to 1-2 channels for focus.
                </p>
            </div>

            <div className="space-y-3">
                {allChannels.map(({ id, status }) => {
                    const isSelected = selectedChannels.includes(id)

                    return (
                        <button
                            key={id}
                            onClick={() => handleToggleChannel(id)}
                            className={`
                w-full flex items-center gap-4 p-4 rounded-xl border-2 text-left transition-all
                ${isSelected
                                    ? 'border-primary bg-primary/5'
                                    : 'border-border hover:border-primary/30 bg-card'
                                }
              `}
                        >
                            <div className={`
                w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-colors
                ${isSelected ? 'border-primary bg-primary' : 'border-muted-foreground'}
              `}>
                                {isSelected && <Check className="w-3 h-3 text-primary-foreground" strokeWidth={2} />}
                            </div>

                            <span className="text-sm font-medium text-foreground capitalize flex-1">
                                {id.replace('_', ' ')}
                            </span>

                            <span className={`
                px-2 py-0.5 rounded-full text-xs font-medium
                ${status === 'recommended'
                                    ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                                    : status === 'not_recommended'
                                        ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                                        : 'bg-muted text-muted-foreground'
                                }
              `}>
                                {status === 'recommended' ? 'Recommended' : status === 'not_recommended' ? 'Not recommended' : 'Optional'}
                            </span>
                        </button>
                    )
                })}
            </div>

            {selectedChannels.length > 2 && (
                <div className="p-4 rounded-xl bg-amber-100/50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
                    <p className="text-sm text-amber-700 dark:text-amber-400">
                        ⚠️ You've selected {selectedChannels.length} channels. Consider focusing on 1-2 for better results.
                    </p>
                </div>
            )}
        </div>
    )
}

// Slot: Metrics
const SlotMetrics = ({ framework, slots, updateSlots }) => {
    if (!framework) return null

    const metrics = slots.metrics || {
        primary: framework.metrics.primary.name,
        target: '',
        baseline: '',
        leading: framework.metrics.leading.map(l => l.name)
    }

    const handleChange = (key, value) => {
        updateSlots('metrics', {
            ...metrics,
            [key]: value
        })
    }

    return (
        <div className="space-y-6">
            <div className="mb-6">
                <h2 className="font-serif text-xl text-foreground mb-2">How you'll know it worked</h2>
                <p className="text-sm text-muted-foreground">
                    Define your success metrics and targets.
                </p>
            </div>

            {/* Primary KPI */}
            <div className="p-4 rounded-xl bg-primary/5 border border-primary/20">
                <h3 className="text-sm font-medium text-foreground mb-3 flex items-center gap-2">
                    <BarChart3 className="w-4 h-4 text-primary" strokeWidth={1.5} />
                    Primary KPI (Win Condition)
                </h3>

                <div className="space-y-4">
                    <div>
                        <label className="block text-xs text-muted-foreground mb-1">Metric</label>
                        <div className="px-4 py-3 bg-background border border-border rounded-xl text-foreground font-medium">
                            {framework.metrics.primary.name}
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-xs text-muted-foreground mb-1">Baseline (current)</label>
                            <input
                                type="text"
                                value={metrics.baseline || ''}
                                onChange={(e) => handleChange('baseline', e.target.value)}
                                placeholder="e.g., 5"
                                className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-muted-foreground mb-1">Target</label>
                            <input
                                type="text"
                                value={metrics.target || ''}
                                onChange={(e) => handleChange('target', e.target.value)}
                                placeholder={framework.metrics.primary.target}
                                className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Leading indicators */}
            <div>
                <h3 className="text-sm font-medium text-foreground mb-3">Leading Indicators</h3>
                <div className="space-y-2">
                    {framework.metrics.leading.map((indicator, idx) => (
                        <div
                            key={idx}
                            className="flex items-center gap-4 p-4 rounded-xl bg-card border border-border"
                        >
                            <div className="flex-1">
                                <div className="text-sm text-foreground">{indicator.name}</div>
                                <div className="text-xs text-muted-foreground">Target: {indicator.target}</div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

// Main component - now just renders the specific slot passed as prop
const StepBuild = ({ data, updateData, slot = 'inputs' }) => {
    const framework = data.selectedFramework

    const updateSlots = (slotName, slotData) => {
        updateData('slots', {
            ...data.slots,
            [slotName]: slotData
        })
    }

    if (!framework) {
        return (
            <div className="text-center py-12">
                <p className="text-muted-foreground">Please select a framework first.</p>
            </div>
        )
    }

    const renderSlotContent = () => {
        switch (slot) {
            case 'inputs':
                return <SlotInputs framework={framework} slots={data.slots} updateSlots={updateSlots} />
            case 'rules':
                return <SlotRules framework={framework} slots={data.slots} updateSlots={updateSlots} />
            case 'actions':
                return <SlotActions framework={framework} slots={data.slots} updateSlots={updateSlots} />
            case 'outputs':
                return <SlotOutputs framework={framework} slots={data.slots} updateSlots={updateSlots} />
            case 'channels':
                return <SlotChannels framework={framework} slots={data.slots} updateSlots={updateSlots} />
            case 'metrics':
                return <SlotMetrics framework={framework} slots={data.slots} updateSlots={updateSlots} />
            default:
                return null
        }
    }

    return (
        <div className="max-w-3xl mx-auto">
            {/* Dynamic Header based on slot */}
            <div className="mb-8 text-center">
                <h1 className="font-serif text-3xl text-foreground mb-2">
                    {slot === 'inputs' && "What you're starting with"}
                    {slot === 'rules' && "Rules you can't break"}
                    {slot === 'actions' && "What you'll do each day"}
                    {slot === 'outputs' && "What you'll make"}
                    {slot === 'channels' && "Where you'll put it"}
                    {slot === 'metrics' && "How you'll know it worked"}
                </h1>
            </div>

            <motion.div
                key={slot}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="bg-card border border-border rounded-2xl p-6 md:p-8"
            >
                {renderSlotContent()}
            </motion.div>
        </div>
    )
}

export default StepBuild
