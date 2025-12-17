import { motion } from 'framer-motion'
import {
    FileText,
    Image,
    Video,
    File,
    Plus,
    ExternalLink,
    Check,
    Clock,
    AlertCircle
} from 'lucide-react'
import useRaptorflowStore from '../../../../store/raptorflowStore'

/**
 * Assets Tab - Deliverables Control Center
 * 
 * Shows all outputs/deliverables with:
 * - Status (not started, in progress, ready, published)
 * - Actions (Create, Open in Muse, Mark published)
 */

const STATUS_CONFIG = {
    not_started: { label: 'Not Started', icon: Clock, color: 'muted' },
    in_progress: { label: 'In Progress', icon: AlertCircle, color: 'amber' },
    ready: { label: 'Ready', icon: Check, color: 'emerald' },
    published: { label: 'Published', icon: ExternalLink, color: 'primary' }
}

const TYPE_ICONS = {
    document: FileText,
    article: FileText,
    page: FileText,
    image: Image,
    video: Video,
    content: FileText,
    emails: FileText,
    default: File
}

const TabAssets = ({ move, framework }) => {
    const { openMuseDrawer, getAssetsByMove } = useRaptorflowStore()

    // Get deliverables from framework or slots
    const frameworkDeliverables = framework?.outputs?.deliverables || []
    const slotOutputs = move.slots?.outputs || []

    // Merge and create asset list
    const deliverables = frameworkDeliverables.map(d => ({
        ...d,
        status: 'not_started',
        // Check if we have an actual asset for this
        ...slotOutputs.find(o => o.id === d.id)
    }))

    // Get linked assets from store
    const linkedAssets = getAssetsByMove ? getAssetsByMove(move.id) : []

    const handleCreateInMuse = (deliverable) => {
        if (openMuseDrawer) {
            openMuseDrawer({
                context: `Create: ${deliverable.name}`,
                deliverableType: deliverable.type,
                moveName: move.name
            })
        }
    }

    return (
        <div className="max-w-3xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-lg font-medium text-foreground">Deliverables</h2>
                    <p className="text-sm text-muted-foreground">
                        {deliverables.filter(d => d.status === 'ready' || d.status === 'published').length} of {deliverables.length} complete
                    </p>
                </div>

                <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-xl text-sm font-medium hover:opacity-90 transition-opacity">
                    <Plus className="w-4 h-4" strokeWidth={1.5} />
                    Add Asset
                </button>
            </div>

            {/* Deliverables list */}
            <div className="space-y-3">
                {deliverables.map((deliverable, idx) => {
                    const Icon = TYPE_ICONS[deliverable.type] || TYPE_ICONS.default
                    const statusConfig = STATUS_CONFIG[deliverable.status] || STATUS_CONFIG.not_started
                    const StatusIcon = statusConfig.icon

                    return (
                        <motion.div
                            key={deliverable.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.05 }}
                            className="flex items-center gap-4 p-4 bg-card border border-border rounded-xl hover:border-primary/30 transition-colors"
                        >
                            {/* Type icon */}
                            <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center flex-shrink-0">
                                <Icon className="w-5 h-5 text-muted-foreground" strokeWidth={1.5} />
                            </div>

                            {/* Info */}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                    <h3 className="text-sm font-medium text-foreground truncate">
                                        {deliverable.name}
                                    </h3>
                                    {deliverable.required && (
                                        <span className="px-1.5 py-0.5 rounded text-[10px] bg-primary/10 text-primary font-medium">
                                            Required
                                        </span>
                                    )}
                                </div>
                                <div className="flex items-center gap-3 mt-1">
                                    <span className="text-xs text-muted-foreground capitalize">
                                        {deliverable.type}
                                    </span>
                                </div>
                            </div>

                            {/* Status */}
                            <div className={`
                flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium
                ${statusConfig.color === 'muted'
                                    ? 'bg-muted text-muted-foreground'
                                    : statusConfig.color === 'amber'
                                        ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
                                        : statusConfig.color === 'emerald'
                                            ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                                            : 'bg-primary/10 text-primary'
                                }
              `}>
                                <StatusIcon className="w-3 h-3" strokeWidth={1.5} />
                                {statusConfig.label}
                            </div>

                            {/* Action */}
                            <button
                                onClick={() => handleCreateInMuse(deliverable)}
                                className="px-4 py-2 text-sm text-primary hover:bg-primary/5 rounded-lg transition-colors"
                            >
                                {deliverable.status === 'not_started' ? 'Create' : 'Edit'}
                            </button>
                        </motion.div>
                    )
                })}
            </div>

            {/* Linked assets section */}
            {linkedAssets.length > 0 && (
                <div className="mt-8">
                    <h3 className="text-sm font-medium text-foreground mb-3">Linked Assets</h3>
                    <div className="space-y-2">
                        {linkedAssets.map((asset) => (
                            <div
                                key={asset.id}
                                className="flex items-center gap-3 p-3 bg-muted/50 border border-border rounded-xl"
                            >
                                <FileText className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
                                <span className="text-sm text-foreground flex-1">{asset.name || asset.title}</span>
                                <button className="text-xs text-primary hover:underline">Open</button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Empty state */}
            {deliverables.length === 0 && linkedAssets.length === 0 && (
                <div className="text-center py-12">
                    <div className="w-16 h-16 rounded-2xl bg-muted flex items-center justify-center mx-auto mb-4">
                        <FileText className="w-8 h-8 text-muted-foreground" strokeWidth={1.5} />
                    </div>
                    <h3 className="text-lg font-medium text-foreground mb-2">No assets yet</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                        Create your first deliverable to get started.
                    </p>
                    <button className="px-4 py-2 bg-primary text-primary-foreground rounded-xl text-sm font-medium hover:opacity-90 transition-opacity">
                        Create in Muse
                    </button>
                </div>
            )}
        </div>
    )
}

export default TabAssets
