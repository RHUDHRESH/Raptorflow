import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { Check, X, AlertCircle, ChevronRight } from 'lucide-react'

/**
 * Step 5: Preflight Check (Hard Gate)
 * 
 * Validates all required fields before allowing the Move to start.
 * This is a hard gate - can't proceed without passing all checks.
 */

const CheckItem = ({ label, passed, onFix, category }) => (
    <div className={`
    flex items-center gap-3 p-4 rounded-xl border transition-all
    ${passed
            ? 'bg-emerald-50 border-emerald-200 dark:bg-emerald-900/20 dark:border-emerald-800'
            : 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800'
        }
  `}>
        <div className={`
      w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0
      ${passed
                ? 'bg-emerald-500 text-white'
                : 'bg-red-500 text-white'
            }
    `}>
            {passed ? (
                <Check className="w-4 h-4" strokeWidth={2} />
            ) : (
                <X className="w-4 h-4" strokeWidth={2} />
            )}
        </div>

        <span className={`flex-1 text-sm ${passed ? 'text-emerald-700 dark:text-emerald-300' : 'text-red-700 dark:text-red-300'}`}>
            {label}
        </span>

        {!passed && onFix && (
            <button
                onClick={onFix}
                className="flex items-center gap-1 px-3 py-1.5 bg-red-100 hover:bg-red-200 dark:bg-red-900/40 dark:hover:bg-red-900/60 text-red-700 dark:text-red-300 rounded-lg text-xs font-medium transition-colors"
            >
                Fix now
                <ChevronRight className="w-3 h-3" strokeWidth={2} />
            </button>
        )}
    </div>
)

const CheckCategory = ({ title, icon: Icon, checks }) => {
    const allPassed = checks.every(c => c.passed)
    const passedCount = checks.filter(c => c.passed).length

    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-foreground flex items-center gap-2">
                    {Icon && <Icon className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />}
                    {title}
                </h3>
                <span className={`
          text-xs font-medium px-2 py-0.5 rounded-full
          ${allPassed
                        ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                        : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                    }
        `}>
                    {passedCount}/{checks.length} passed
                </span>
            </div>

            <div className="space-y-2">
                {checks.map((check, idx) => (
                    <CheckItem key={idx} {...check} />
                ))}
            </div>
        </div>
    )
}

const StepPreflight = ({ data, updateData, onPrev, goToStep }) => {
    const framework = data.selectedFramework

    // Run all preflight checks
    const preflightResults = useMemo(() => {
        if (!framework) return { passed: false, categories: [] }

        const results = {
            offer: [],
            tracking: [],
            outputs: [],
            channels: []
        }

        // Offer requirements (Step 4)
        framework.inputs.fields.forEach(field => {
            if (field.required) {
                const value = data.slots.inputs?.[field.id]
                results.offer.push({
                    label: field.label,
                    passed: !!value && value.toString().trim().length > 0,
                    category: 'offer',
                    step: 4
                })
            }
        })

        // Rules enforcement (Step 5)
        framework.rules.required.forEach(rule => {
            results.offer.push({
                label: rule.label,
                passed: true, // Required rules are always "on"
                category: 'offer',
                step: 5
            })
        })

        // Tracking requirements (Step 9)
        const metrics = data.slots.metrics || {}
        results.tracking.push({
            label: 'Primary KPI selected',
            passed: true, // Framework provides default
            category: 'tracking',
            step: 9
        })
        results.tracking.push({
            label: 'Baseline added',
            passed: !!metrics.baseline,
            category: 'tracking',
            step: 9
        })
        results.tracking.push({
            label: 'Target defined',
            passed: !!metrics.target,
            category: 'tracking',
            step: 9
        })

        // Outputs (Step 7)
        const outputs = data.slots.outputs || framework.outputs.deliverables
        const requiredOutputs = outputs.filter(o => o.required)
        results.outputs.push({
            label: `${requiredOutputs.length} required deliverables ready`,
            passed: requiredOutputs.length > 0,
            category: 'outputs',
            step: 7
        })

        // Channels (Step 8)
        const channels = data.slots.channels || framework.channels.recommended
        results.channels.push({
            label: 'At least 1 channel selected',
            passed: channels.length > 0,
            category: 'channels',
            step: 8
        })
        results.channels.push({
            label: 'Not too many channels (1-2 recommended)',
            passed: channels.length <= 2,
            category: 'channels',
            step: 8
        })

        // Check if all passed
        const allChecks = [...results.offer, ...results.tracking, ...results.outputs, ...results.channels]
        const allPassed = allChecks.every(c => c.passed)

        return {
            passed: allPassed,
            categories: [
                { id: 'offer', title: 'Offer Requirements', checks: results.offer },
                { id: 'tracking', title: 'Tracking', checks: results.tracking },
                { id: 'outputs', title: 'Outputs', checks: results.outputs },
                { id: 'channels', title: 'Channels', checks: results.channels }
            ],
            summary: {
                total: allChecks.length,
                passed: allChecks.filter(c => c.passed).length,
                failed: allChecks.filter(c => !c.passed).length
            }
        }
    }, [framework, data.slots])

    // Update parent with preflight status
    useMemo(() => {
        updateData('preflightPassed', preflightResults.passed)
    }, [preflightResults.passed, updateData])

    if (!framework) {
        return (
            <div className="text-center py-12">
                <p className="text-muted-foreground">Please select a framework first.</p>
            </div>
        )
    }

    return (
        <div className="pb-24 max-w-2xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Header */}
            <div className="text-center mb-8">
                <h1 className="font-serif text-3xl text-foreground mb-3">
                    Preflight Check
                </h1>
                <p className="text-muted-foreground">
                    Let's make sure everything is ready before you launch.
                </p>
            </div>

            {/* Overall status */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`
          p-6 rounded-2xl border-2 mb-8
          ${preflightResults.passed
                        ? 'bg-emerald-50 border-emerald-200 dark:bg-emerald-900/20 dark:border-emerald-800'
                        : 'bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800'
                    }
        `}
            >
                <div className="flex items-center gap-4">
                    <div className={`
            w-12 h-12 rounded-xl flex items-center justify-center
            ${preflightResults.passed
                            ? 'bg-emerald-500 text-white'
                            : 'bg-amber-500 text-white'
                        }
          `}>
                        {preflightResults.passed ? (
                            <Check className="w-6 h-6" strokeWidth={2} />
                        ) : (
                            <AlertCircle className="w-6 h-6" strokeWidth={2} />
                        )}
                    </div>

                    <div className="flex-1">
                        <h2 className={`font-medium ${preflightResults.passed ? 'text-emerald-700 dark:text-emerald-300' : 'text-amber-700 dark:text-amber-300'}`}>
                            {preflightResults.passed
                                ? 'All checks passed! Ready to launch.'
                                : `${preflightResults.summary.failed} check${preflightResults.summary.failed > 1 ? 's' : ''} need attention`
                            }
                        </h2>
                        <p className={`text-sm ${preflightResults.passed ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'}`}>
                            {preflightResults.summary.passed} of {preflightResults.summary.total} requirements met
                        </p>
                    </div>
                </div>
            </motion.div>

            {/* Check categories */}
            <div className="space-y-8">
                {preflightResults.categories.map((category, idx) => (
                    category.checks.length > 0 && (
                        <motion.div
                            key={category.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.1 }}
                        >
                            <CheckCategory
                                title={category.title}
                                checks={category.checks.map(check => ({
                                    ...check,
                                    onFix: !check.passed ? () => goToStep(check.step) : undefined
                                }))}
                            />
                        </motion.div>
                    )
                ))}
            </div>

            {/* Warning if not passed */}
            {!preflightResults.passed && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4 }}
                    className="mt-8 p-4 rounded-xl bg-muted border border-border"
                >
                    <div className="flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                        <div>
                            <h4 className="text-sm font-medium text-foreground mb-1">
                                Can't start until all checks pass
                            </h4>
                            <p className="text-sm text-muted-foreground">
                                Go back and fix the issues above to unlock the Start button.
                            </p>
                        </div>
                    </div>
                </motion.div>
            )}
        </div>
    )
}

export default StepPreflight
