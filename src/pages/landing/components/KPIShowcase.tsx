import { motion } from 'framer-motion'
import { HERO_STATS } from '@/data/landing-content'
import { Target, Zap, Sparkles } from 'lucide-react'

// Map stat labels to icons
const STAT_ICONS: Record<string, React.ElementType> = {
    'day war plan': Target,
    'execution speed': Zap,
    'clarity unlocked': Sparkles,
}

const StatCard = ({ stat, index }: { stat: { value: string; label: string }; index: number }) => {
    const Icon = STAT_ICONS[stat.label] || Sparkles

    return (
        <motion.div
            className="relative text-center px-4 first:pl-0 last:pr-0 group"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6 + index * 0.15, type: "spring", stiffness: 100 }}
        >
            {/* Animated icon above */}
            <motion.div
                className="flex justify-center mb-4"
                whileHover={{ scale: 1.1, rotate: 5 }}
            >
                <motion.div
                    className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 flex items-center justify-center border border-amber-500/20"
                    animate={{
                        boxShadow: [
                            '0 0 0 0 rgba(245, 158, 11, 0)',
                            '0 0 20px 4px rgba(245, 158, 11, 0.15)',
                            '0 0 0 0 rgba(245, 158, 11, 0)'
                        ]
                    }}
                    transition={{ duration: 3, repeat: Infinity, delay: index * 0.5 }}
                >
                    <Icon className="w-6 h-6 text-amber-500" />
                </motion.div>
            </motion.div>

            {/* Stat value */}
            <motion.div
                className="text-4xl md:text-6xl lg:text-7xl font-mono font-bold tracking-tighter bg-clip-text text-transparent bg-gradient-to-br from-amber-500 via-orange-500 to-amber-600"
                whileHover={{ scale: 1.1 }}
                transition={{ type: "spring", stiffness: 300 }}
            >
                {stat.value}
            </motion.div>

            {/* Label */}
            <div className="mt-3 text-xs md:text-sm text-muted-foreground font-medium uppercase tracking-widest leading-relaxed">
                {stat.label}
            </div>

            {/* Hover glow effect */}
            <motion.div
                className="absolute inset-0 -z-10 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                style={{
                    background: 'radial-gradient(circle at center, rgba(245, 158, 11, 0.1) 0%, transparent 70%)'
                }}
            />
        </motion.div>
    )
}

export const KPIShowcase = () => (
    <motion.div
        className="relative rounded-3xl border border-border bg-gradient-to-br from-card via-card to-muted/50 p-8 md:p-12 overflow-hidden shadow-2xl shadow-primary/5"
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
    >
        {/* Background glow */}
        <motion.div
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2/3 h-2/3 bg-primary/10 blur-[100px] rounded-full pointer-events-none"
            animate={{ scale: [1, 1.1, 1], opacity: [0.3, 0.5, 0.3] }}
            transition={{ duration: 5, repeat: Infinity }}
        />

        {/* Floating particles */}
        {[...Array(6)].map((_, i) => (
            <motion.div
                key={i}
                className="absolute w-1 h-1 rounded-full bg-amber-400/40"
                style={{
                    left: `${15 + i * 15}%`,
                    top: `${20 + (i % 3) * 25}%`,
                }}
                animate={{
                    y: [0, -20, 0],
                    opacity: [0.2, 0.6, 0.2],
                }}
                transition={{
                    duration: 3 + i * 0.5,
                    repeat: Infinity,
                    delay: i * 0.3,
                }}
            />
        ))}

        <div className="relative z-10 grid grid-cols-3 gap-8 md:gap-12 divide-x divide-border/50">
            {HERO_STATS.map((stat, i) => (
                <StatCard key={stat.label} stat={stat} index={i} />
            ))}
        </div>

        {/* Decorative corners with animation */}
        <motion.div
            className="absolute top-4 left-4 w-6 h-6 border-l-2 border-t-2 border-primary/30 rounded-tl-lg"
            animate={{ opacity: [0.3, 0.6, 0.3] }}
            transition={{ duration: 2, repeat: Infinity }}
        />
        <motion.div
            className="absolute top-4 right-4 w-6 h-6 border-r-2 border-t-2 border-primary/30 rounded-tr-lg"
            animate={{ opacity: [0.3, 0.6, 0.3] }}
            transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
        />
        <motion.div
            className="absolute bottom-4 left-4 w-6 h-6 border-l-2 border-b-2 border-primary/30 rounded-bl-lg"
            animate={{ opacity: [0.3, 0.6, 0.3] }}
            transition={{ duration: 2, repeat: Infinity, delay: 1 }}
        />
        <motion.div
            className="absolute bottom-4 right-4 w-6 h-6 border-r-2 border-b-2 border-primary/30 rounded-br-lg"
            animate={{ opacity: [0.3, 0.6, 0.3] }}
            transition={{ duration: 2, repeat: Infinity, delay: 1.5 }}
        />
    </motion.div>
)
