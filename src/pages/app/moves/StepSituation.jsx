import { motion } from 'framer-motion'
import { Check, Clock, Coins, Users, Zap, Target, MousePointer, Activity } from 'lucide-react'

/**
 * Step 2: Situation Snapshot
 * 
 * Quick context questions to determine framework fit.
 */

const OptionCard = ({ label, description, isSelected, onClick, icon: Icon }) => (
    <button
        onClick={onClick}
        className={`
      relative flex flex-col items-start p-5 rounded-2xl border transition-all duration-200 h-full w-full text-left group
      ${isSelected
                ? 'border-primary bg-primary/5 shadow-sm ring-1 ring-primary/20'
                : 'border-border hover:border-primary/30 bg-card hover:bg-muted/30'
            }
    `}
    >
        {isSelected && (
            <div className="absolute top-3 right-3 text-primary">
                <div className="w-5 h-5 bg-primary rounded-full flex items-center justify-center">
                    <Check className="w-3 h-3 text-primary-foreground" strokeWidth={3} />
                </div>
            </div>
        )}

        <div className={`
      w-10 h-10 rounded-xl flex items-center justify-center mb-4 transition-colors
      ${isSelected ? 'bg-primary/20 text-primary' : 'bg-muted text-muted-foreground group-hover:text-primary group-hover:bg-primary/10'}
    `}>
            {Icon ? <Icon size={20} /> : <Activity size={20} />}
        </div>

        <div className={`font-medium mb-1 ${isSelected ? 'text-primary' : 'text-foreground'}`}>
            {label}
        </div>
        {description && (
            <div className="text-xs text-muted-foreground leading-relaxed">{description}</div>
        )}
    </button>
)

const OptionRow = ({ options, value, onChange, columns = 3 }) => (
    <div className={`grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-${columns}`}>
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

const ToggleOption = ({ label, description, checked, onChange, icon: Icon }) => (
    <button
        onClick={() => onChange(!checked)}
        className={`
      flex items-center justify-between p-5 rounded-2xl border transition-all duration-200 w-full group
      ${checked
                ? 'border-primary bg-primary/5 shadow-sm ring-1 ring-primary/20'
                : 'border-border hover:border-primary/30 bg-card hover:bg-muted/30'
            }
    `}
    >
        <div className="flex items-center gap-4 text-left">
            <div className={`
        w-10 h-10 rounded-xl flex items-center justify-center transition-colors
        ${checked ? 'bg-primary/20 text-primary' : 'bg-muted text-muted-foreground group-hover:text-primary group-hover:bg-primary/10'}
      `}>
                {Icon ? <Icon size={20} /> : <Activity size={20} />}
            </div>
            <div>
                <div className={`font-medium ${checked ? 'text-primary' : 'text-foreground'}`}>
                    {label}
                </div>
                {description && (
                    <div className="text-xs text-muted-foreground mt-0.5">{description}</div>
                )}
            </div>
        </div>

        <div className={`
      w-11 h-6 rounded-full transition-colors relative flex-shrink-0 ml-4
      ${checked ? 'bg-primary' : 'bg-muted'}
    `}>
            <div className={`
        absolute top-1 w-4 h-4 rounded-full bg-white transition-transform duration-200 shadow-sm
        ${checked ? 'translate-x-6' : 'translate-x-1'}
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
        <div className="max-w-4xl mx-auto pb-24">
            {/* Header */}
            <div className="text-center mb-10">
                <h1 className="font-serif text-2xl text-foreground mb-2">
                    Tell us your situation
                </h1>
                <p className="text-sm text-muted-foreground max-w-lg mx-auto">
                    Answer these quick questions so we can recommend the perfect strategy.
                </p>
                <div className="mt-4 inline-flex items-center gap-2 px-3 py-1 bg-muted/50 rounded-full text-xs text-muted-foreground border border-border/50">
                    <Clock className="w-3.5 h-3.5" />
                    Takes ~60 seconds
                </div>
            </div>

            <div className="space-y-12">
                {/* Section A: Core Constraints */}
                <motion.section
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                >
                    <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-6 pl-1">
                        Core Constraints
                    </h2>

                    <div className="space-y-8">
                        {/* Speed needed */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-4 pl-1">
                                How fast do you need results?
                            </label>
                            <OptionRow
                                options={[
                                    { value: '7', label: '7 Days', description: 'Need results ASAP (Sprint)', icon: Zap },
                                    { value: '14', label: '14 Days', description: 'Standard timeframe (Move)', icon: Clock },
                                    { value: '30', label: '30 Days', description: 'More time for quality (Deep)', icon: Target }
                                ]}
                                value={situation.speedNeeded}
                                onChange={(v) => updateSituation('speedNeeded', v)}
                            />
                        </div>

                        {/* Time budget */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-4 pl-1">
                                How much time can you invest per week?
                            </label>
                            <OptionRow
                                options={[
                                    { value: '4h', label: '4 Hours', description: 'I am swamped', icon: Activity },
                                    { value: '8h', label: '8 Hours', description: 'Standard effort', icon: Clock },
                                    { value: '15h', label: '15+ Hours', description: 'All-in focused', icon: Target }
                                ]}
                                value={situation.timeBudget}
                                onChange={(v) => updateSituation('timeBudget', v)}
                            />
                        </div>

                        {/* Sales motion */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-4 pl-1">
                                How do you usually close deals?
                            </label>
                            <OptionRow
                                options={[
                                    { value: 'calls', label: 'Sales Calls', description: 'High ticket, high touch', icon: Users },
                                    { value: 'dms', label: 'DMs / Chat', description: 'Conversational closing', icon: MousePointer },
                                    { value: 'checkout', label: 'Self-Serve', description: 'Direct to checkout', icon: Coins }
                                ]}
                                value={situation.salesMotion}
                                onChange={(v) => updateSituation('salesMotion', v)}
                            />
                        </div>
                        {/* Traffic level */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-4 pl-1">
                                What is your current traffic level?
                            </label>
                            <OptionRow
                                options={[
                                    { value: 'low', label: 'Low', description: 'Just starting / <1k followers', icon: Users },
                                    { value: 'medium', label: 'Medium', description: 'Growing / 1k-10k followers', icon: Activity },
                                    { value: 'high', label: 'High', description: 'established / 10k+ followers', icon: Zap }
                                ]}
                                value={situation.trafficLevel}
                                onChange={(v) => updateSituation('trafficLevel', v)}
                            />
                        </div>
                    </div>
                </motion.section>

                <div className="border-t border-border/50" />

                {/* Section B: Assets & Proof */}
                <motion.section
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-6 pl-1">
                        Assets & Proof
                    </h2>

                    <div className="space-y-8">
                        {/* Customer results */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-4 pl-1">
                                Do you have customer results to show?
                            </label>
                            <OptionRow
                                options={[
                                    { value: 'none', label: 'None yet', description: "I'm looking for my first wins", icon: Users },
                                    { value: 'some', label: 'Some', description: 'A few good testimonials', icon: Check },
                                    { value: 'strong', label: 'Strong', description: 'Clear, undeniable case studies', icon: Zap }
                                ]}
                                value={situation.customerResults}
                                onChange={(v) => updateSituation('customerResults', v)}
                            />
                        </div>

                        {/* Paid budget toggle */}
                        <ToggleOption
                            label="Do you have a paid ad budget?"
                            description="Can you invest money to accelerate distribution?"
                            checked={situation.paidBudget}
                            onChange={(v) => updateSituation('paidBudget', v)}
                            icon={Coins}
                        />
                    </div>
                </motion.section>
            </div>
        </div>
    )
}

export default StepSituation
