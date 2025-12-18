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
    AlertCircle,
    LayoutGrid,
    PenTool
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
    not_started: { label: 'Pending', icon: Clock, color: 'muted' },
    in_progress: { label: 'Drafting', icon: PenTool, color: 'amber' },
    ready: { label: 'Review Ready', icon: AlertCircle, color: 'blue' },
    published: { label: 'Shipped', icon: Check, color: 'emerald' }
}

const TYPE_ICONS = {
    document: FileText,
    article: FileText,
    page: LayoutGrid,
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

    const completedCount = deliverables.filter(d => d.status === 'ready' || d.status === 'published').length
    const totalCount = deliverables.length
    const completionPercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0

    return (
        <div className="max-w-3xl mx-auto pb-12">
            {/* Header Stats */}
            <div className="flex items-center justify-between mb-8 p-4 bg-muted/30 border border-border/60 rounded-xl">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-sm">
                        {completionPercent}%
                    </div>
                    <div>
                        <h2 className="text-sm font-bold text-foreground uppercase tracking-wide">Payload Manifest</h2>
                        <p className="text-xs text-muted-foreground">
                            {completedCount} of {totalCount} assets ready for deployment
                        </p>
                    </div>
                </div>

                <button className="flex items-center gap-2 px-3 py-2 bg-primary text-primary-foreground rounded-lg text-xs font-bold hover:opacity-90 transition-opacity uppercase tracking-wider">
                    <Plus className="w-3 h-3" strokeWidth={3} />
                    New Asset
                </button>
            </div>

            {/* Deliverables list */}
            <div className="space-y-3">
                {deliverables.length > 0 ? (
                    deliverables.map((deliverable, idx) => {
                        const Icon = TYPE_ICONS[deliverable.type] || TYPE_ICONS.default
                        const statusConfig = STATUS_CONFIG[deliverable.status] || STATUS_CONFIG.not_started
                        const StatusIcon = statusConfig.icon

                        return (
                            <motion.div
                                key={deliverable.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.05 }}
                                className="group flex items-center gap-4 p-4 bg-card border border-border rounded-xl transition-all hover:border-primary/40 hover:shadow-sm"
                            >
                                {/* Type icon */}
                                <div className="w-10 h-10 rounded-lg bg-muted/50 group-hover:bg-primary/5 flex items-center justify-center flex-shrink-0 transition-colors">
                                    <Icon className="w-5 h-5 text-muted-foreground group-hover:text-primary" strokeWidth={1.5} />
                                </div>

                                {/* Info */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                        <h3 className="text-sm font-bold text-foreground truncate">
                                            {deliverable.name}
                                        </h3>
                                        {deliverable.required && (
                                            <span className="px-1.5 py-0.5 rounded text-[9px] uppercase font-bold bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300">
                                                Required
                                            </span>
                                        )}
                                    </div>
                                    <div className="flex items-center gap-3 mt-0.5">
                                        <span className="text-xs text-muted-foreground capitalize">
                                            {deliverable.type}
                                        </span>
                                    </div>
                                </div>

                                {/* Status */}
                                <div className={`
                                flex items-center gap-1.5 px-2.5 py-1 rounded text-[10px] font-bold uppercase tracking-wide
                                ${statusConfig.color === 'muted'
                                        ? 'bg-muted text-muted-foreground'
                                        : statusConfig.color === 'amber'
                                            ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
                                            : statusConfig.color === 'blue'
                                                ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400'
                                                : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                                    }
                            `}>
                                    <StatusIcon className="w-3 h-3" strokeWidth={2} />
                                    {statusConfig.label}
                                </div>

                                {/* Action */}
                                <button
                                    onClick={() => handleCreateInMuse(deliverable)}
                                    className="px-3 py-1.5 text-xs font-medium text-foreground hover:bg-muted rounded-lg transition-colors border border-transparent hover:border-border"
                                >
                                    {deliverable.status === 'not_started' ? 'Initialize' : 'Edit'}
                                </button>
                            </motion.div>
                        )
                    })
                ) : (
                    <div className="text-center py-16 border-2 border-dashed border-border/50 rounded-2xl bg-muted/10">
                        <div className="w-16 h-16 rounded-2xl bg-muted/50 flex items-center justify-center mx-auto mb-4">
                            <FileText className="w-8 h-8 text-muted-foreground" strokeWidth={1.5} />
                        </div>
                        <h3 className="text-lg font-bold text-foreground mb-1">No Assets Required</h3>
                        <p className="text-sm text-muted-foreground mb-6 max-w-xs mx-auto">
                            This move doesn't require any pre-defined assets. You can add ad-hoc items if needed.
                        </p>
                        <button className="px-4 py-2 bg-primary text-primary-foreground rounded-xl text-sm font-bold hover:opacity-90 transition-opacity">
                            Create Ad-Hoc Asset
                        </button>
                    </div>
                )}

            </div>

            {/* Linked assets section */}
            {linkedAssets.length > 0 && (
                <div className="mt-8 pt-8 border-t border-border">
                    <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-3">Linked Resources</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {linkedAssets.map((asset) => (
                            <div
                                key={asset.id}
                                className="flex items-center gap-3 p-3 bg-muted/30 border border-border rounded-xl hover:border-primary/30 transition-colors"
                            >
                                <FileText className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
                                <span className="text-sm text-foreground flex-1 truncate">{asset.name || asset.title}</span>
                                <button className="text-xs text-primary font-bold hover:underline">OPEN</button>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}

export default TabAssets
