import { motion } from 'framer-motion'
import { HERO_STATS } from '@/data/landing-content'
import { Target, Zap, Trophy } from 'lucide-react'

// Clean icons for each stat - monochrome
const STAT_ICONS = [Target, Zap, Trophy]

export const KPIShowcase = () => (
    <motion.div
        className="relative rounded-3xl border border-zinc-200 p-10 md:p-14 overflow-hidden bg-white/70 backdrop-blur-sm"
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
    >
        {/* Subtle monochrome background glow */}
        <div
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full"
            style={{
                background: 'radial-gradient(ellipse at center, rgba(0, 0, 0, 0.02) 0%, transparent 70%)'
            }}
        />

        <div className="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-10 md:gap-8">
            {HERO_STATS.map((stat, i) => {
                const Icon = STAT_ICONS[i]
                return (
                    <motion.div
                        key={stat.label}
                        className="text-center group"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 + i * 0.1 }}
                    >
                        {/* Icon - Monochrome */}
                        <motion.div
                            className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-zinc-100 border border-zinc-200 mb-5"
                            whileHover={{ scale: 1.1, rotate: 5 }}
                            transition={{ type: "spring", stiffness: 300 }}
                        >
                            <Icon className="w-7 h-7 text-zinc-700" />
                        </motion.div>

                        {/* Value - Bold black */}
                        <motion.div
                            className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-zinc-900"
                            whileHover={{ scale: 1.05 }}
                        >
                            {stat.value}
                        </motion.div>

                        {/* Label */}
                        <div className="mt-3 text-sm md:text-base text-zinc-500 font-medium uppercase tracking-wider">
                            {stat.label}
                        </div>
                    </motion.div>
                )
            })}
        </div>

        {/* Decorative corners - Monochrome */}
        <div className="absolute top-4 left-4 w-8 h-8 border-l-2 border-t-2 border-zinc-300 rounded-tl-xl" />
        <div className="absolute top-4 right-4 w-8 h-8 border-r-2 border-t-2 border-zinc-300 rounded-tr-xl" />
        <div className="absolute bottom-4 left-4 w-8 h-8 border-l-2 border-b-2 border-zinc-300 rounded-bl-xl" />
        <div className="absolute bottom-4 right-4 w-8 h-8 border-r-2 border-b-2 border-zinc-300 rounded-br-xl" />
    </motion.div>
)

