import { motion } from 'framer-motion'

/**
 * Step 2: Situation Snapshot
 * 
 * Quick context questions to determine framework fit.
 * Keep it fast, crisp, low effort.
 */

const OptionCard = ({ label, description, isSelected, onClick, icon }) => (
    <button
        onClick={onClick}
        className={`
      flex-1 p-4 rounded-xl border-2 text-left transition-all duration-200
      ${isSelected
                ? 'border-primary bg-primary/5'
                : 'border-border hover:border-primary/50 bg-card'
            }
    `}
    >
        {icon && (
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center mb-2 ${isSelected ? 'bg-primary/10' : 'bg-muted'}`}>
                {icon}
            </div>
        )}
        <div className={`text-sm font-medium ${isSelected ? 'text-primary' : 'text-foreground'}`}>
            {label}
        </div>
        {description && (
            <div className="text-xs text-muted-foreground mt-1">{description}</div>
        )}
    </button>
)

const OptionRow = ({ options, value, onChange, columns = 3 }) => (
    <div className={`grid gap-3 ${columns === 4 ? 'grid-cols-4' : columns === 2 ? 'grid-cols-2' : 'grid-cols-3'}`}>
        {options.map((option) => (
            <OptionCard
                key={option.value}
                label={option.label}
                description={option.description}
                isSelected={value === option.value}
                onClick={() => onChange(option.value)}
                icon={option.icon}
            />
        ))}
    </div>
)

const ToggleOption = ({ label, description, checked, onChange }) => (
    <button
        onClick={() => onChange(!checked)}
        className={`
      flex items-center justify-between p-4 rounded-xl border-2 transition-all duration-200
      ${checked
                ? 'border-primary bg-primary/5'
                : 'border-border hover:border-primary/50 bg-card'
            }
    `}
    >
        <div>
            <div className={`text-sm font-medium ${checked ? 'text-primary' : 'text-foreground'}`}>
                {label}
            </div>
            {description && (
                <div className="text-xs text-muted-foreground mt-0.5">{description}</div>
            )}
        </div>
        <div className={`
      w-10 h-6 rounded-full transition-colors relative
      ${checked ? 'bg-primary' : 'bg-muted'}
    `}>
            <div className={`
        absolute top-1 w-4 h-4 rounded-full bg-white transition-transform
        ${checked ? 'translate-x-5' : 'translate-x-1'}
      `} />
        </div>
    </button>
)

const StepSituation = ({ data, updateData }) => {
    const situation = data.situation

    const updateSituation = (key, value) => {
        updateData('situation', {
            ...situation,
            [key]: value
        })
    }

    return (
        <div className="pb-24 max-w-2xl mx-auto">
            {/* Header */}
            <div className="text-center mb-10">
                <h1 className="font-serif text-3xl text-foreground mb-3">
                    Tell us your situation
                </h1>
                <p className="text-muted-foreground">
                    Answer these so we recommend the right approach for you.
                </p>
                <div className="mt-2 inline-flex items-center gap-2 text-xs text-muted-foreground">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Takes ~60 seconds
                </div>
            </div>

            <div className="space-y-8">
                {/* Section A: Core Constraints */}
                <motion.section
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                >
                    <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-4">
                        Core Constraints
                    </h2>

                    <div className="space-y-6">
                        {/* Speed needed */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-3">
                                How fast do you need results?
                            </label>
                            <OptionRow
                                options={[
                                    { value: '7', label: '7 days', description: 'Fast sprint' },
                                    { value: '14', label: '14 days', description: 'Standard' },
                                    { value: '30', label: '30 days', description: 'Deep work' }
                                ]}
                                value={situation.speedNeeded}
                                onChange={(v) => updateSituation('speedNeeded', v)}
                            />
                        </div>

                        {/* Time budget */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-3">
                                How much time can you invest?
                            </label>
                            <OptionRow
                                options={[
                                    { value: '4h', label: '4 hours', description: 'Minimal' },
                                    { value: '8h', label: '8 hours', description: 'Standard' },
                                    { value: '15h', label: '15+ hours', description: 'Deep dive' }
                                ]}
                                value={situation.timeBudget}
                                onChange={(v) => updateSituation('timeBudget', v)}
                            />
                        </div>

                        {/* Sales motion */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-3">
                                How do you close deals?
                            </label>
                            <OptionRow
                                options={[
                                    { value: 'calls', label: 'Sales Calls', description: 'Talk to close' },
                                    { value: 'dms', label: 'DMs / Chat', description: 'Message to close' },
                                    { value: 'checkout', label: 'Self-Serve', description: 'Direct checkout' }
                                ]}
                                value={situation.salesMotion}
                                onChange={(v) => updateSituation('salesMotion', v)}
                            />
                        </div>

                        {/* Traffic level */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-3">
                                Current traffic/audience level?
                            </label>
                            <OptionRow
                                options={[
                                    { value: 'low', label: 'Low', description: '<1k followers' },
                                    { value: 'medium', label: 'Medium', description: '1k-10k' },
                                    { value: 'high', label: 'High', description: '10k+' }
                                ]}
                                value={situation.trafficLevel}
                                onChange={(v) => updateSituation('trafficLevel', v)}
                            />
                        </div>
                    </div>
                </motion.section>

                {/* Section B: Assets & Proof */}
                <motion.section
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-4">
                        Assets & Proof
                    </h2>

                    <div className="space-y-6">
                        {/* Customer results */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-3">
                                Do you have customer results to show?
                            </label>
                            <OptionRow
                                options={[
                                    { value: 'none', label: 'None yet', description: 'Still building' },
                                    { value: 'some', label: 'Some', description: 'A few cases' },
                                    { value: 'strong', label: 'Strong', description: 'Clear wins' }
                                ]}
                                value={situation.customerResults}
                                onChange={(v) => updateSituation('customerResults', v)}
                            />
                        </div>

                        {/* Clear offer */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-3">
                                How clear is your offer?
                            </label>
                            <OptionRow
                                options={[
                                    { value: 'messy', label: 'Messy', description: 'Needs work' },
                                    { value: 'okay', label: 'Okay', description: 'Functional' },
                                    { value: 'sharp', label: 'Sharp', description: 'Dialed in' }
                                ]}
                                value={situation.clearOffer}
                                onChange={(v) => updateSituation('clearOffer', v)}
                            />
                        </div>

                        {/* Primary channel */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-3">
                                Primary channel today?
                            </label>
                            <OptionRow
                                options={[
                                    { value: 'linkedin', label: 'LinkedIn' },
                                    { value: 'instagram', label: 'Instagram' },
                                    { value: 'email', label: 'Email' },
                                    { value: 'twitter', label: 'Twitter/X' }
                                ]}
                                value={situation.primaryChannel}
                                onChange={(v) => updateSituation('primaryChannel', v)}
                                columns={4}
                            />
                        </div>

                        {/* Paid budget toggle */}
                        <ToggleOption
                            label="Paid budget available?"
                            description="Can you invest in ads or promotions?"
                            checked={situation.paidBudget}
                            onChange={(v) => updateSituation('paidBudget', v)}
                        />
                    </div>
                </motion.section>
            </div>

            {/* Summary strip */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="mt-8 p-4 rounded-xl bg-muted/50 border border-border"
            >
                <div className="flex flex-wrap gap-2">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium">
                        {situation.speedNeeded} days
                    </span>
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-muted text-muted-foreground text-xs font-medium">
                        {situation.timeBudget}
                    </span>
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-muted text-muted-foreground text-xs font-medium capitalize">
                        {situation.salesMotion}
                    </span>
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-muted text-muted-foreground text-xs font-medium capitalize">
                        {situation.trafficLevel} traffic
                    </span>
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-muted text-muted-foreground text-xs font-medium capitalize">
                        {situation.customerResults} proof
                    </span>
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-muted text-muted-foreground text-xs font-medium capitalize">
                        {situation.primaryChannel}
                    </span>
                </div>
            </motion.div>
        </div>
    )
}

export default StepSituation
