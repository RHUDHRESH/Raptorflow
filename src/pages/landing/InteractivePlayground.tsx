import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    Check,
    Sparkles,
    BarChart3,
    Target,
    ChevronRight,
    Play,
    Zap,
    TrendingUp,
    Copy,
    RefreshCw,
    MousePointerClick
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { RaptorFlowLogo } from '@/components/brand/Logo'

// ═══════════════════════════════════════════════════════════════════════════════
// INTERACTIVE PLAYGROUND - Let visitors experience RaptorFlow without signing up
// ═══════════════════════════════════════════════════════════════════════════════

type PlaygroundTab = 'matrix' | 'muse' | 'blackbox'

// Sample data for the demo
const DEMO_TASKS = [
    { id: 1, text: 'Post LinkedIn carousel about ICP pain points', done: false },
    { id: 2, text: 'Send follow-up email to webinar attendees', done: false },
    { id: 3, text: 'Review Black Box test results for CTA variants', done: false },
    { id: 4, text: 'Schedule 3 tweets for product launch', done: true },
]

const DEMO_GENERATED_CONTENT = {
    linkedin: [
        "Stop wasting hours on marketing that doesn't convert.\n\nHere's what most founders get wrong:\n→ Random posting without strategy\n→ No clear message or positioning\n→ Zero tracking of what works\n\nThe fix? A system that tells you exactly what to do today.\n\n#marketing #founders #startup",
        "The difference between founders who scale and those who stall?\n\nIt's not budget. It's not luck.\n\nIt's having a daily marketing execution system.\n\n• Clear positioning\n• Daily checklist\n• Automatic A/B testing\n\nStop guessing. Start executing.",
        "I used to spend 10+ hours/week on marketing.\n\nNow it takes 30 minutes.\n\nThe secret: I stopped trying to do everything and built a system that does 3 things well:\n\n1. Tells me what to post\n2. Creates the content\n3. Tests what works\n\nSimplicity wins."
    ],
    email: [
        "Subject: Your marketing shouldn't feel like gambling\n\nHey {{first_name}},\n\nQuick question: How many hours did you spend last week deciding what to post?\n\nIf the answer is 'too many' — you're not alone.\n\nMost founders treat marketing like a slot machine. Pull the lever, hope for the best.\n\nBut what if you had a system that told you exactly what to do each day?\n\n→ Clear tasks, not vague goals\n→ Content that writes itself\n→ Data that shows what's actually working\n\nCurious? Let me show you how.\n\nBest,\n[Your name]",
        "Subject: The 30-minute marketing day\n\nMost founders spend 2-3 hours daily on marketing.\n\nThe best ones? 30 minutes.\n\nThe difference isn't budget or talent. It's having a system.\n\nHere's what that looks like:\n• Morning: Check your 3 daily tasks\n• Execute: Content is pre-written\n• Done: Move on to actual work\n\nWant to see how it works?\n\n→ [CTA: See the system]"
    ],
    tweet: [
        "Marketing tip that saved my startup:\n\nStop asking 'what should I post?'\n\nStart asking 'what does my ICP need to hear today?'\n\nThe answer writes itself. 🧵",
        "Unpopular opinion: You don't need a marketing team.\n\nYou need a marketing SYSTEM.\n\n→ Strategy locked\n→ Content automated\n→ Tests running 24/7\n\nOne founder. Zero chaos.",
        "The founder marketing stack:\n\n❌ 10 scattered tools\n❌ 5 hours of 'content creation'\n❌ Hoping something sticks\n\n✅ 1 system\n✅ 30 min daily\n✅ Data-driven everything",
        "Hot take: Most startup marketing fails because founders are guessing.\n\nNot because they're bad at marketing.\n\nRemove the guesswork → Remove the failure.\n\nIt's that simple."
    ],
    ad: [
        "🎯 HEADLINE: Stop Guessing. Start Winning.\n\n📝 PRIMARY TEXT:\nTired of marketing that doesn't convert?\n\nRaptorFlow gives you:\n✓ Daily execution checklists\n✓ AI-powered content\n✓ Automatic A/B testing\n\nJoin 500+ founders who stopped guessing.\n\n🔘 CTA: Get Your War Plan\n📍 URL: raptorflow.com/start",
        "🎯 HEADLINE: Your Marketing War Room\n\n📝 PRIMARY TEXT:\nEvery morning, you'll know exactly what to do.\n\nNo more staring at blank screens.\nNo more hoping for traction.\n\nJust execute. Daily.\n\n🔘 CTA: Start Free Trial\n📍 URL: raptorflow.com/trial"
    ]
}

const CONTENT_TYPES = [
    { id: 'linkedin', label: 'LinkedIn', icon: '💼' },
    { id: 'email', label: 'Email', icon: '📧' },
    { id: 'tweet', label: 'Tweet', icon: '🐦' },
    { id: 'ad', label: 'Ad Copy', icon: '📢' },
] as const

type ContentType = typeof CONTENT_TYPES[number]['id']

const DEMO_AB_TESTS = [
    {
        id: 'cta-1',
        name: 'CTA Button Copy',
        variantA: { text: 'Get Started Free', clicks: 127, conversions: 23 },
        variantB: { text: 'Start Your Trial', clicks: 134, conversions: 31 },
        winner: 'B',
        lift: '+18%'
    },
    {
        id: 'headline-1',
        name: 'Hero Headline',
        variantA: { text: 'Marketing Made Simple', clicks: 89, conversions: 12 },
        variantB: { text: 'Stop Guessing, Start Executing', clicks: 112, conversions: 24 },
        winner: 'B',
        lift: '+47%'
    }
]

// Tab button component
const TabButton = ({
    active,
    onClick,
    icon: Icon,
    label,
    badge
}: {
    active: boolean
    onClick: () => void
    icon: React.ComponentType<{ className?: string }>
    label: string
    badge?: string
}) => (
    <motion.button
        onClick={onClick}
        className={cn(
            "flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm transition-all",
            active
                ? "bg-primary text-primary-foreground shadow-lg shadow-primary/25"
                : "text-muted-foreground hover:text-foreground hover:bg-muted"
        )}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
    >
        <Icon className="w-4 h-4" />
        {label}
        {badge && (
            <span className="ml-1 px-1.5 py-0.5 text-xs rounded-full bg-primary/20 text-primary">
                {badge}
            </span>
        )}
    </motion.button>
)

// Matrix Tab - Interactive checklist
const MatrixDemo = () => {
    const [tasks, setTasks] = useState(DEMO_TASKS)
    const [showConfetti, setShowConfetti] = useState(false)

    const toggleTask = (id: number) => {
        setTasks(prev => prev.map(t =>
            t.id === id ? { ...t, done: !t.done } : t
        ))
        if (!tasks.find(t => t.id === id)?.done) {
            setShowConfetti(true)
            setTimeout(() => setShowConfetti(false), 1000)
        }
    }

    const completedCount = tasks.filter(t => t.done).length

    return (
        <div className="space-y-4">
            {/* Progress bar */}
            <div className="flex items-center gap-4 mb-6">
                <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <motion.div
                        className="h-full bg-primary rounded-full"
                        initial={{ width: '25%' }}
                        animate={{ width: `${(completedCount / tasks.length) * 100}%` }}
                        transition={{ duration: 0.5, ease: "easeOut" }}
                    />
                </div>
                <span className="text-sm font-medium text-muted-foreground">
                    {completedCount}/{tasks.length} done
                </span>
            </div>

            {/* Task list */}
            <div className="space-y-2">
                {tasks.map((task, i) => (
                    <motion.div
                        key={task.id}
                        className={cn(
                            "group flex items-center gap-3 p-4 rounded-xl border transition-all cursor-pointer",
                            task.done
                                ? "bg-primary/5 border-primary/20"
                                : "bg-card border-border hover:border-primary/30 hover:shadow-md"
                        )}
                        onClick={() => toggleTask(task.id)}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        whileHover={{ x: 4 }}
                    >
                        <motion.div
                            className={cn(
                                "w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all",
                                task.done
                                    ? "bg-primary border-primary"
                                    : "border-muted-foreground/30 group-hover:border-primary"
                            )}
                            whileTap={{ scale: 0.8 }}
                        >
                            <AnimatePresence>
                                {task.done && (
                                    <motion.div
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        exit={{ scale: 0 }}
                                    >
                                        <Check className="w-4 h-4 text-primary-foreground" />
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </motion.div>
                        <span className={cn(
                            "flex-1 transition-all",
                            task.done && "line-through text-muted-foreground"
                        )}>
                            {task.text}
                        </span>
                        {!task.done && (
                            <MousePointerClick className="w-4 h-4 text-muted-foreground/50 group-hover:text-primary transition-colors" />
                        )}
                    </motion.div>
                ))}
            </div>

            {/* Confetti effect */}
            <AnimatePresence>
                {showConfetti && (
                    <div className="absolute inset-0 pointer-events-none overflow-hidden">
                        {[...Array(12)].map((_, i) => (
                            <motion.div
                                key={i}
                                className="absolute w-2 h-2 rounded-full"
                                style={{
                                    left: '50%',
                                    top: '50%',
                                    backgroundColor: ['#f59e0b', '#10b981', '#3b82f6', '#8b5cf6'][i % 4]
                                }}
                                initial={{ scale: 0, x: 0, y: 0 }}
                                animate={{
                                    scale: [0, 1, 0],
                                    x: Math.cos(i * 30 * Math.PI / 180) * (50 + Math.random() * 50),
                                    y: Math.sin(i * 30 * Math.PI / 180) * (50 + Math.random() * 50),
                                }}
                                exit={{ opacity: 0 }}
                                transition={{ duration: 0.6 }}
                            />
                        ))}
                    </div>
                )}
            </AnimatePresence>

            {/* Hint text */}
            <p className="text-xs text-muted-foreground text-center mt-4">
                Click tasks to complete them — this is your daily Matrix checklist
            </p>
        </div>
    )
}

// Muse Tab - AI content generation demo
const MuseDemo = () => {
    const [contentType, setContentType] = useState<ContentType>('linkedin')
    const [isGenerating, setIsGenerating] = useState(false)
    const [generatedContent, setGeneratedContent] = useState<string | null>(null)
    const [displayedText, setDisplayedText] = useState('')
    const [copied, setCopied] = useState(false)
    const [generationCount, setGenerationCount] = useState(0)

    const generateContent = () => {
        setIsGenerating(true)
        setGeneratedContent(null)
        setDisplayedText('')

        // Pick content from selected type, cycling through options
        const contentOptions = DEMO_GENERATED_CONTENT[contentType]
        const content = contentOptions[generationCount % contentOptions.length]
        setGenerationCount(prev => prev + 1)

        // Simulate AI typing after a delay
        setTimeout(() => {
            setIsGenerating(false)
            setGeneratedContent(content)

            // Typewriter effect
            let i = 0
            const interval = setInterval(() => {
                if (i <= content.length) {
                    setDisplayedText(content.slice(0, i))
                    i++
                } else {
                    clearInterval(interval)
                }
            }, 12)
        }, 1200)
    }

    const copyContent = async () => {
        if (generatedContent) {
            await navigator.clipboard.writeText(generatedContent)
            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
        }
    }

    // Reset when content type changes
    const handleTypeChange = (type: ContentType) => {
        setContentType(type)
        setGeneratedContent(null)
        setDisplayedText('')
        setGenerationCount(0)
    }

    return (
        <div className="space-y-4">
            {/* Content type selector */}
            <div className="flex gap-2 overflow-x-auto pb-2">
                {CONTENT_TYPES.map((type) => (
                    <motion.button
                        key={type.id}
                        onClick={() => handleTypeChange(type.id)}
                        className={cn(
                            "flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap",
                            contentType === type.id
                                ? "bg-primary/10 text-primary border border-primary/30"
                                : "text-muted-foreground hover:bg-muted border border-transparent"
                        )}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        <span>{type.icon}</span>
                        {type.label}
                    </motion.button>
                ))}
            </div>

            {/* Generate button */}
            <motion.button
                onClick={generateContent}
                disabled={isGenerating}
                className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-primary to-primary/80 text-primary-foreground rounded-xl font-medium shadow-lg shadow-primary/25 disabled:opacity-70"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
            >
                {isGenerating ? (
                    <>
                        <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        >
                            <RefreshCw className="w-5 h-5" />
                        </motion.div>
                        Generating with Muse AI...
                    </>
                ) : (
                    <>
                        <Sparkles className="w-5 h-5" />
                        {generatedContent ? 'Generate Another' : `Generate ${CONTENT_TYPES.find(t => t.id === contentType)?.label}`}
                    </>
                )}
            </motion.button>

            {/* Output area */}
            <div className="relative min-h-[200px] p-4 rounded-xl border border-border bg-muted/30">
                {!generatedContent && !isGenerating && (
                    <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">
                        <div className="text-center">
                            <Sparkles className="w-8 h-8 mx-auto mb-2 opacity-50" />
                            <p className="text-sm">Select a content type and click generate</p>
                        </div>
                    </div>
                )}

                {isGenerating && (
                    <div className="space-y-2">
                        {[...Array(4)].map((_, i) => (
                            <motion.div
                                key={i}
                                className="h-4 bg-muted rounded"
                                initial={{ width: '0%' }}
                                animate={{ width: `${60 + Math.random() * 40}%` }}
                                transition={{ duration: 0.5, delay: i * 0.1 }}
                            />
                        ))}
                    </div>
                )}

                {generatedContent && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                    >
                        <pre className="whitespace-pre-wrap text-sm text-foreground font-sans leading-relaxed">
                            {displayedText}
                            <motion.span
                                animate={{ opacity: [1, 0] }}
                                transition={{ duration: 0.5, repeat: Infinity }}
                                className="inline-block w-0.5 h-4 bg-primary ml-0.5"
                            />
                        </pre>
                    </motion.div>
                )}

                {/* Copy button */}
                {generatedContent && displayedText === generatedContent && (
                    <motion.button
                        onClick={copyContent}
                        className="absolute top-2 right-2 p-2 rounded-lg bg-card border border-border hover:border-primary/50 transition-colors"
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                    >
                        {copied ? (
                            <Check className="w-4 h-4 text-primary" />
                        ) : (
                            <Copy className="w-4 h-4 text-muted-foreground" />
                        )}
                    </motion.button>
                )}
            </div>

            <p className="text-xs text-muted-foreground text-center">
                Real Muse AI generates content from your strategy, ICP, and brand voice
            </p>
        </div>
    )
}

// BlackBox Tab - A/B testing demo
const BlackBoxDemo = () => {
    const [activeTest, setActiveTest] = useState(0)
    const test = DEMO_AB_TESTS[activeTest]

    return (
        <div className="space-y-4">
            {/* Test selector */}
            <div className="flex gap-2">
                {DEMO_AB_TESTS.map((t, i) => (
                    <motion.button
                        key={t.id}
                        onClick={() => setActiveTest(i)}
                        className={cn(
                            "flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all",
                            activeTest === i
                                ? "bg-primary/10 text-primary border border-primary/30"
                                : "text-muted-foreground hover:bg-muted"
                        )}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        {t.name}
                    </motion.button>
                ))}
            </div>

            {/* Test comparison */}
            <div className="grid grid-cols-2 gap-4">
                {/* Variant A */}
                <motion.div
                    className={cn(
                        "p-4 rounded-xl border-2 transition-all",
                        test.winner === 'A' ? "border-primary bg-primary/5" : "border-border"
                    )}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    key={`${test.id}-a`}
                >
                    <div className="flex items-center justify-between mb-3">
                        <span className="text-xs font-medium text-muted-foreground">Variant A</span>
                        {test.winner === 'A' && (
                            <span className="px-2 py-0.5 text-xs font-medium bg-primary text-primary-foreground rounded-full">
                                Winner
                            </span>
                        )}
                    </div>
                    <p className="font-medium text-foreground mb-4">"{test.variantA.text}"</p>
                    <div className="grid grid-cols-2 gap-2 text-center">
                        <div className="p-2 rounded-lg bg-muted">
                            <div className="text-lg font-bold text-foreground">{test.variantA.clicks}</div>
                            <div className="text-xs text-muted-foreground">Clicks</div>
                        </div>
                        <div className="p-2 rounded-lg bg-muted">
                            <div className="text-lg font-bold text-foreground">{test.variantA.conversions}</div>
                            <div className="text-xs text-muted-foreground">Conversions</div>
                        </div>
                    </div>
                </motion.div>

                {/* Variant B */}
                <motion.div
                    className={cn(
                        "p-4 rounded-xl border-2 transition-all",
                        test.winner === 'B' ? "border-primary bg-primary/5" : "border-border"
                    )}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    key={`${test.id}-b`}
                >
                    <div className="flex items-center justify-between mb-3">
                        <span className="text-xs font-medium text-muted-foreground">Variant B</span>
                        {test.winner === 'B' && (
                            <motion.span
                                className="px-2 py-0.5 text-xs font-medium bg-primary text-primary-foreground rounded-full"
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                transition={{ type: "spring", stiffness: 500 }}
                            >
                                Winner
                            </motion.span>
                        )}
                    </div>
                    <p className="font-medium text-foreground mb-4">"{test.variantB.text}"</p>
                    <div className="grid grid-cols-2 gap-2 text-center">
                        <div className="p-2 rounded-lg bg-muted">
                            <div className="text-lg font-bold text-foreground">{test.variantB.clicks}</div>
                            <div className="text-xs text-muted-foreground">Clicks</div>
                        </div>
                        <div className="p-2 rounded-lg bg-muted">
                            <div className="text-lg font-bold text-primary">{test.variantB.conversions}</div>
                            <div className="text-xs text-muted-foreground">Conversions</div>
                        </div>
                    </div>
                </motion.div>
            </div>

            {/* Result callout */}
            <motion.div
                className="flex items-center justify-center gap-3 p-4 rounded-xl bg-primary/10 border border-primary/20"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                key={test.id}
            >
                <TrendingUp className="w-5 h-5 text-primary" />
                <span className="font-medium text-foreground">
                    Variant {test.winner} wins with <span className="text-primary">{test.lift}</span> lift in conversions
                </span>
            </motion.div>

            <p className="text-xs text-muted-foreground text-center">
                Black Box automatically tests variants and promotes winners
            </p>
        </div>
    )
}

// Main Playground Component
export const InteractivePlayground = () => {
    const [activeTab, setActiveTab] = useState<PlaygroundTab>('matrix')
    const [hasInteracted, setHasInteracted] = useState(false)

    useEffect(() => {
        // Track first interaction
        const handleInteraction = () => {
            if (!hasInteracted) setHasInteracted(true)
        }
        window.addEventListener('click', handleInteraction, { once: true })
        return () => window.removeEventListener('click', handleInteraction)
    }, [hasInteracted])

    return (
        <motion.div
            className="relative w-full max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
        >
            {/* Browser chrome mockup */}
            <div className="rounded-2xl border border-border bg-card shadow-2xl shadow-black/10 overflow-hidden">
                {/* Title bar */}
                <div className="flex items-center gap-2 px-4 py-3 bg-muted/50 border-b border-border">
                    <div className="flex gap-1.5">
                        <div className="w-3 h-3 rounded-full bg-red-400" />
                        <div className="w-3 h-3 rounded-full bg-yellow-400" />
                        <div className="w-3 h-3 rounded-full bg-green-400" />
                    </div>
                    <div className="flex-1 flex justify-center">
                        <div className="px-4 py-1 rounded-lg bg-background/50 text-xs text-muted-foreground flex items-center gap-2">
                            <RaptorFlowLogo size="sm" showText={false} className="scale-75 origin-left" />
                            app.raptorflow.com
                        </div>
                    </div>
                </div>

                {/* Tab navigation */}
                <div className="flex items-center gap-2 p-4 border-b border-border bg-background/50">
                    <TabButton
                        active={activeTab === 'matrix'}
                        onClick={() => setActiveTab('matrix')}
                        icon={Target}
                        label="Matrix"
                        badge="4"
                    />
                    <TabButton
                        active={activeTab === 'muse'}
                        onClick={() => setActiveTab('muse')}
                        icon={Sparkles}
                        label="Muse AI"
                    />
                    <TabButton
                        active={activeTab === 'blackbox'}
                        onClick={() => setActiveTab('blackbox')}
                        icon={BarChart3}
                        label="Black Box"
                        badge="2"
                    />
                </div>

                {/* Content area */}
                <div className="relative p-6 min-h-[400px]">
                    <AnimatePresence mode="wait">
                        {activeTab === 'matrix' && (
                            <motion.div
                                key="matrix"
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 20 }}
                                transition={{ duration: 0.2 }}
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
                                transition={{ duration: 0.2 }}
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
                                transition={{ duration: 0.2 }}
                            >
                                <BlackBoxDemo />
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>

            {/* Guided tooltip for first-time users */}
            <AnimatePresence>
                {!hasInteracted && (
                    <motion.div
                        className="absolute -top-12 left-1/2 -translate-x-1/2"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                    >
                        <div className="flex items-center gap-2 px-4 py-2 bg-foreground text-background rounded-full text-sm font-medium shadow-lg">
                            <motion.div
                                animate={{ y: [0, -3, 0] }}
                                transition={{ duration: 1, repeat: Infinity }}
                            >
                                <MousePointerClick className="w-4 h-4" />
                            </motion.div>
                            Try it — it's fully interactive!
                            <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-foreground rotate-45" />
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    )
}

export default InteractivePlayground
