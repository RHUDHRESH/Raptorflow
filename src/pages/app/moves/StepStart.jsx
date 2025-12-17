import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
    Calendar,
    User,
    Users,
    Link2,
    Bell,
    Clock,
    Target,
    FileText,
    Rocket
} from 'lucide-react'
import { PROBLEM_TYPES } from '../../../data/frameworkConfigs'
import useRaptorflowStore from '../../../store/raptorflowStore'
import { BrandIcon } from '@/components/brand/BrandSystem'

/**
 * Step 6: Start & Link
 * 
 * Final configuration before launching the Move:
 * - Start date
 * - Campaign link (optional)
 * - Run mode (Solo/Team)
 * - Notifications
 */

const StepStart = ({ data, updateData }) => {
    const navigate = useNavigate()
    const { campaigns, createMove, openMuseDrawer } = useRaptorflowStore()
    const [isCreating, setIsCreating] = useState(false)

    const framework = data.selectedFramework
    const problem = data.problemType ? PROBLEM_TYPES[data.problemType] : null

    // Generate default name
    const defaultName = framework
        ? `${framework.name} - ${new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`
        : 'New Move'

    const handleCreateMove = async () => {
        if (!framework || isCreating) return

        setIsCreating(true)

        try {
            // Create the move with all collected data
            const moveData = {
                name: data.moveName || defaultName,
                problemType: data.problemType,
                frameworkId: framework.id,
                frameworkName: framework.name,
                expert: framework.expert,

                // Slots
                slots: data.slots,

                // Basics
                campaignId: data.campaignId || null,
                channel: data.slots.channels?.[0] || 'linkedin',
                durationDays: framework.defaultDuration,
                metric: framework.metrics.primary.name,

                // Timing
                startDate: data.startDate,

                // Generated tasks from framework
                checklistItems: (data.slots.dailyActions || framework.dailyActions.templates).map((task, idx) => ({
                    id: `task_${idx}_${Date.now()}`,
                    text: task.text || task.task,
                    done: false,
                    day: task.day,
                    duration: task.duration
                })),

                // Tracking setup
                tracking: {
                    metric: framework.metrics.primary.name,
                    baseline: data.slots.metrics?.baseline || 0,
                    target: data.slots.metrics?.target || framework.metrics.primary.target,
                    updates: []
                },

                // Status
                status: 'active',

                // Metadata
                createdAt: new Date().toISOString()
            }

            // Add to store
            createMove(moveData)

            // Navigate to moves page
            navigate('/app/moves')
        } catch (error) {
            console.error('Failed to create move:', error)
            setIsCreating(false)
        }
    }

    if (!framework) {
        return (
            <div className="text-center py-12">
                <p className="text-muted-foreground">Please complete the previous steps first.</p>
            </div>
        )
    }

    return (
        <div className="pb-24">
            {/* Header */}
            <div className="text-center mb-8">
                <h1 className="font-serif text-3xl text-foreground mb-3">
                    Ready to launch!
                </h1>
                <p className="text-muted-foreground">
                    Final settings before your Move begins.
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Left: Settings */}
                <div className="space-y-6">
                    {/* Move name */}
                    <div>
                        <label className="block text-sm font-medium text-foreground mb-2">
                            Move Name
                        </label>
                        <input
                            type="text"
                            value={data.moveName || ''}
                            onChange={(e) => updateData('moveName', e.target.value)}
                            placeholder={defaultName}
                            className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                        />
                    </div>

                    {/* Start date */}
                    <div>
                        <label className="block text-sm font-medium text-foreground mb-2 flex items-center gap-2">
                            <Calendar className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
                            Start Date
                        </label>
                        <input
                            type="date"
                            value={data.startDate || new Date().toISOString().split('T')[0]}
                            onChange={(e) => updateData('startDate', e.target.value)}
                            className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                        />
                    </div>

                    {/* Link to campaign */}
                    <div>
                        <label className="block text-sm font-medium text-foreground mb-2 flex items-center gap-2">
                            <Link2 className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
                            Link to Campaign (optional)
                        </label>
                        <select
                            value={data.campaignId || ''}
                            onChange={(e) => updateData('campaignId', e.target.value || null)}
                            className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                        >
                            <option value="">Standalone Move</option>
                            {(campaigns || []).map(campaign => (
                                <option key={campaign.id} value={campaign.id}>
                                    {campaign.name}
                                </option>
                            ))}
                        </select>
                        <p className="mt-1.5 text-xs text-muted-foreground">
                            Link to a campaign to track progress together.
                        </p>
                    </div>

                    {/* Run mode */}
                    <div>
                        <label className="block text-sm font-medium text-foreground mb-2 flex items-center gap-2">
                            <Users className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
                            Run Mode
                        </label>
                        <div className="grid grid-cols-2 gap-3">
                            <button
                                onClick={() => updateData('runMode', 'solo')}
                                className={`
                  p-4 rounded-xl border-2 text-left transition-all
                  ${data.runMode === 'solo' || !data.runMode
                                        ? 'border-primary bg-primary/5'
                                        : 'border-border hover:border-primary/30 bg-card'
                                    }
                `}
                            >
                                <User className={`w-5 h-5 mb-2 ${data.runMode === 'solo' || !data.runMode ? 'text-primary' : 'text-muted-foreground'}`} strokeWidth={1.5} />
                                <div className={`text-sm font-medium ${data.runMode === 'solo' || !data.runMode ? 'text-primary' : 'text-foreground'}`}>
                                    Solo
                                </div>
                                <div className="text-xs text-muted-foreground mt-0.5">
                                    You own all tasks
                                </div>
                            </button>

                            <button
                                onClick={() => updateData('runMode', 'team')}
                                className={`
                  p-4 rounded-xl border-2 text-left transition-all
                  ${data.runMode === 'team'
                                        ? 'border-primary bg-primary/5'
                                        : 'border-border hover:border-primary/30 bg-card'
                                    }
                `}
                            >
                                <Users className={`w-5 h-5 mb-2 ${data.runMode === 'team' ? 'text-primary' : 'text-muted-foreground'}`} strokeWidth={1.5} />
                                <div className={`text-sm font-medium ${data.runMode === 'team' ? 'text-primary' : 'text-foreground'}`}>
                                    Team
                                </div>
                                <div className="text-xs text-muted-foreground mt-0.5">
                                    Assign tasks to others
                                </div>
                            </button>
                        </div>
                    </div>

                    {/* Notifications */}
                    <div className="p-4 rounded-xl bg-muted/50 border border-border">
                        <div className="flex items-center gap-3 mb-3">
                            <Bell className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
                            <span className="text-sm font-medium text-foreground">Notifications</span>
                        </div>
                        <div className="space-y-3">
                            <label className="flex items-center gap-3 cursor-pointer">
                                <input
                                    type="checkbox"
                                    defaultChecked
                                    className="w-4 h-4 rounded border-border text-primary focus:ring-primary/20"
                                />
                                <span className="text-sm text-muted-foreground">Daily task reminders</span>
                            </label>
                            <label className="flex items-center gap-3 cursor-pointer">
                                <input
                                    type="checkbox"
                                    defaultChecked
                                    className="w-4 h-4 rounded border-border text-primary focus:ring-primary/20"
                                />
                                <span className="text-sm text-muted-foreground">Checkpoint alerts</span>
                            </label>
                        </div>
                    </div>
                </div>

                {/* Right: Summary card */}
                <div>
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-card border border-border rounded-2xl p-6 sticky top-32"
                    >
                        <h3 className="font-serif text-lg text-foreground mb-4">Move Summary</h3>

                        {/* Problem + Framework */}
                        <div className="space-y-4 mb-6">
                            <div className="flex items-start gap-3">
                                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                                    <BrandIcon name="speed" size={20} className="text-primary" />
                                </div>
                                <div>
                                    <div className="text-sm font-medium text-foreground">{framework.name}</div>
                                    <div className="text-xs text-muted-foreground">{framework.subtitle}</div>
                                </div>
                            </div>

                            {problem && (
                                <div className="p-3 rounded-xl bg-muted/50 border border-border">
                                    <div className="text-xs text-muted-foreground mb-1">Solving</div>
                                    <div className="text-sm text-foreground">"{problem.statement}"</div>
                                </div>
                            )}
                        </div>

                        {/* Key stats */}
                        <div className="grid grid-cols-2 gap-4 mb-6">
                            <div className="p-3 rounded-xl bg-muted/50 border border-border">
                                <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                                    <Clock className="w-3 h-3" strokeWidth={1.5} />
                                    Duration
                                </div>
                                <div className="text-sm font-medium text-foreground">{framework.defaultDuration} days</div>
                            </div>

                            <div className="p-3 rounded-xl bg-muted/50 border border-border">
                                <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                                    <Target className="w-3 h-3" strokeWidth={1.5} />
                                    Primary KPI
                                </div>
                                <div className="text-sm font-medium text-foreground">{framework.metrics.primary.name}</div>
                            </div>

                            <div className="p-3 rounded-xl bg-muted/50 border border-border">
                                <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                                    <FileText className="w-3 h-3" strokeWidth={1.5} />
                                    Deliverables
                                </div>
                                <div className="text-sm font-medium text-foreground">{framework.outputs.deliverables.length} items</div>
                            </div>

                            <div className="p-3 rounded-xl bg-muted/50 border border-border">
                                <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                                    <Calendar className="w-3 h-3" strokeWidth={1.5} />
                                    Tasks
                                </div>
                                <div className="text-sm font-medium text-foreground">{framework.dailyActions.templates.length} total</div>
                            </div>
                        </div>

                        {/* First task preview */}
                        <div className="p-4 rounded-xl bg-primary/5 border border-primary/20 mb-6">
                            <div className="text-xs text-primary font-medium mb-1">Today's first task will be:</div>
                            <div className="text-sm text-foreground">
                                {framework.dailyActions.templates[0]?.task || 'Get started'}
                            </div>
                        </div>

                        {/* Launch button */}
                        <button
                            onClick={handleCreateMove}
                            disabled={isCreating}
                            className="w-full flex items-center justify-center gap-2 py-4 bg-primary text-primary-foreground rounded-xl text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
                        >
                            {isCreating ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                                    Creating...
                                </>
                            ) : (
                                <>
                                    <Rocket className="w-4 h-4" strokeWidth={1.5} />
                                    Start Move
                                </>
                            )}
                        </button>
                    </motion.div>
                </div>
            </div>
        </div>
    )
}

export default StepStart
