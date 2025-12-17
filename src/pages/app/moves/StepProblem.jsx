import { motion } from 'framer-motion'
import { Check, Target, Clock } from 'lucide-react'
import { PROBLEM_TYPES } from '../../../data/frameworkConfigs'
import { BrandIcon } from '@/components/brand/BrandSystem'

/**
 * Step 1: Pick the Problem
 * 
 * Users select from 8 core problems/jobs they want to solve.
 * This is the entry point - not frameworks.
 */

const ProblemCard = ({ problem, isSelected, onSelect }) => {
    return (
        <motion.button
            onClick={onSelect}
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.99 }}
            className={`
        relative p-4 text-left rounded-xl border transition-all duration-200 h-full flex flex-col group
        ${isSelected
                    ? 'border-primary bg-primary/5 shadow-sm ring-1 ring-primary/20'
                    : 'border-border hover:border-primary/50 bg-card hover:bg-muted/30'
                }
      `}
        >
            {/* Selected check */}
            {isSelected && (
                <div className="absolute top-3 right-3 text-primary">
                    <div className="w-5 h-5 bg-primary rounded-full flex items-center justify-center">
                        <Check className="w-3 h-3 text-primary-foreground" strokeWidth={3} />
                    </div>
                </div>
            )}

            <div className="flex items-start gap-3 mb-2">
                <div className={`
          w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 transition-colors
          ${isSelected ? 'bg-primary/20 text-primary' : 'bg-muted text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary'}
        `}>
                    <BrandIcon name={problem.icon} size={16} />
                </div>
                <div className="flex-1 min-w-0 pr-6">
                    <h3 className={`font-serif text-base leading-tight mb-1 ${isSelected ? 'text-primary' : 'text-foreground'}`}>
                        "{problem.statement}"
                    </h3>
                    <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                        {problem.goal}
                    </div>
                </div>
            </div>

            <p className="text-xs text-muted-foreground mb-3 flex-1 line-clamp-2">
                {problem.description}
            </p>

            <div className="flex items-center gap-3 pt-3 border-t border-border/50 text-[10px] text-muted-foreground">
                <div className="flex items-center gap-1">
                    <Target className="w-3 h-3" />
                    <span className="truncate max-w-[80px]">{problem.defaultKpi}</span>
                </div>
                <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span>{problem.defaultDuration}d</span>
                </div>
            </div>
        </motion.button>
    )
}

const StepProblem = ({ data, updateData, onNext }) => {
    const problems = Object.values(PROBLEM_TYPES)

    const handleSelect = (problemId) => {
        updateData('problemType', problemId)
    }

    return (
        <div className="max-w-6xl mx-auto pb-12">
            {/* Compact Header */}
            <div className="text-center mb-8">
                <h1 className="font-serif text-2xl text-foreground mb-2">
                    What's your biggest challenge?
                </h1>
                <p className="text-sm text-muted-foreground max-w-lg mx-auto">
                    Select a problem to start resolving it.
                </p>
            </div>

            {/* Dense Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {problems.map((problem) => (
                    <ProblemCard
                        key={problem.id}
                        problem={problem}
                        isSelected={data.problemType === problem.id}
                        onSelect={() => handleSelect(problem.id)}
                    />
                ))}
            </div>

            {/* Helper Text */}
            <div className="mt-8 text-center">
                <p className="text-xs text-muted-foreground">
                    Tip: Pick the one that hurts the most right now. You can run more moves later.
                </p>
            </div>
        </div>
    )
}

export default StepProblem
