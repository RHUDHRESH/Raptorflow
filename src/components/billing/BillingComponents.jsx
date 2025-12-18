/**
 * Enhanced Billing Components for Settings Page
 * Includes subscription management, plan upgrade, and cancellation flows
 */

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    CreditCard,
    ArrowRight,
    ArrowUpRight,
    Check,
    X,
    AlertTriangle,
    Loader,
    Calendar,
    Receipt,
    Download,
    Pause,
    Play,
    XCircle
} from 'lucide-react'
import { subscriptionsAPI } from '../../lib/api'
import { PLANS, PLAN_ORDER } from '../../config/plans'
import { useAuth } from '../../contexts/AuthContext'

// Plan Upgrade Modal
export const PlanUpgradeModal = ({ isOpen, onClose, currentPlanId, onSuccess }) => {
    const [selectedPlan, setSelectedPlan] = useState(null)
    const [proration, setProration] = useState(null)
    const [loading, setLoading] = useState(false)
    const [previewLoading, setPreviewLoading] = useState(false)
    const [error, setError] = useState('')

    const currentIndex = PLAN_ORDER.indexOf(currentPlanId)
    const availablePlans = PLAN_ORDER.filter((_, i) => i > currentIndex).map(id => PLANS[id])

    useEffect(() => {
        if (selectedPlan) {
            previewUpgrade(selectedPlan.id)
        }
    }, [selectedPlan])

    const previewUpgrade = async (planId) => {
        setPreviewLoading(true)
        setError('')
        try {
            const result = await subscriptionsAPI.previewUpgrade(planId)
            setProration(result)
        } catch (err) {
            setError(err.message)
        } finally {
            setPreviewLoading(false)
        }
    }

    const handleUpgrade = async () => {
        if (!selectedPlan) return
        setLoading(true)
        setError('')
        try {
            await subscriptionsAPI.upgrade(selectedPlan.id)
            onSuccess?.()
            onClose()
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="w-full max-w-2xl bg-card border border-border rounded-2xl overflow-hidden"
            >
                {/* Header */}
                <div className="p-6 border-b border-border">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="font-serif text-xl text-ink">Upgrade Your Plan</h2>
                            <p className="text-body-sm text-ink-400 mt-1">
                                Current plan: <span className="text-primary">{PLANS[currentPlanId]?.name}</span>
                            </p>
                        </div>
                        <button onClick={onClose} className="p-2 text-ink-400 hover:text-ink rounded-lg hover:bg-paper-200">
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6">
                    {error && (
                        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700 text-sm">
                            <AlertTriangle className="w-4 h-4" />
                            {error}
                        </div>
                    )}

                    {/* Plan selection */}
                    <div className="grid grid-cols-2 gap-4 mb-6">
                        {availablePlans.map(plan => (
                            <button
                                key={plan.id}
                                onClick={() => setSelectedPlan(plan)}
                                className={`p-4 rounded-xl border text-left transition-all ${selectedPlan?.id === plan.id
                                        ? 'border-primary bg-signal-muted ring-2 ring-primary/20'
                                        : 'border-border hover:border-ink-200'
                                    }`}
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <span className="font-medium text-ink">{plan.name}</span>
                                    {plan.recommended && (
                                        <span className="px-2 py-0.5 bg-primary text-white text-xs rounded-full">
                                            Recommended
                                        </span>
                                    )}
                                </div>
                                <div className="text-2xl font-mono text-ink mb-2">{plan.priceDisplay}<span className="text-sm text-ink-400">/mo</span></div>
                                <div className="text-body-xs text-ink-400">{plan.tagline}</div>
                            </button>
                        ))}
                    </div>

                    {/* Proration preview */}
                    {selectedPlan && (
                        <div className="p-4 bg-paper-200 rounded-xl">
                            <h4 className="text-body-sm font-medium text-ink mb-3">Upgrade Summary</h4>
                            {previewLoading ? (
                                <div className="flex items-center gap-2 text-ink-400">
                                    <Loader className="w-4 h-4 animate-spin" />
                                    Calculating...
                                </div>
                            ) : proration ? (
                                <div className="space-y-2 text-body-sm">
                                    <div className="flex justify-between">
                                        <span className="text-ink-400">Credit for remaining days</span>
                                        <span className="text-emerald-600">-₹{(proration.proration.creditPaise / 100).toFixed(2)}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-ink-400">New plan for remaining days</span>
                                        <span className="text-ink">₹{(proration.proration.chargePaise / 100).toFixed(2)}</span>
                                    </div>
                                    <div className="flex justify-between pt-2 border-t border-border font-medium">
                                        <span className="text-ink">Due now</span>
                                        <span className="text-primary text-lg">{proration.totalDueDisplay}</span>
                                    </div>
                                </div>
                            ) : null}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-border bg-paper-200 flex items-center justify-between">
                    <button onClick={onClose} className="px-4 py-2 text-ink-400 hover:text-ink">
                        Cancel
                    </button>
                    <button
                        onClick={handleUpgrade}
                        disabled={!selectedPlan || loading}
                        className="flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-xl hover:opacity-95 disabled:opacity-50"
                    >
                        {loading ? <Loader className="w-4 h-4 animate-spin" /> : <ArrowUpRight className="w-4 h-4" />}
                        Upgrade Now
                    </button>
                </div>
            </motion.div>
        </div>
    )
}

// Cancel Subscription Modal
export const CancelSubscriptionModal = ({ isOpen, onClose, subscription, onSuccess }) => {
    const [step, setStep] = useState('reason') // reason, confirm, done
    const [reason, setReason] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const reasons = [
        'Too expensive',
        'Not using it enough',
        'Missing features I need',
        'Found a better alternative',
        'Temporary pause needed',
        'Other'
    ]

    const handleCancel = async (immediate = false) => {
        setLoading(true)
        setError('')
        try {
            await subscriptionsAPI.cancel(immediate, reason)
            setStep('done')
            setTimeout(() => {
                onSuccess?.()
                onClose()
            }, 2000)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handlePause = async () => {
        setLoading(true)
        setError('')
        try {
            await subscriptionsAPI.pause()
            onSuccess?.()
            onClose()
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-lg bg-card border border-border rounded-2xl overflow-hidden"
            >
                {step === 'done' ? (
                    <div className="p-8 text-center">
                        <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <Check className="w-8 h-8 text-amber-600" />
                        </div>
                        <h3 className="font-serif text-xl text-ink mb-2">Subscription Cancelled</h3>
                        <p className="text-ink-400">You'll retain access until the end of your billing period.</p>
                    </div>
                ) : (
                    <>
                        <div className="p-6 border-b border-border">
                            <h2 className="font-serif text-xl text-ink">Cancel Subscription</h2>
                            <p className="text-body-sm text-ink-400 mt-1">We're sorry to see you go</p>
                        </div>

                        <div className="p-6">
                            {error && (
                                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                                    {error}
                                </div>
                            )}

                            {step === 'reason' && (
                                <>
                                    <p className="text-body-sm text-ink-400 mb-4">Help us improve by telling us why you're leaving:</p>
                                    <div className="space-y-2 mb-6">
                                        {reasons.map(r => (
                                            <button
                                                key={r}
                                                onClick={() => setReason(r)}
                                                className={`w-full p-3 rounded-lg border text-left text-body-sm transition-all ${reason === r
                                                        ? 'border-primary bg-signal-muted text-ink'
                                                        : 'border-border text-ink-400 hover:border-ink-200'
                                                    }`}
                                            >
                                                {r}
                                            </button>
                                        ))}
                                    </div>

                                    {/* Pause offer */}
                                    <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl mb-4">
                                        <h4 className="text-body-sm font-medium text-emerald-800 mb-2">
                                            Need a break instead?
                                        </h4>
                                        <p className="text-body-xs text-emerald-700 mb-3">
                                            Pause your subscription for 30 days instead of cancelling.
                                        </p>
                                        <button
                                            onClick={handlePause}
                                            disabled={loading}
                                            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm hover:bg-emerald-700"
                                        >
                                            <Pause className="w-4 h-4" />
                                            Pause for 30 days
                                        </button>
                                    </div>

                                    <button
                                        onClick={() => setStep('confirm')}
                                        disabled={!reason}
                                        className="w-full py-3 text-red-600 hover:bg-red-50 rounded-lg text-body-sm disabled:opacity-50"
                                    >
                                        Continue with cancellation
                                    </button>
                                </>
                            )}

                            {step === 'confirm' && (
                                <>
                                    <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl mb-4">
                                        <h4 className="text-body-sm font-medium text-amber-800 mb-2">What happens next:</h4>
                                        <ul className="text-body-xs text-amber-700 space-y-1">
                                            <li>• You'll keep access until {new Date(subscription?.currentPeriodEnd || Date.now()).toLocaleDateString()}</li>
                                            <li>• Your data will be preserved for 30 days</li>
                                            <li>• You can reactivate anytime before the period ends</li>
                                        </ul>
                                    </div>

                                    <div className="flex gap-3">
                                        <button
                                            onClick={() => setStep('reason')}
                                            className="flex-1 py-3 border border-border rounded-lg text-ink-400 hover:text-ink"
                                        >
                                            Go Back
                                        </button>
                                        <button
                                            onClick={() => handleCancel(false)}
                                            disabled={loading}
                                            className="flex-1 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                                        >
                                            {loading ? 'Processing...' : 'Confirm Cancellation'}
                                        </button>
                                    </div>
                                </>
                            )}
                        </div>
                    </>
                )}
            </motion.div>
        </div>
    )
}

// Enhanced Billing Tab
export const EnhancedBillingTab = () => {
    const { profile, refreshProfile } = useAuth()
    const [subscription, setSubscription] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [showUpgradeModal, setShowUpgradeModal] = useState(false)
    const [showCancelModal, setShowCancelModal] = useState(false)

    useEffect(() => {
        loadSubscription()
    }, [])

    const loadSubscription = async () => {
        setLoading(true)
        setError('')
        try {
            const result = await subscriptionsAPI.getCurrent()
            setSubscription(result.subscription)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleReactivate = async () => {
        try {
            await subscriptionsAPI.reactivate()
            await loadSubscription()
            refreshProfile?.()
        } catch (err) {
            setError(err.message)
        }
    }

    const handleResume = async () => {
        try {
            await subscriptionsAPI.resume()
            await loadSubscription()
            refreshProfile?.()
        } catch (err) {
            setError(err.message)
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <Loader className="w-6 h-6 animate-spin text-primary" />
            </div>
        )
    }

    const currentPlan = subscription?.planCode
        ? PLANS[subscription.planCode]
        : null

    const canUpgrade = subscription && PLAN_ORDER.indexOf(subscription.planCode) < PLAN_ORDER.length - 1
    const isCancelled = subscription?.cancelAtPeriodEnd
    const isPaused = subscription?.status === 'paused'

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h2 className="font-serif text-xl text-ink">Billing</h2>
                <p className="text-body-sm text-ink-400">Manage your subscription and payments</p>
            </div>

            {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-2 text-red-700 text-sm">
                    <AlertTriangle className="w-4 h-4" />
                    {error}
                </div>
            )}

            {/* Status banner for cancelled/paused */}
            {isCancelled && (
                <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl">
                    <div className="flex items-center justify-between">
                        <div>
                            <h4 className="text-body-sm font-medium text-amber-800">Subscription Ending</h4>
                            <p className="text-body-xs text-amber-700">
                                Your access ends on {new Date(subscription.currentPeriodEnd).toLocaleDateString()}
                            </p>
                        </div>
                        <button
                            onClick={handleReactivate}
                            className="px-4 py-2 bg-amber-600 text-white rounded-lg text-sm hover:bg-amber-700"
                        >
                            Reactivate
                        </button>
                    </div>
                </div>
            )}

            {isPaused && (
                <div className="p-4 bg-orange-50 border border-orange-200 rounded-xl">
                    <div className="flex items-center justify-between">
                        <div>
                            <h4 className="text-body-sm font-medium text-orange-800">Subscription Paused</h4>
                            <p className="text-body-xs text-orange-700">Your subscription is currently paused</p>
                        </div>
                        <button
                            onClick={handleResume}
                            className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg text-sm hover:bg-orange-700"
                        >
                            <Play className="w-4 h-4" />
                            Resume
                        </button>
                    </div>
                </div>
            )}

            {/* Current plan card */}
            {subscription && currentPlan && (
                <div className="bg-card border border-primary rounded-xl p-6">
                    <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 bg-signal-muted rounded-xl flex items-center justify-center">
                                <CreditCard className="w-6 h-6 text-primary" strokeWidth={1.5} />
                            </div>
                            <div>
                                <div className="text-body-sm text-ink-400">Current Plan</div>
                                <div className="text-xl font-serif text-ink">{currentPlan.name}</div>
                            </div>
                        </div>
                        <div className="text-right">
                            <div className="text-2xl font-mono text-ink">{currentPlan.priceDisplay}</div>
                            <div className="text-body-xs text-ink-400">per month</div>
                        </div>
                    </div>

                    {/* Billing cycle info */}
                    <div className="flex items-center gap-4 py-4 border-t border-border-light text-body-sm">
                        <div className="flex items-center gap-2">
                            <Calendar className="w-4 h-4 text-ink-400" />
                            <span className="text-ink-400">Next billing:</span>
                            <span className="text-ink">{new Date(subscription.currentPeriodEnd).toLocaleDateString()}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-ink-400">Days remaining:</span>
                            <span className="text-ink font-mono">{subscription.daysRemaining}</span>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-3 pt-4 border-t border-border-light">
                        {canUpgrade && !isCancelled && (
                            <button
                                onClick={() => setShowUpgradeModal(true)}
                                className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg text-sm hover:opacity-95"
                            >
                                <ArrowUpRight className="w-4 h-4" />
                                Upgrade Plan
                            </button>
                        )}
                        {!isCancelled && !isPaused && (
                            <button
                                onClick={() => setShowCancelModal(true)}
                                className="flex items-center gap-2 px-4 py-2 text-ink-400 hover:text-red-600 rounded-lg text-sm hover:bg-red-50"
                            >
                                <XCircle className="w-4 h-4" />
                                Cancel Subscription
                            </button>
                        )}
                    </div>
                </div>
            )}

            {/* No subscription */}
            {!subscription && (
                <div className="bg-paper-200 border border-border rounded-xl p-8 text-center">
                    <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                        <CreditCard className="w-8 h-8 text-ink-400" />
                    </div>
                    <h3 className="font-serif text-lg text-ink mb-2">No Active Subscription</h3>
                    <p className="text-body-sm text-ink-400 mb-4">Choose a plan to get started with RaptorFlow</p>
                    <a href="/pricing" className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-xl">
                        View Plans <ArrowRight className="w-4 h-4" />
                    </a>
                </div>
            )}

            {/* Plan Features */}
            {currentPlan && (
                <div className="bg-card border border-border rounded-xl p-6">
                    <h3 className="text-body-sm font-medium text-ink mb-4">Plan Features</h3>
                    <div className="grid grid-cols-2 gap-3">
                        {currentPlan.features.map((feature, i) => (
                            <div key={i} className="flex items-center gap-2 text-body-sm">
                                <Check className="w-4 h-4 text-emerald-500" />
                                <span className="text-ink">{feature}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Modals */}
            <AnimatePresence>
                {showUpgradeModal && subscription && (
                    <PlanUpgradeModal
                        isOpen={showUpgradeModal}
                        onClose={() => setShowUpgradeModal(false)}
                        currentPlanId={subscription.planCode}
                        onSuccess={() => {
                            loadSubscription()
                            refreshProfile?.()
                        }}
                    />
                )}
                {showCancelModal && (
                    <CancelSubscriptionModal
                        isOpen={showCancelModal}
                        onClose={() => setShowCancelModal(false)}
                        subscription={subscription}
                        onSuccess={() => {
                            loadSubscription()
                            refreshProfile?.()
                        }}
                    />
                )}
            </AnimatePresence>
        </div>
    )
}

export default EnhancedBillingTab
