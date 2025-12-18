import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence, useMotionValue, useTransform, useSpring } from 'framer-motion'
import {
    Check,
    Sparkles,
    BarChart3,
    Target,
    ArrowRight,
    Zap,
    TrendingUp,
    Copy,
    RefreshCw,
    Trophy,
    Flame,
    Star,
    Heart,
    Rocket
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Link } from 'react-router-dom'

// ═══════════════════════════════════════════════════════════════════════════════
// INTERACTIVE PLAYGROUND - Mind-blowing, cute, and impressive!
// ═══════════════════════════════════════════════════════════════════════════════

type PlaygroundTab = 'matrix' | 'muse' | 'blackbox'

// Confetti particle component
const Confetti = ({ x, y }: { x: number; y: number }) => {
    const colors = [
        'hsl(var(--primary))',
        'hsl(var(--destructive))',
        'var(--success-500)',
        'var(--info-500)',
        'var(--zinc-400)',
        'var(--rust-600)',
    ]

    return (
        <div className="fixed pointer-events-none z-50" style={{ left: x, top: y }}>
            {[...Array(20)].map((_, i) => (
                <motion.div
                    key={i}
                    className="absolute w-2 h-2 rounded-full"
                    style={{ backgroundColor: colors[i % colors.length] }}
                    initial={{
                        x: 0,
                        y: 0,
                        scale: 1,
                        opacity: 1
                    }}
                    animate={{
                        x: (Math.random() - 0.5) * 200,
                        y: (Math.random() - 0.5) * 200 - 50,
                        scale: 0,
                        opacity: 0,
                        rotate: Math.random() * 360
                    }}
                    transition={{
                        duration: 0.8 + Math.random() * 0.4,
                        ease: "easeOut"
                    }}
                />
            ))}
        </div>
    )
}

// Star burst effect
const StarBurst = ({ show }: { show: boolean }) => (
    <AnimatePresence>
        {show && (
            <motion.div
                className="absolute inset-0 pointer-events-none"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
            >
                {[...Array(6)].map((_, i) => (
                    <motion.div
                        key={i}
                        className="absolute left-1/2 top-1/2"
                        initial={{ scale: 0, rotate: i * 60 }}
                        animate={{ scale: [0, 1, 0], rotate: i * 60 + 30 }}
                        transition={{ duration: 0.5 }}
                    >
                        <Star className="w-4 h-4 text-zinc-400 fill-zinc-400" />
                    </motion.div>
                ))}
            </motion.div>
        )}
    </AnimatePresence>
)

// Sample data
const DEMO_TASKS = [
    { id: 1, text: 'Post LinkedIn carousel about ICP pain points', emoji: '📝', done: false },
    { id: 2, text: 'Send follow-up email to webinar attendees', emoji: '📧', done: false },
    { id: 3, text: 'Review Black Box test results for CTA variants', emoji: '🧪', done: false },
    { id: 4, text: 'Schedule 3 tweets for product launch', emoji: '🚀', done: true },
]

const DEMO_GENERATED_CONTENT = {
    linkedin: [
        "🔥 Stop wasting hours on marketing that doesn't convert.\n\nHere's what most founders get wrong:\n→ Random posting without strategy\n→ No clear message or positioning\n→ Zero tracking of what works\n\nThe fix? A system that tells you exactly what to do today.\n\n#marketing #founders #startup",
    ],
    email: [
        "Subject: Your marketing shouldn't feel like gambling 🎰\n\nHey {{first_name}},\n\nQuick question: How many hours did you spend last week deciding what to post?\n\nIf the answer is 'too many' — you're not alone.\n\nLet me show you a better way.\n\nBest,\n[Your name]",
    ],
    tweet: [
        "Marketing tip that saved my startup:\n\nStop asking 'what should I post?'\n\nStart asking 'what does my ICP need to hear today?'\n\nThe answer writes itself. 🧵✨",
    ],
    ad: [
        "🎯 HEADLINE: Stop Guessing. Start Winning.\n\n📝 PRIMARY TEXT:\nTired of marketing that doesn't convert?\n\nRaptorFlow gives you:\n✓ Daily execution checklists\n✓ AI-powered content\n✓ Automatic A/B testing\n\n🔥 Join 500+ founders who stopped guessing.",
    ]
}

const CONTENT_TYPES = [
    { id: 'linkedin', label: 'LinkedIn', icon: '💼', color: 'from-gray-500 to-gray-600' },
    { id: 'email', label: 'Email', icon: '📧', color: 'from-emerald-500 to-emerald-600' },
    { id: 'tweet', label: 'Tweet', icon: '🐦', color: 'from-gray-400 to-gray-500' },
    { id: 'ad', label: 'Ad Copy', icon: '📢', color: 'from-purple-500 to-purple-600' },
] as const

type ContentType = typeof CONTENT_TYPES[number]['id']

// 3D Tilt Card wrapper
const TiltCard = ({ children, className }: { children: React.ReactNode; className?: string }) => {
    const ref = useRef<HTMLDivElement>(null)
    const x = useMotionValue(0)
    const y = useMotionValue(0)

    const rotateX = useTransform(y, [-100, 100], [5, -5])
    const rotateY = useTransform(x, [-100, 100], [-5, 5])

    const springRotateX = useSpring(rotateX, { stiffness: 300, damping: 30 })
    const springRotateY = useSpring(rotateY, { stiffness: 300, damping: 30 })

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!ref.current) return
        const rect = ref.current.getBoundingClientRect()
        const centerX = rect.left + rect.width / 2
        const centerY = rect.top + rect.height / 2
        x.set(e.clientX - centerX)
        y.set(e.clientY - centerY)
    }

    const handleMouseLeave = () => {
        x.set(0)
        y.set(0)
    }

    return (
        <motion.div
            ref={ref}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            style={{ rotateX: springRotateX, rotateY: springRotateY, transformPerspective: 1000 }}
            className={className}
        >
            {children}
        </motion.div>
    )
}

// Fancy tab button
const TabButton = ({
    active,
    onClick,
    icon: Icon,
    label,
    emoji,
    color
}: {
    active: boolean
    onClick: () => void
    icon: React.ComponentType<{ className?: string }>
    label: string
    emoji?: string
    color?: string
}) => (
    <motion.button
        onClick={onClick}
        className={cn(
            "relative flex items-center gap-2 px-5 py-3 rounded-xl font-semibold text-sm transition-all overflow-hidden",
            active
                ? `bg-gradient-to-r ${color || 'from-zinc-500 to-gray-500'} text-white shadow-lg`
                : "bg-white/80 text-zinc-600 hover:bg-white border border-zinc-200/50 hover:border-zinc-300"
        )}
        whileHover={{ scale: 1.05, y: -2 }}
        whileTap={{ scale: 0.95 }}
    >
        {emoji && <span className="text-lg">{emoji}</span>}
        <Icon className="w-4 h-4" />
        {label}
        {active && (
            <motion.div
                className="absolute inset-0 bg-white/20"
                initial={{ x: '-100%' }}
                animate={{ x: '200%' }}
                transition={{ duration: 1.5, repeat: Infinity, repeatDelay: 2 }}
            />
        )}
    </motion.button>
)

// Matrix Demo - Super interactive checklist
const MatrixDemo = () => {
    const [tasks, setTasks] = useState(DEMO_TASKS)
    const [confettiPos, setConfettiPos] = useState<{ x: number; y: number } | null>(null)
    const [celebrating, setCelebrating] = useState(false)

    const toggleTask = (id: number, e: React.MouseEvent) => {
        const task = tasks.find(t => t.id === id)
        if (task && !task.done) {
            setConfettiPos({ x: e.clientX, y: e.clientY })
            setCelebrating(true)
            setTimeout(() => {
                setConfettiPos(null)
                setCelebrating(false)
            }, 1000)
        }
        setTasks(prev => prev.map(t =>
            t.id === id ? { ...t, done: !t.done } : t
        ))
    }

    const completedCount = tasks.filter(t => t.done).length
    const allDone = completedCount === tasks.length

    return (
        <div className="space-y-5">
            {confettiPos && <Confetti x={confettiPos.x} y={confettiPos.y} />}

            {/* Progress bar with celebration */}
            <div className="relative">
                <div className="flex items-center gap-4">
                    <div className="flex-1 h-3 bg-zinc-100 rounded-full overflow-hidden shadow-inner">
                        <motion.div
                            className="h-full bg-gradient-to-r from-zinc-400 via-gray-500 to-red-500 rounded-full relative"
                            initial={{ width: '25%' }}
                            animate={{ width: `${(completedCount / tasks.length) * 100}%` }}
                            transition={{ duration: 0.5, ease: "easeOut" }}
                        >
                            {/* Shimmer */}
                            <motion.div
                                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent"
                                animate={{ x: ['-100%', '200%'] }}
                                transition={{ duration: 2, repeat: Infinity, repeatDelay: 1 }}
                            />
                        </motion.div>
                    </div>
                    <motion.span
                        className="text-sm font-bold text-zinc-600 min-w-[60px]"
                        animate={celebrating ? { scale: [1, 1.3, 1] } : {}}
                    >
                        {completedCount}/{tasks.length} ✨
                    </motion.span>
                </div>

                {allDone && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="absolute -top-8 left-1/2 -translate-x-1/2 flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-full text-sm font-bold shadow-lg"
                    >
                        <Trophy className="w-4 h-4" /> All tasks complete!
                    </motion.div>
                )}
            </div>

            {/* Task list */}
            <div className="space-y-3">
                {tasks.map((task, i) => (
                    <motion.div
                        key={task.id}
                        className={cn(
                            "group relative flex items-center gap-4 p-5 rounded-2xl border-2 transition-all cursor-pointer overflow-hidden",
                            task.done
                                ? "bg-gradient-to-r from-emerald-50 to-green-50 border-emerald-300"
                                : "bg-white border-zinc-200 hover:border-zinc-400 hover:shadow-lg hover:shadow-zinc-100"
                        )}
                        onClick={(e) => toggleTask(task.id, e)}
                        initial={{ opacity: 0, x: -30 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        whileHover={{ scale: 1.02, x: 5 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        {/* Hover glow */}
                        <motion.div
                            className="absolute inset-0 bg-gradient-to-r from-zinc-400/10 to-gray-400/10 opacity-0 group-hover:opacity-100 transition-opacity"
                        />

                        {/* Checkbox */}
                        <motion.div
                            className={cn(
                                "relative w-8 h-8 rounded-xl flex items-center justify-center transition-all z-10",
                                task.done
                                    ? "bg-gradient-to-br from-emerald-400 to-emerald-600 shadow-lg shadow-emerald-200"
                                    : "border-2 border-zinc-300 group-hover:border-zinc-400 bg-white"
                            )}
                            whileTap={{ scale: 0.7, rotate: 15 }}
                        >
                            <AnimatePresence mode="wait">
                                {task.done ? (
                                    <motion.div
                                        key="check"
                                        initial={{ scale: 0, rotate: -180 }}
                                        animate={{ scale: 1, rotate: 0 }}
                                        exit={{ scale: 0 }}
                                        transition={{ type: "spring", stiffness: 500 }}
                                    >
                                        <Check className="w-5 h-5 text-white" strokeWidth={3} />
                                    </motion.div>
                                ) : (
                                    <motion.div
                                        key="empty"
                                        className="w-3 h-3 rounded-full bg-zinc-200 group-hover:bg-zinc-300"
                                    />
                                )}
                            </AnimatePresence>
                            <StarBurst show={task.done && celebrating} />
                        </motion.div>

                        {/* Emoji */}
                        <motion.span
                            className="text-2xl z-10"
                            animate={task.done ? { rotate: [0, 20, -20, 0] } : {}}
                            transition={{ duration: 0.5 }}
                        >
                            {task.emoji}
                        </motion.span>

                        {/* Text */}
                        <span className={cn(
                            "flex-1 font-medium z-10 transition-all",
                            task.done ? "line-through text-emerald-700" : "text-zinc-700"
                        )}>
                            {task.text}
                        </span>

                        {/* Click hint */}
                        {!task.done && (
                            <motion.div
                                className="flex items-center gap-1 text-xs text-zinc-500 font-medium opacity-0 group-hover:opacity-100"
                                initial={{ x: 10 }}
                                animate={{ x: 0 }}
                            >
                                Click me! <Sparkles className="w-3 h-3" />
                            </motion.div>
                        )}
                    </motion.div>
                ))}
            </div>
        </div>
    )
}

// Muse Demo - AI Content Generation
const MuseDemo = () => {
    const [contentType, setContentType] = useState<ContentType>('linkedin')
    const [isGenerating, setIsGenerating] = useState(false)
    const [content, setContent] = useState<string | null>(null)
    const [displayedText, setDisplayedText] = useState('')
    const [copied, setCopied] = useState(false)
    const [sparkles, setSparkles] = useState(false)

    const generate = () => {
        setIsGenerating(true)
        setContent(null)
        setDisplayedText('')
        setSparkles(true)
        setTimeout(() => setSparkles(false), 500)

        setTimeout(() => {
            setIsGenerating(false)
            const newContent = DEMO_GENERATED_CONTENT[contentType][0]
            setContent(newContent)

            let i = 0
            const interval = setInterval(() => {
                if (i <= newContent.length) {
                    setDisplayedText(newContent.slice(0, i))
                    i += 2
                } else {
                    clearInterval(interval)
                }
            }, 10)
        }, 1500)
    }

    const copy = async () => {
        if (content) {
            await navigator.clipboard.writeText(content)
            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
        }
    }

    const currentType = CONTENT_TYPES.find(t => t.id === contentType)

    return (
        <div className="space-y-5">
            {/* Content type pills */}
            <div className="flex flex-wrap gap-2">
                {CONTENT_TYPES.map((type) => (
                    <motion.button
                        key={type.id}
                        onClick={() => { setContentType(type.id); setContent(null); setDisplayedText('') }}
                        className={cn(
                            "flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-sm transition-all",
                            contentType === type.id
                                ? `bg-gradient-to-r ${type.color} text-white shadow-lg`
                                : "bg-white border-2 border-zinc-200 text-zinc-600 hover:border-zinc-300"
                        )}
                        whileHover={{ scale: 1.05, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <span className="text-lg">{type.icon}</span>
                        {type.label}
                    </motion.button>
                ))}
            </div>

            {/* Generate button */}
            <motion.button
                onClick={generate}
                disabled={isGenerating}
                className="relative w-full flex items-center justify-center gap-3 px-8 py-5 bg-gradient-to-r from-zinc-500 via-gray-500 to-red-500 text-white rounded-2xl font-bold text-lg shadow-xl shadow-gray-200 disabled:opacity-70 overflow-hidden"
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
            >
                {/* Shimmer */}
                <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                    animate={{ x: ['-100%', '200%'] }}
                    transition={{ duration: 2, repeat: Infinity, repeatDelay: 1 }}
                />

                {isGenerating ? (
                    <>
                        <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear" }}>
                            <RefreshCw className="w-6 h-6" />
                        </motion.div>
                        <span>✨ Generating magic...</span>
                    </>
                ) : (
                    <>
                        <Sparkles className="w-6 h-6" />
                        <span>Generate {currentType?.label} ✨</span>
                    </>
                )}

                {sparkles && <Confetti x={window.innerWidth / 2} y={window.innerHeight / 2} />}
            </motion.button>

            {/* Output */}
            <motion.div
                className="relative min-h-[180px] p-5 rounded-2xl bg-card border-2 border-border shadow-inner overflow-hidden"
                animate={content ? { borderColor: 'hsl(var(--primary))' } : {}}
            >
                {!content && !isGenerating && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-muted-foreground">
                        <motion.div
                            animate={{ y: [0, -5, 0] }}
                            transition={{ duration: 2, repeat: Infinity }}
                        >
                            <Sparkles className="w-10 h-10 mb-3 text-primary/40" />
                        </motion.div>
                        <p className="text-sm font-medium">Click generate to see the magic ✨</p>
                    </div>
                )}

                {isGenerating && (
                    <div className="space-y-3">
                        {[80, 60, 90, 40].map((w, i) => (
                            <motion.div
                                key={i}
                                className="h-4 bg-gradient-to-r from-primary/15 to-primary/5 rounded-lg"
                                initial={{ width: 0, opacity: 0.5 }}
                                animate={{ width: `${w}%`, opacity: 1 }}
                                transition={{ delay: i * 0.1, duration: 0.5 }}
                            />
                        ))}
                    </div>
                )}

                {content && (
                    <motion.pre
                        className="whitespace-pre-wrap text-sm text-zinc-700 font-sans leading-relaxed"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                    >
                        {displayedText}
                        <motion.span
                            className="inline-block w-0.5 h-4 bg-zinc-500 ml-0.5"
                            animate={{ opacity: [1, 0] }}
                            transition={{ duration: 0.5, repeat: Infinity }}
                        />
                    </motion.pre>
                )}

                {/* Copy button */}
                {content && displayedText === content && (
                    <motion.button
                        onClick={copy}
                        className="absolute top-3 right-3 flex items-center gap-2 px-3 py-2 bg-zinc-800 text-white rounded-lg text-xs font-medium shadow-lg"
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        {copied ? <><Check className="w-3 h-3" /> Copied!</> : <><Copy className="w-3 h-3" /> Copy</>}
                    </motion.button>
                )}
            </motion.div>
        </div>
    )
}

// BlackBox Demo - A/B Testing
const BlackBoxDemo = () => {
    const [activeTest, setActiveTest] = useState(0)
    const tests = [
        { name: 'CTA Button', a: { text: 'Get Started', rate: '12%' }, b: { text: 'Start Free Trial', rate: '18%' }, winner: 'B', lift: '+50%' },
        { name: 'Headline', a: { text: 'Simple Marketing', rate: '8%' }, b: { text: 'Your Marketing Engine', rate: '15%' }, winner: 'B', lift: '+87%' },
    ]
    const test = tests[activeTest]

    return (
        <div className="space-y-5">
            {/* Test selector */}
            <div className="flex gap-3">
                {tests.map((t, i) => (
                    <motion.button
                        key={i}
                        onClick={() => setActiveTest(i)}
                        className={cn(
                            "flex-1 py-3 px-4 rounded-xl font-semibold text-sm transition-all",
                            activeTest === i
                                ? "bg-gradient-to-r from-violet-500 to-purple-600 text-white shadow-lg"
                                : "bg-white border-2 border-zinc-200 text-zinc-600 hover:border-purple-300"
                        )}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        🧪 {t.name}
                    </motion.button>
                ))}
            </div>

            {/* A/B Cards */}
            <div className="grid grid-cols-2 gap-4">
                {['A', 'B'].map((variant) => {
                    const data = variant === 'A' ? test.a : test.b
                    const isWinner = test.winner === variant
                    return (
                        <motion.div
                            key={variant}
                            className={cn(
                                "relative p-5 rounded-2xl border-2 transition-all",
                                isWinner
                                    ? "bg-gradient-to-br from-emerald-50 to-green-50 border-emerald-400 shadow-lg shadow-emerald-100"
                                    : "bg-white border-zinc-200"
                            )}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: variant === 'B' ? 0.1 : 0 }}
                            whileHover={{ scale: 1.02, y: -2 }}
                        >
                            {isWinner && (
                                <motion.div
                                    className="absolute -top-3 -right-3 flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-emerald-500 to-green-500 text-white rounded-full text-xs font-bold shadow-lg"
                                    initial={{ scale: 0, rotate: -20 }}
                                    animate={{ scale: 1, rotate: 0 }}
                                    transition={{ type: "spring", delay: 0.3 }}
                                >
                                    <Trophy className="w-3 h-3" /> WINNER
                                </motion.div>
                            )}

                            <div className="text-sm font-bold text-zinc-400 mb-2">Variant {variant}</div>
                            <div className="font-bold text-zinc-800 mb-3">"{data.text}"</div>
                            <div className={cn(
                                "text-3xl font-black",
                                isWinner ? "text-emerald-600" : "text-zinc-400"
                            )}>
                                {data.rate}
                            </div>
                            <div className="text-xs text-zinc-500 mt-1">conversion rate</div>
                        </motion.div>
                    )
                })}
            </div>

            {/* Result */}
            <motion.div
                className="flex items-center justify-center gap-3 p-4 bg-gradient-to-r from-zinc-50 to-gray-50 rounded-xl border border-zinc-200"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
            >
                <Flame className="w-5 h-5 text-gray-500" />
                <span className="font-bold text-zinc-700">
                    Variant B wins with <span className="text-emerald-600">{test.lift}</span> lift!
                </span>
                <Rocket className="w-5 h-5 text-gray-500" />
            </motion.div>
        </div>
    )
}

// Main Playground Component
export const InteractivePlayground = () => {
    const [activeTab, setActiveTab] = useState<PlaygroundTab>('matrix')
    const [hasInteracted, setHasInteracted] = useState(false)

    return (
        <section id="demo" className="relative py-24 overflow-hidden bg-background">
            <div className="max-w-5xl mx-auto px-6">
                {/* Header */}
                <motion.div
                    className="text-center mb-12"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                >
                    <motion.div
                        className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/20 rounded-full text-sm font-semibold text-primary mb-6"
                        whileHover={{ scale: 1.05 }}
                    >
                        <Zap className="w-4 h-4" />
                        See It In Action
                    </motion.div>

                    <h2 className="font-serif text-4xl md:text-6xl font-medium text-foreground mb-4">
                        Don't Trust Words.{" "}
                        <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/80 italic">
                            Trust Code.
                        </span>
                    </h2>
                    <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                        Click below. Generate a strategy. See the marketing plan build itself.
                    </p>
                </motion.div>

                {/* Interactive hint */}
                <AnimatePresence>
                    {!hasInteracted && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="flex justify-center mb-6"
                        >
                            <motion.div
                                className="flex items-center gap-2 px-5 py-3 bg-zinc-800 text-white rounded-full text-sm font-medium shadow-xl"
                                animate={{ y: [0, -5, 0] }}
                                transition={{ duration: 1.5, repeat: Infinity }}
                            >
                                <Sparkles className="w-4 h-4 text-zinc-400" />
                                Try it — it's fully interactive!
                            </motion.div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* 3D Browser Frame */}
                <TiltCard className="relative">
                    <motion.div
                        className="bg-white rounded-3xl shadow-2xl shadow-zinc-200 border border-zinc-200 overflow-hidden"
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                    >
                        {/* Browser header */}
                        <div className="flex items-center justify-between px-5 py-4 bg-gradient-to-r from-zinc-50 to-zinc-100 border-b border-zinc-200">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-red-400" />
                                <div className="w-3 h-3 rounded-full bg-zinc-400" />
                                <div className="w-3 h-3 rounded-full bg-emerald-400" />
                            </div>
                            <div className="flex items-center gap-2 px-4 py-1.5 bg-white rounded-lg border border-zinc-200 text-sm text-zinc-500">
                                <div className="w-4 h-4 rounded bg-gradient-to-br from-zinc-500 to-gray-500 flex items-center justify-center text-white text-[8px] font-bold">R</div>
                                app.raptorflow.com
                            </div>
                            <div className="w-20" />
                        </div>

                        {/* Tabs */}
                        <div className="flex items-center gap-3 px-6 py-4 bg-zinc-50/50 border-b border-zinc-100">
                            <TabButton
                                active={activeTab === 'matrix'}
                                onClick={() => { setActiveTab('matrix'); setHasInteracted(true) }}
                                icon={Target}
                                label="Matrix"
                                emoji="📋"
                                color="from-zinc-500 to-gray-500"
                            />
                            <TabButton
                                active={activeTab === 'muse'}
                                onClick={() => { setActiveTab('muse'); setHasInteracted(true) }}
                                icon={Sparkles}
                                label="Muse AI"
                                emoji="✨"
                                color="from-violet-500 to-purple-500"
                            />
                            <TabButton
                                active={activeTab === 'blackbox'}
                                onClick={() => { setActiveTab('blackbox'); setHasInteracted(true) }}
                                icon={BarChart3}
                                label="Black Box"
                                emoji="🧪"
                                color="from-emerald-500 to-teal-500"
                            />
                        </div>

                        {/* Content */}
                        <div className="p-6 min-h-[400px]">
                            <AnimatePresence mode="wait">
                                {activeTab === 'matrix' && (
                                    <motion.div
                                        key="matrix"
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: 20 }}
                                    >
                                        <MatrixDemo />
                                    </motion.div>
                                )}
                                {activeTab === 'muse' && (
                                    <motion.div
                                        key="muse"
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: 20 }}
                                    >
                                        <MuseDemo />
                                    </motion.div>
                                )}
                                {activeTab === 'blackbox' && (
                                    <motion.div
                                        key="blackbox"
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: 20 }}
                                    >
                                        <BlackBoxDemo />
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </motion.div>
                </TiltCard>

                {/* CTA */}
                <motion.div
                    className="flex justify-center mt-10"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                >
                    <Link
                        to="/signup"
                        className="group inline-flex items-center gap-3 px-10 py-5 bg-gradient-to-r from-zinc-800 to-zinc-900 text-white rounded-2xl font-bold text-xl shadow-2xl shadow-zinc-400/30 hover:shadow-zinc-500/40 transition-all hover:scale-[1.02]"
                    >
                        Build My Marketing System
                        <motion.span
                            animate={{ x: [0, 5, 0] }}
                            transition={{ duration: 1.5, repeat: Infinity }}
                        >
                            <ArrowRight className="w-6 h-6" />
                        </motion.span>
                    </Link>
                </motion.div>
            </div>
        </section>
    )
}

