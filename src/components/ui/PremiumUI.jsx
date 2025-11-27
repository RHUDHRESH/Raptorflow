import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Loader2, X, Check, ChevronRight, AlertCircle } from 'lucide-react'
import { cn } from '../../utils/cn'
import { cardHover, fadeInUp, fadeInScale } from '../../utils/animations'

// --- Typography ---
export const LuxeHeading = ({ level = 1, children, className, ...props }) => {
    const Tag = `h${level}`
    const sizes = {
        1: "text-4xl md:text-5xl font-black tracking-tight",
        2: "text-3xl md:text-4xl font-bold tracking-tight",
        3: "text-2xl font-bold tracking-tight",
        4: "text-xl font-bold",
        5: "text-lg font-semibold",
        6: "text-base font-semibold uppercase tracking-wider"
    }

    return (
        <Tag className={cn("font-serif text-neutral-900", sizes[level], className)} {...props}>
            {children}
        </Tag>
    )
}

// --- Buttons ---
export const LuxeButton = ({
    children,
    variant = 'primary',
    size = 'md',
    className,
    isLoading,
    icon: Icon,
    disabled,
    ...props
}) => {
    const variants = {
        primary: "bg-neutral-900 text-white hover:bg-neutral-800 border border-transparent shadow-lg shadow-neutral-900/20",
        secondary: "bg-white text-neutral-900 border border-neutral-200 hover:border-neutral-900 hover:bg-neutral-50",
        ghost: "bg-transparent text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100/50 border border-transparent",
        danger: "bg-red-50 text-red-600 border border-red-100 hover:bg-red-100 hover:border-red-200"
    }

    const sizes = {
        sm: "px-3 py-1.5 text-xs",
        md: "px-5 py-2.5 text-sm",
        lg: "px-8 py-3.5 text-base"
    }

    return (
        <motion.button
            whileHover={!disabled && !isLoading ? { scale: 1.02 } : {}}
            whileTap={!disabled && !isLoading ? { scale: 0.98 } : {}}
            className={cn(
                "relative inline-flex items-center justify-center gap-2 rounded-xl font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed",
                variants[variant],
                sizes[size],
                className
            )}
            disabled={disabled || isLoading}
            {...props}
        >
            {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
            {!isLoading && Icon && <Icon className="w-4 h-4" />}
            {children}
        </motion.button>
    )
}

// --- Cards ---
export const LuxeCard = ({ children, className, hover = true, onClick, delay = 0, ...props }) => {
    return (
        <motion.div
            initial="hidden"
            animate="show"
            variants={fadeInUp}
            custom={delay}
            whileHover={hover && onClick ? "hover" : undefined}
            whileTap={hover && onClick ? "tap" : undefined}
            onClick={onClick}
            className={cn(
                "bg-white border border-neutral-200 rounded-xl p-6 transition-colors",
                onClick && "cursor-pointer",
                className
            )}
            {...props}
        >
            {children}
        </motion.div>
    )
}

// --- Inputs ---
export const LuxeInput = ({ label, error, className, id, ...props }) => {
    return (
        <div className="space-y-1.5 w-full">
            {label && (
                <label htmlFor={id} className="text-sm font-medium text-neutral-700 ml-1">
                    {label}
                </label>
            )}
            <div className="relative">
                <input
                    id={id}
                    className={cn(
                        "w-full h-11 px-4 rounded-xl border bg-neutral-50/50 text-neutral-900 placeholder:text-neutral-400 transition-all focus:bg-white focus:ring-2 focus:ring-neutral-900/5 outline-none",
                        error
                            ? "border-red-300 focus:border-red-400 focus:ring-red-100"
                            : "border-neutral-200 focus:border-neutral-900",
                        className
                    )}
                    {...props}
                />
            </div>
            {error && (
                <motion.p
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-xs text-red-500 font-medium ml-1 flex items-center gap-1"
                >
                    <AlertCircle className="w-3 h-3" /> {error}
                </motion.p>
            )}
        </div>
    )
}

// --- Modals ---
export const LuxeModal = ({ isOpen, onClose, title, children, size = 'md' }) => {
    const sizes = {
        sm: "max-w-md",
        md: "max-w-2xl",
        lg: "max-w-4xl",
        xl: "max-w-6xl"
    }

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-neutral-900/40 backdrop-blur-sm z-50"
                    />
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            className={cn(
                                "w-full bg-white rounded-2xl shadow-2xl overflow-hidden pointer-events-auto flex flex-col max-h-[90vh]",
                                sizes[size]
                            )}
                        >
                            <div className="flex items-center justify-between p-6 border-b border-neutral-100 bg-white sticky top-0 z-10">
                                <h3 className="font-serif text-xl font-bold text-neutral-900">{title}</h3>
                                <button
                                    onClick={onClose}
                                    className="p-2 rounded-full hover:bg-neutral-100 text-neutral-500 hover:text-neutral-900 transition-colors"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>
                            <div className="p-6 overflow-y-auto custom-scrollbar">
                                {children}
                            </div>
                        </motion.div>
                    </div>
                </>
            )}
        </AnimatePresence>
    )
}

// --- Badges ---
export const LuxeBadge = ({ children, variant = 'neutral', className }) => {
    const variants = {
        neutral: "bg-neutral-100 text-neutral-600 border-neutral-200",
        dark: "bg-neutral-900 text-white border-neutral-900",
        success: "bg-green-50 text-green-700 border-green-200",
        warning: "bg-amber-50 text-amber-700 border-amber-200",
        error: "bg-red-50 text-red-700 border-red-200",
        info: "bg-blue-50 text-blue-700 border-blue-200"
    }

    return (
        <span className={cn(
            "inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border",
            variants[variant],
            className
        )}>
            {children}
        </span>
    )
}

// --- Stats ---
export const LuxeStat = ({ label, value, trend, icon: Icon, delay = 0 }) => {
    return (
        <LuxeCard className="relative overflow-hidden group" delay={delay}>
            <div className="flex items-start justify-between mb-4">
                <div>
                    <p className="text-xs font-medium text-neutral-500 uppercase tracking-wider mb-1">{label}</p>
                    <h4 className="font-serif text-3xl font-bold text-neutral-900">{value}</h4>
                </div>
                {Icon && (
                    <div className="w-10 h-10 rounded-full bg-neutral-50 flex items-center justify-center group-hover:bg-neutral-900 group-hover:text-white transition-colors duration-300">
                        <Icon className="w-5 h-5" />
                    </div>
                )}
            </div>
            {trend && (
                <div className={cn(
                    "text-xs font-medium flex items-center gap-1",
                    trend > 0 ? "text-green-600" : "text-red-600"
                )}>
                    {trend > 0 ? "+" : ""}{trend}%
                    <span className="text-neutral-400 font-normal">vs last month</span>
                </div>
            )}
        </LuxeCard>
    )
}
