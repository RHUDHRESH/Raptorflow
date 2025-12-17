import React, { useMemo, useState, useEffect } from 'react'
import { Helmet, HelmetProvider } from 'react-helmet-async'
import { Link } from 'react-router-dom'
import { Check, X, ArrowRight, ChevronRight } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArtworkSlot } from '@/components/ArtworkSlot'
import { MarketingLayout } from '@/components/MarketingLayout'
import { cn } from '@/lib/utils'

// Custom hook for hover state
const useHover = (ref) => {
  const [isHovered, setIsHovered] = useState(false)

  const on = () => setIsHovered(true)
  const off = () => setIsHovered(false)

  useEffect(() => {
    if (!ref.current) return
    const node = ref.current

    node.addEventListener('mouseenter', on)
    node.addEventListener('mousemove', on)
    node.addEventListener('mouseleave', off)

    return () => {
      node.removeEventListener('mouseenter', on)
      node.removeEventListener('mousemove', on)
      node.removeEventListener('mouseleave', off)
    }
  }, [ref])

  return isHovered
}

const ProofPill = ({ label }: { label: string }) => {
  const ref = React.useRef(null)
  const isHovered = useHover(ref)

  return (
    <motion.span
      ref={ref}
      className="inline-flex items-center rounded-full border border-border bg-card px-3 py-1 text-[12px] text-muted-foreground overflow-hidden relative"
      whileHover={{
        borderColor: 'rgba(212, 175, 55, 0.8)',
        boxShadow: '0 0 0 1px rgba(212, 175, 55, 0.3)'
      }}
      transition={{ duration: 0.2 }}
    >
      <motion.span
        className="absolute inset-0 bg-gradient-to-r from-transparent via-primary/5 to-transparent"
        initial={{ x: '-100%' }}
        animate={{ x: isHovered ? '100%' : '-100%' }}
        transition={{ duration: 0.8, ease: 'easeInOut' }}
      />
      {label}
    </motion.span>
  )
}

const SectionHeader = ({
  eyebrow,
  title,
  description,
  right,
}: {
  eyebrow?: string
  title: string
  description?: string
  right?: React.ReactNode
}) => {
  const words = title.split(' ')

  return (
    <div className="grid gap-8 lg:grid-cols-12 lg:items-end">
      <div className="lg:col-span-7">
        {eyebrow && (
          <motion.div
            className="text-editorial-caption inline-block"
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            {eyebrow}
          </motion.div>
        )}
        <h2 className="mt-2 font-serif text-headline-lg">
          {words.map((word, i) => (
            <motion.span
              key={i}
              className="inline-block mr-2"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-20% 0px -20% 0px" }}
              transition={{
                duration: 0.5,
                delay: 0.1 + i * 0.05,
                ease: [0.16, 1, 0.3, 1]
              }}
            >
              {word}{' '}
            </motion.span>
          ))}
        </h2>
        {description && (
          <motion.p
            className="mt-3 text-body-sm text-muted-foreground max-w-[70ch]"
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            {description}
          </motion.p>
        )}
      </div>
      {right && (
        <motion.div
          className="lg:col-span-5 lg:flex lg:justify-end"
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          {right}
        </motion.div>
      )}
    </div>
  )
}

const EditorialMoveCard = ({
  index,
  title,
  subtitle,
  duration,
  daily,
  assets,
  metric,
}: {
  index: string
  title: string
  subtitle: string
  duration: string
  daily: string
  assets: string[]
  metric: string
}) => {
  const gradientClassByIndex = useMemo(() => {
    const n = Number.parseInt(index, 10)
    const safe = Number.isFinite(n) ? n : 0
    const gradients = [
      'from-amber-500/[0.10] via-transparent to-transparent',
      'from-zinc-200/[0.08] via-transparent to-transparent',
      'from-stone-200/[0.08] via-transparent to-transparent',
    ]
    return gradients[Math.abs(safe) % gradients.length]
  }, [index])

  return (
    <motion.article
      className="group relative"
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="relative overflow-hidden rounded-3xl border border-border/60 bg-background/60 shadow-[0_1px_0_rgba(255,255,255,0.04)] backdrop-blur-xl">
        <div className="absolute inset-0 pointer-events-none">
          <div className={cn("absolute -left-20 -top-20 h-72 w-72 rounded-full bg-gradient-to-br blur-3xl", gradientClassByIndex)} />
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border/80 to-transparent opacity-70" />
          <div className="absolute inset-0 opacity-[0.018] mix-blend-overlay" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\"0 0 256 256\" xmlns=\"http://www.w3.org/2000/svg\"%3E%3Cfilter id=\"noise\"%3E%3CfeTurbulence type=\"fractalNoise\" baseFrequency=\"0.85\" numOctaves=\"3\" stitchTiles=\"stitch\"/%3E%3C/filter%3E%3Crect width=\"100%25\" height=\"100%25" filter=\"url(%23noise)\"/%3E%3C/svg%3E")' }} />
        </div>

        <div className="relative p-7 md:p-8">
          <div className="flex items-start justify-between gap-6">
            <div className="min-w-0">
              <div className="flex items-center gap-3">
                <span className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-border/60 bg-background/40 font-mono text-[11px] text-muted-foreground">
                  {index}
                </span>
                <span className="font-mono text-[11px] uppercase tracking-[0.26em] text-muted-foreground">
                  {duration}
                </span>
              </div>

              <h3 className="mt-5 font-serif text-[30px] leading-[1.02] tracking-[-0.02em] text-foreground">
                {title}
              </h3>
              <p className="mt-2 max-w-[60ch] text-[13px] leading-relaxed text-muted-foreground">
                {subtitle}
              </p>
            </div>
          </div>

          <div className="mt-8 grid gap-4 md:grid-cols-12">
            <div className="md:col-span-7">
              <div className="rounded-2xl border border-border/60 bg-background/30 p-5">
                <div className="text-[11px] uppercase tracking-[0.22em] text-muted-foreground">Daily decision</div>
                <p className="mt-2 text-[14px] leading-relaxed text-foreground/85">{daily}</p>
              </div>
            </div>
            <div className="md:col-span-5">
              <div className="rounded-2xl border border-border/60 bg-muted/25 p-5">
                <div className="text-[11px] uppercase tracking-[0.22em] text-muted-foreground">Metric</div>
                <div className="mt-2 font-mono text-sm text-foreground">{metric}</div>
              </div>
            </div>
          </div>

          <div className="mt-6 rounded-3xl border border-border/60 bg-background/30 p-6">
            <div className="text-[11px] uppercase tracking-[0.22em] text-muted-foreground">Asset strip</div>
            <div className="mt-4 grid gap-2 sm:grid-cols-2">
              {assets.map((asset) => (
                <div key={asset} className="rounded-2xl border border-border/60 bg-background/40 px-4 py-3">
                  <div className="text-[13px] text-foreground/85">{asset}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </motion.article>
  )
}

const PremiumLanding = () => {
  const [activeComparisonId, setActiveComparisonId] = useState('cadence')

  const moveCards = useMemo(
    () => [
      {
        title: 'Signal Move',
        subtitle: 'Demand / attention / belief',
        duration: '7–30 days',
        daily: 'Decide what you want them to believe today—and where it lives.',
        assets: ['Message clarity sheet', 'Angle library', 'Editorial brief', 'One flagship asset'],
        metric: 'Qualified attention',
      },
      {
        title: 'Convert Move',
        subtitle: 'Pipeline / conversion / sales actions',
        duration: '7–30 days',
        daily: 'Decide what the next best action is—and remove friction.',
        assets: ['Landing page skeleton', 'Offer page', 'Email sequence', 'Sales enablement'],
        metric: 'Pipeline created',
      },
      {
        title: 'Stick Move',
        subtitle: 'Retention / referral / compounding',
        duration: '7–30 days',
        daily: 'Decide what keeps customers returning—and build the loop.',
        assets: ['Onboarding sequence', 'Churn reasons map', 'Referral prompt', 'Renewal narrative'],
        metric: 'Expansion signals',
      },
    ],
    [],
  )

  const artifacts = useMemo(
    () => [
      {
        id: 'artifact-message-clarity',
        label: 'Message clarity sheet',
        prompt:
          'Editorial worksheet on warm paper: messaging hierarchy, audience pains, proof points; ink sketch margins; subtle grain; premium magazine layout.',
      },
      {
        id: 'artifact-90-day-map',
        label: '90-day map',
        prompt:
          '90-day execution map: three parallel sprint columns with hairline rules, serif section titles, mono dates; looks like a museum placard.',
      },
      {
        id: 'artifact-3-move-briefs',
        label: '3 Move briefs',
        prompt:
          'Three-page editorial brief set: Signal / Convert / Stick, each with a duration badge, one metric, and deliverable strip; paper texture.',
      },
      {
        id: 'artifact-asset-pack',
        label: 'Example asset pack',
        prompt:
          'Minimal ad/email/post pack preview: typographic mockups, hairline dividers, antique-gold accent only on CTA; calm, premium.',
      },
      {
        id: 'artifact-tracking-panel',
        label: 'Tracking panel screenshot',
        prompt:
          'Low-contrast analytics panel: quiet sidebar, calm table density, mono metrics, sparing accent for selection; paper backdrop.',
      },
    ],
    [],
  )

  const comparisonRows = useMemo(
    () => [
      {
        id: 'cadence',
        label: 'Weekly cadence',
        without: ['Restart meetings', 'Urgent pivots', 'No map the team trusts'],
        withRaptorFlow: ['One decision/day', 'Three parallel sprints', 'A 90-day map everyone can point at'],
        detail:
          'Instead of re-deciding the week every Monday, you run a pre-committed cadence: decisions are made once, then executed calmly.',
        pills: ['Less thrash', 'Clear ownership', 'Predictable shipping'],
      },
      {
        id: 'shipping',
        label: 'What ships',
        without: ['Campaigns start then stall', '“We should post more”', 'Assets live in threads'],
        withRaptorFlow: ['Asset strip every sprint', 'Flagship piece + derivatives', 'Sales enablement stays current'],
        detail:
          'The system produces tangible artifacts each sprint, so progress is visible and transferable—not trapped in meetings or Slack.',
        pills: ['Real deliverables', 'Reusable assets', 'Clear handoffs'],
      },
      {
        id: 'metrics',
        label: 'Metrics',
        without: ['Dashboards that don’t change behavior', 'Too many KPIs', 'No feedback loop'],
        withRaptorFlow: ['One metric per Move', 'Weekly review rhythm', 'Decisions tied to numbers'],
        detail:
          'You stop measuring for comfort. Each Move has one metric that matters, reviewed on schedule, used to decide the next action.',
        pills: ['Clarity', 'Accountability', 'Signal over noise'],
      },
      {
        id: 'alignment',
        label: 'Team alignment',
        without: ['Plan lives in the founder’s head', 'Context resets weekly', 'Everyone interprets differently'],
        withRaptorFlow: ['Shared map + shared language', 'Briefs that travel', 'Fewer meetings, better decisions'],
        detail:
          'When the plan is visible and repeatable, teams stop debating what matters and start executing the same sequence of moves.',
        pills: ['Shared clarity', 'Lower cognitive load', 'Fewer resets'],
      },
      {
        id: 'tools',
        label: 'Tooling',
        without: ['Tool sprawl', 'New shiny every month', 'Work scattered across apps'],
        withRaptorFlow: ['System first, tools second', 'Templates + checklists', 'Simple stack that ships'],
        detail:
          'Tools are optional. The cadence is not. RaptorFlow gives you the system so your tooling can stay simple and consistent.',
        pills: ['Less chaos', 'More consistency', 'Easier onboarding'],
      },
    ],
    [],
  )

  const activeComparison =
    comparisonRows.find((row) => row.id === activeComparisonId) ?? comparisonRows[0]

  return (
    <HelmetProvider>
      <Helmet>
        <title>RaptorFlow | Daily decisions that stack</title>
        <meta
          name="description"
          content="RaptorFlow installs a 90-day execution system built on a 3-Move Stack—three parallel 7–30 day sprints—so your marketing stops resetting and starts compounding."
        />
      </Helmet>

      <MarketingLayout>
        {/* HERO / MASTHEAD SPREAD */}
        <section className="masthead">
          <div className="container-editorial">
            <div className="grid items-center gap-12 lg:grid-cols-12">
              <div className="lg:col-span-6">
                <div className="space-y-8">
                  <div className="space-y-2">
                    <Link to="/" className="inline-flex items-center">
                      <span className="font-serif text-2xl font-medium tracking-tight">
                        Raptor<span className="text-primary">Flow</span>
                      </span>
                    </Link>
                    <div className="text-editorial-caption">A 90-day execution system</div>
                  </div>

                  <div className="space-y-4">
                    <h1 className="text-balance font-serif text-headline-xl">
                      Daily decisions that stack—so marketing compounds.
                    </h1>
                    <p className="text-body-lg text-muted-foreground max-w-[60ch]">
                      A clear 90-day system built on a 3-Move Stack (Signal / Convert / Stick). Three parallel
                      7–30 day sprints. One decision per day. Real assets shipped.
                    </p>
                  </div>

                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                    <motion.a
                      href="#pricing"
                      className="group relative inline-flex items-center justify-center rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground overflow-hidden"
                      whileHover={{
                        boxShadow: '0 0 0 1px rgba(212, 175, 55, 0.5)'
                      }}
                      initial={{ opacity: 0, y: 10 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.5, delay: 0.2 }}
                    >
                      <span className="relative z-10 flex items-center gap-2">
                        View pricing
                        <motion.span
                          className="inline-block"
                          animate={{
                            x: [0, 4, 0],
                          }}
                          transition={{
                            duration: 1.5,
                            repeat: Infinity,
                            ease: 'easeInOut',
                          }}
                        >
                          <ArrowRight size={16} />
                        </motion.span>
                      </span>
                      <motion.span
                        className="absolute inset-0 bg-gradient-to-r from-primary/80 to-primary/60 opacity-0 group-hover:opacity-100"
                        initial={{ x: '-100%' }}
                        whileHover={{ x: '100%' }}
                        transition={{ duration: 0.8, ease: 'easeInOut' }}
                      />
                    </motion.a>
                  </div>

                  <div className="grid gap-3 sm:grid-cols-3">
                    {["No busywork", "Weekly cadence", "Artifacts shipped"].map((item) => (
                      <div key={item} className="rounded-card border border-border bg-card p-4">
                        <div className="flex items-start gap-2">
                          <Check className="mt-0.5 h-4 w-4 text-primary" />
                          <div className="text-body-sm text-foreground">{item}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="lg:col-span-6">
                <div className="rounded-card border border-border bg-card p-4 shadow-editorial-sm">
                  <ArtworkSlot
                    id="hero-artwork"
                    placement="masthead-bg"
                    prompt="Editorial hero artwork: ink sketch + premium photography collage on warm paper, calm negative space, subtle antique-gold highlight, no neon."
                    aspectRatio={4 / 5}
                    fallback={{ monogram: 'RF', grain: true, gradientClassName: 'bg-gradient-to-br from-muted to-card' }}
                    className="bg-muted"
                    alt="Editorial hero artwork placeholder"
                    file="landing_hero_editorial.jpg"
                  />
                </div>

                <div className="mt-6 grid gap-3 sm:grid-cols-2">
                  <motion.div
                    className="rounded-card border border-border bg-background/70 p-4"
                    whileHover={{
                      backgroundColor: 'rgba(255, 255, 255, 0.85)',
                      borderColor: 'rgba(212, 175, 55, 0.3)',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)'
                    }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="text-editorial-caption">For founders</div>
                    <div className="mt-2 text-body-sm text-muted-foreground">Stop resetting your plan every week.</div>
                  </motion.div>
                  <motion.div
                    className="rounded-card border border-border bg-background/70 p-4"
                    whileHover={{
                      backgroundColor: 'rgba(255, 255, 255, 0.85)',
                      borderColor: 'rgba(212, 175, 55, 0.3)',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)'
                    }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="text-editorial-caption">For teams</div>
                    <div className="mt-2 text-body-sm text-muted-foreground">One shared map. Clear ownership.</div>
                  </motion.div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* OUTCOMES */}
        <section id="outcomes" className="py-16 md:py-24">
          <div className="container-editorial">
            <SectionHeader
              eyebrow="Outcomes"
              title="What compounding execution looks like."
              description="We’re not selling vibes. We’re installing a system that changes what happens every day."
            />

            <div className="mt-10 overflow-hidden rounded-card border border-border bg-card shadow-editorial-sm">
              <div className="grid gap-4 border-b border-border bg-background/70 p-6 md:grid-cols-[240px_1fr_1fr] md:gap-6">
                <div className="text-editorial-caption">Tap a row</div>
                <div className="text-editorial-caption">Without RaptorFlow</div>
                <div className="text-editorial-caption">With RaptorFlow</div>
              </div>

              <div className="divide-y divide-border/70">
                {comparisonRows.map((row) => {
                  const isActive = row.id === activeComparisonId
                  return (
                    <button
                      key={row.id}
                      type="button"
                      onClick={() => setActiveComparisonId(row.id)}
                      className={`w-full text-left transition-editorial hover:bg-muted/30 ${isActive ? 'bg-muted/40' : ''
                        }`}
                    >
                      <div className="grid gap-4 p-6 md:grid-cols-[240px_1fr_1fr] md:gap-6">
                        <div className="space-y-2">
                          <div className="font-medium text-foreground">{row.label}</div>
                          <div className="text-body-xs text-muted-foreground">{isActive ? 'Selected' : 'Select'}</div>
                        </div>

                        <ul className="grid gap-2 text-body-sm text-muted-foreground">
                          {row.without.map((item) => (
                            <li key={item} className="flex gap-2">
                              <X className="mt-0.5 h-4 w-4 text-muted-foreground/70" />
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>

                        <ul className="grid gap-2 text-body-sm text-muted-foreground">
                          {row.withRaptorFlow.map((item) => (
                            <li key={item} className="flex gap-2">
                              <Check className="mt-0.5 h-4 w-4 text-primary" />
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>

            <div className="mt-6 rounded-card border border-border bg-card p-7">
              <div className="text-editorial-caption">What you gain</div>
              <div className="mt-2 font-serif text-headline-sm">{activeComparison.label}</div>
              <p className="mt-3 max-w-[75ch] text-body-sm text-muted-foreground">{activeComparison.detail}</p>
              <div className="mt-6 flex flex-wrap gap-2">
                {activeComparison.pills.map((pill) => (
                  <span key={pill} className="pill-editorial pill-neutral">
                    {pill}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* THE VILLAIN */}
        <section id="villain" className="py-16 md:py-24">
          <div className="container-editorial">
            <SectionHeader
              eyebrow="The villain"
              title="Guesswork is the tax you keep paying."
              description="If it doesn’t ship a decision, an asset, or a metric—it’s noise."
            />

            <div className="mt-10 grid gap-4 lg:grid-cols-12 lg:items-start">
              <div className="lg:col-span-5">
                <ArtworkSlot
                  id="villain-art"
                  placement="inline"
                  prompt="Ink sketch on paper: tangled thread labeled 'marketing', cut cleanly into three parallel tracks; hairline rules; calm editorial layout."
                  aspectRatio={4 / 3}
                  fallback={{ monogram: 'RF', grain: true, gradientClassName: 'bg-gradient-to-br from-muted to-card' }}
                  className="bg-muted"
                />
              </div>
              <div className="lg:col-span-7">
                <div className="rounded-card border border-border bg-card p-8">
                  <ul className="grid gap-3 text-body-md text-muted-foreground">
                    <li>Random posting ≠ strategy</li>
                    <li>Agency activity ≠ outcomes</li>
                    <li>Tools ≠ system</li>
                    <li>Motion ≠ momentum</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 3-MOVE STACK */}
        <section id="method" className="py-16 md:py-24">
          <div className="container-editorial">
            <SectionHeader
              eyebrow="Signature block"
              title="The 3-Move Stack"
              description="Three parallel sprints. Each is 7–30 days. Each produces assets, decisions, and one metric that matters."
              right={
                <div className="hidden md:flex items-center gap-2">
                  <ProofPill label="3 parallel tracks" />
                  <ProofPill label="7–30 day sprints" />
                  <ProofPill label="minimum 3 Moves" />
                </div>
              }
            />

            <div className="mt-10 grid gap-6 lg:grid-cols-3">
              {moveCards.map((move, idx) => (
                <EditorialMoveCard
                  key={move.title}
                  index={`0${idx + 1}`}
                  title={move.title}
                  subtitle={move.subtitle}
                  duration={move.duration}
                  daily={move.daily}
                  assets={move.assets}
                  metric={move.metric}
                />
              ))}
            </div>

          </div>
        </section>

        {/* PROOF WITHOUT TESTIMONIALS */}
        <section id="proof" className="py-16 md:py-24">
          <div className="container-editorial">
            <SectionHeader
              eyebrow="Proof"
              title="We don’t ask you to believe. We show you the work."
              description="A clean museum wall of artifacts. The deliverables reduce uncertainty faster than claims."
            />

            <div className="mt-10 grid gap-6 lg:grid-cols-12">
              {/* Museum wall: 1 large + 2 medium + 3 small */}
              <div className="lg:col-span-7 space-y-3">
                <ArtworkSlot
                  id={artifacts[1]?.id}
                  placement="inline"
                  prompt={artifacts[1]?.prompt}
                  aspectRatio={16 / 10}
                  fallback={{ monogram: 'RF', grain: true, gradientClassName: 'bg-gradient-to-br from-card to-muted' }}
                  className="bg-muted"
                />
                <div className="flex items-center justify-between gap-4">
                  <div className="text-body-sm text-foreground">{artifacts[1]?.label}</div>
                  <div className="text-editorial-caption font-mono">artifact</div>
                </div>
              </div>

              <div className="lg:col-span-5 grid gap-6">
                {[artifacts[0], artifacts[2]].map((item) => (
                  <div key={item.id} className="space-y-3">
                    <ArtworkSlot
                      id={item.id}
                      placement="inline"
                      prompt={item.prompt}
                      aspectRatio={4 / 3}
                      fallback={{ monogram: 'RF', grain: true, gradientClassName: 'bg-gradient-to-br from-card to-muted' }}
                      className="bg-muted"
                    />
                    <div className="flex items-center justify-between gap-4">
                      <div className="text-body-sm text-foreground">{item.label}</div>
                      <div className="text-editorial-caption font-mono">artifact</div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="lg:col-span-12 grid gap-6 md:grid-cols-3">
                {[artifacts[3], artifacts[4]].filter(Boolean).map((item) => (
                  <div key={item.id} className="space-y-3">
                    <ArtworkSlot
                      id={item.id}
                      placement="inline"
                      prompt={item.prompt}
                      aspectRatio={5 / 4}
                      fallback={{ monogram: 'RF', grain: true, gradientClassName: 'bg-gradient-to-br from-card to-muted' }}
                      className="bg-muted"
                    />
                    <div className="flex items-center justify-between gap-4">
                      <div className="text-body-sm text-foreground">{item.label}</div>
                      <div className="text-editorial-caption font-mono">artifact</div>
                    </div>
                  </div>
                ))}
                <div className="rounded-card border border-border bg-card p-7">
                  <div className="text-editorial-caption">Why artifacts</div>
                  <div className="mt-3 font-serif text-headline-sm">Reduce uncertainty.</div>
                  <p className="mt-3 text-body-sm text-muted-foreground">
                    The buyer brain says “show me.” So we show the work: the map, the briefs, the asset strip, and the metric.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* PLAN */}
        <section id="plan" className="py-16 md:py-24">
          <div className="container-editorial">
            <SectionHeader
              eyebrow="Plan"
              title="A plan you can hold in your head."
              description="StoryBrand-simple. Three steps. No jargon."
            />

            <div className="mt-10 grid gap-4 lg:grid-cols-3">
              {[
                { step: '01', title: 'Clarify', desc: 'message + audience' },
                { step: '02', title: 'Map', desc: 'the next 90 days' },
                { step: '03', title: 'Run', desc: '3 Moves in parallel' },
              ].map((row) => (
                <div key={row.step} className="rounded-card border border-border bg-card p-7">
                  <div className="flex items-start justify-between gap-6">
                    <div>
                      <div className="text-editorial-caption font-mono">{row.step}</div>
                      <div className="mt-2 font-serif text-headline-sm">{row.title}</div>
                      <div className="mt-2 text-body-sm text-muted-foreground">{row.desc}</div>
                    </div>
                    <div className="h-10 w-10 rounded-card border border-border bg-muted flex items-center justify-center text-muted-foreground">
                      <span className="font-mono text-xs">→</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* OBJECTION HANDLING */}
        <section id="objections" className="py-16 md:py-24">
          <div className="container-editorial">
            <SectionHeader
              eyebrow="Objections"
              title="You’re probably thinking…"
              description="We label the objection first. Then we answer it."
            />

            <div className="mt-10 grid gap-4 lg:grid-cols-3">
              {[
                {
                  q: 'You’re probably thinking this will be generic…',
                  a: 'If your 3-Move Stack feels generic, we rebuild it until it is unmistakably your business.',
                },
                {
                  q: 'It sounds like you’ve tried agencies…',
                  a: 'Agencies can ship activity. This installs a system: decisions, assets, and a single metric per Move.',
                },
                {
                  q: 'It sounds like you don’t have time…',
                  a: 'That’s the point: one decision/day. The system reduces cognitive load and stops weekly resets.',
                },
              ].map((item) => (
                <div key={item.q} className="rounded-card border border-border bg-card p-7">
                  <div className="font-medium text-foreground">{item.q}</div>
                  <p className="mt-3 text-body-sm text-muted-foreground">{item.a}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* GUARANTEE */}
        <section id="guarantee" className="py-16 md:py-24">
          <div className="container-editorial">
            <div className="rounded-card border border-border bg-card p-8 md:p-10">
              <div className="grid gap-6 lg:grid-cols-[1fr_300px] lg:items-center">
                <div>
                  <div className="text-editorial-caption">Guarantee</div>
                  <h2 className="mt-2 font-serif text-headline-lg">Specificity Guarantee</h2>
                  <p className="mt-3 text-body-sm text-muted-foreground max-w-[70ch]">
                    If your 3-Move Stack feels generic, we rebuild it until it’s unmistakably your business.
                  </p>
                </div>

                <div className="rounded-card border border-border bg-card p-7">
                  <div className="text-editorial-caption">Included artifacts</div>
                  <div className="mt-4 grid gap-2 text-body-sm text-muted-foreground">
                    <div className="flex items-center justify-between">
                      <span>3 Move briefs</span>
                      <span className="font-mono">PDF</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>90-day map</span>
                      <span className="font-mono">Canvas</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Asset strip</span>
                      <span className="font-mono">Checklist</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* PRICING */}
        <section id="pricing" className="py-16 md:py-24">
          <div className="container-editorial">
            <SectionHeader
              eyebrow="Pricing"
              title="Pricing."
              description="Pick a plan. See limits."
            />

            {(() => {
              const plans = [
                {
                  id: 'starter',
                  name: 'Starter',
                  price: '₹4,999',
                  badge: 'Minimum',
                  tagline: 'Solo founders. Clean cadence.',
                  summary: 'plan → moves → assets → checklist',
                  caps: [
                    { k: 'Campaigns', v: '1 active' },
                    { k: 'Moves', v: '20 / month' },
                    { k: 'Muse', v: '200 generations / month' },
                    { k: 'Radar', v: '3 ICPs • 3 scans/day' },
                    { k: 'Black Box', v: '8 duels / month' },
                    { k: 'Seats', v: '1' },
                  ],
                  includes: [
                    'Matrix: daily checklist + completion + basic performance',
                    'Strategy: editable, versioned, pin campaigns',
                    'Campaigns: AI-build or manual',
                    'Moves: nimble, editable, generates daily tasks',
                    'Muse: posts, scripts, landing sections, ad copy',
                    'Radar: Small + Big scans (Big → Move)',
                    'Black Box: smart-link click tracking + promote winner to Muse defaults',
                  ],
                },
                {
                  id: 'glide',
                  name: 'Glide',
                  price: '₹6,999',
                  badge: 'Most popular',
                  tagline: 'Consistent output + optimization.',
                  summary: 'more campaigns • more moves • more variants',
                  caps: [
                    { k: 'Campaigns', v: '3 active' },
                    { k: 'Moves', v: '60 / month' },
                    { k: 'Muse', v: '600 generations / month' },
                    { k: 'Radar', v: '5 ICPs • 6 scans/day' },
                    { k: 'Black Box', v: '25 duels / month' },
                    { k: 'Seats', v: '2' },
                  ],
                  includes: [
                    'Everything in Starter',
                    'Muse: multi-variant generation (3–5 options)',
                    'Black Moves presets: Hook, CTA, Headline, Proof Order duels',
                  ],
                },
                {
                  id: 'soar',
                  name: 'Soar',
                  price: '₹11,999',
                  badge: 'Team + growth',
                  tagline: 'Heavier execution loops.',
                  summary: 'brand compliance • more experiments',
                  caps: [
                    { k: 'Campaigns', v: '10 active' },
                    { k: 'Moves', v: '150 / month' },
                    { k: 'Muse', v: '1,500 generations / month' },
                    { k: 'Radar', v: '15 ICPs • 15 scans/day' },
                    { k: 'Black Box', v: '80 duels / month' },
                    { k: 'Seats', v: '5' },
                  ],
                  includes: [
                    'Everything in Glide',
                    'Muse: brand compliance mode (taboo words, claim ledger checks)',
                    'Black Box: conversion tracking option (simple lead-capture pages)',
                    'Trail (Lite): CSV import targets + sequence generator + daily send queue + outcome tracking',
                  ],
                },
                {
                  id: 'orbit',
                  name: 'Orbit',
                  price: '₹24,999',
                  badge: 'Agency',
                  tagline: 'Multi-brand operations.',
                  summary: 'templates • cross-client learnings',
                  caps: [
                    { k: 'Client workspaces', v: '10 included' },
                    { k: 'Black Box', v: '250 duels / month' },
                    { k: 'Radar', v: '50 ICPs total' },
                    { k: 'Seats', v: '10' },
                  ],
                  includes: [
                    'Everything in Soar',
                    'Templates: reusable Strategy/Campaign/Move templates',
                    'Cross-client learnings library (optional per client)',
                  ],
                },
              ]

              const [selectedId, setSelectedId] = React.useState('glide')
              const selected = plans.find((p) => p.id === selectedId) ?? plans[1]

              const planPrice = Number(String(selected.price).replace(/[^0-9]/g, ''))

              const [addonIcp, setAddonIcp] = React.useState<number>(0)
              const [addonDuels, setAddonDuels] = React.useState<number>(0)
              const [addonMuse, setAddonMuse] = React.useState<number>(0)

              const addonIcpUnit = 999
              const addonDuelsUnit = 999
              const addonMuseUnit = 999

              const addonsSubtotal = addonIcp * addonIcpUnit + addonDuels * addonDuelsUnit + addonMuse * addonMuseUnit
              const totalMonthly = planPrice + addonsSubtotal

              const clamp = (n: number, min: number, max: number) => Math.max(min, Math.min(max, n))

              return (
                <>
                  {/* TOP: full-width plan strip */}
                  <div className="mt-8 rounded-card border border-border bg-card p-5">
                    <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                      <div>
                        <div className="text-editorial-caption">Plans</div>
                        <div className="mt-2 font-serif text-headline-sm">Starter → Glide → Soar → Orbit</div>
                      </div>
                      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
                        {plans.map((p) => {
                          const isSelected = p.id === selectedId
                          return (
                            <button
                              key={p.id}
                              type="button"
                              onClick={() => setSelectedId(p.id)}
                              className={
                                "relative rounded-2xl border px-4 py-3 text-left transition-editorial " +
                                (isSelected
                                  ? "border-primary/40 bg-primary/[0.06]"
                                  : "border-border bg-background/40 hover:bg-muted/20")
                              }
                            >
                              <div className="flex items-start justify-between gap-3">
                                <div>
                                  <div className="text-editorial-caption">{p.name}</div>
                                  <div className="mt-1 font-mono text-sm text-foreground">{p.price} / mo</div>
                                </div>
                                <span className={cn('pill-editorial pill-neutral font-mono', isSelected ? 'border-primary/30 bg-primary/[0.08]' : '')}>
                                  {p.badge}
                                </span>
                              </div>
                            </button>
                          )
                        })}
                      </div>
                    </div>
                  </div>

                  {/* BOTTOM: split layout */}
                  <div className="mt-6 grid gap-6 lg:grid-cols-12 lg:items-start">
                    {/* LEFT: add-ons */}
                    <div className="lg:col-span-7 rounded-card border border-border bg-card p-6">
                      <div className="text-editorial-caption">Add-ons</div>
                      <div className="mt-2 font-serif text-headline-sm">Add capacity.</div>
                      <p className="mt-2 text-body-sm text-muted-foreground">
                        ICPs are capped at 1. Duels and generations are unlimited.
                      </p>

                      <div className="my-5 h-px bg-border/70" />

                      <div className="grid gap-3">
                        <div className="rounded-2xl border border-border bg-background/60 px-4 py-3">
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="text-body-sm text-foreground">+5 ICPs</div>
                              <div className="text-[12px] text-muted-foreground">₹999 / month</div>
                            </div>
                            <div className="flex items-center gap-2">
                              <button
                                type="button"
                                className="h-9 w-9 rounded-md border border-border bg-background text-foreground transition-editorial hover:bg-muted"
                                onClick={() => setAddonIcp((v) => clamp(v - 1, 0, 1))}
                              >
                                −
                              </button>
                              <div className="w-8 text-center font-mono text-sm text-foreground">{addonIcp}</div>
                              <button
                                type="button"
                                className="h-9 w-9 rounded-md border border-border bg-background text-foreground transition-editorial hover:bg-muted"
                                onClick={() => setAddonIcp((v) => clamp(v + 1, 0, 1))}
                              >
                                +
                              </button>
                            </div>
                          </div>
                        </div>

                        <div className="rounded-2xl border border-border bg-background/60 px-4 py-3">
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="text-body-sm text-foreground">+20 Black Box duels</div>
                              <div className="text-[12px] text-muted-foreground">₹999 / month</div>
                            </div>
                            <div className="flex items-center gap-2">
                              <button
                                type="button"
                                className="h-9 w-9 rounded-md border border-border bg-background text-foreground transition-editorial hover:bg-muted"
                                onClick={() => setAddonDuels((v) => Math.max(0, v - 1))}
                              >
                                −
                              </button>
                              <div className="w-8 text-center font-mono text-sm text-foreground">{addonDuels}</div>
                              <button
                                type="button"
                                className="h-9 w-9 rounded-md border border-border bg-background text-foreground transition-editorial hover:bg-muted"
                                onClick={() => setAddonDuels((v) => v + 1)}
                              >
                                +
                              </button>
                            </div>
                          </div>
                        </div>

                        <div className="rounded-2xl border border-border bg-background/60 px-4 py-3">
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="text-body-sm text-foreground">+500 Muse generations</div>
                              <div className="text-[12px] text-muted-foreground">₹999 / month</div>
                            </div>
                            <div className="flex items-center gap-2">
                              <button
                                type="button"
                                className="h-9 w-9 rounded-md border border-border bg-background text-foreground transition-editorial hover:bg-muted"
                                onClick={() => setAddonMuse((v) => Math.max(0, v - 1))}
                              >
                                −
                              </button>
                              <div className="w-8 text-center font-mono text-sm text-foreground">{addonMuse}</div>
                              <button
                                type="button"
                                className="h-9 w-9 rounded-md border border-border bg-background text-foreground transition-editorial hover:bg-muted"
                                onClick={() => setAddonMuse((v) => v + 1)}
                              >
                                +
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="mt-5 flex items-center justify-between rounded-2xl border border-border bg-background/60 px-4 py-3">
                        <span className="text-body-sm text-muted-foreground">Add-ons subtotal</span>
                        <span className="font-mono text-foreground">₹{addonsSubtotal.toLocaleString('en-IN')}/mo</span>
                      </div>
                    </div>

                    {/* RIGHT: billing + what you get */}
                    <div className="lg:col-span-5 rounded-card border border-border bg-card p-6">
                      <div className="text-editorial-caption">Billing suite</div>
                      <div className="mt-2 font-serif text-headline-sm">Summary</div>

                      <div className="my-5 h-px bg-border/70" />

                      <div className="rounded-2xl border border-border bg-background/60 p-4">
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <div className="text-editorial-caption">Plan</div>
                            <div className="mt-1 font-serif text-[18px] leading-tight">{selected.name}</div>
                          </div>
                          <div className="text-right">
                            <div className="font-mono text-xl text-foreground">{selected.price}</div>
                            <div className="text-[11px] text-muted-foreground">/ month</div>
                          </div>
                        </div>

                        <div className="mt-4 grid gap-2">
                          {selected.includes.map((line) => (
                            <div key={line} className="flex gap-3 text-[13px] text-muted-foreground">
                              <span className="mt-0.5 font-mono text-foreground">✓</span>
                              <span className="min-w-0">{line}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="mt-4 grid gap-2 text-[13px] text-muted-foreground">
                        <div className="flex items-center justify-between">
                          <span>Plan</span>
                          <span className="font-mono text-foreground">₹{planPrice.toLocaleString('en-IN')}/mo</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Add-ons</span>
                          <span className="font-mono text-foreground">₹{addonsSubtotal.toLocaleString('en-IN')}/mo</span>
                        </div>
                        <div className="h-px bg-border/70" />
                        <div className="flex items-center justify-between">
                          <span className="text-foreground">Total</span>
                          <span className="font-mono text-foreground">₹{totalMonthly.toLocaleString('en-IN')}/mo</span>
                        </div>
                      </div>

                      <div className="mt-5 grid gap-2">
                        <a
                          href="#pricing"
                          className="inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-editorial hover:opacity-90"
                        >
                          Continue
                        </a>
                        <div className="text-center text-[11px] text-muted-foreground">Cancel anytime.</div>
                      </div>
                    </div>
                  </div>
                </>
              )
            })()}
          </div>
        </section>

        {/* FAQ */}
        <section id="faq" className="py-16 md:py-24">
          <div className="container-editorial">
            <SectionHeader
              eyebrow="Support"
              title="FAQ."
              description="Answers to the most common questions about RaptorFlow."
            />

            <div className="mt-10 grid gap-6 md:grid-cols-2">
              {[
                {
                  q: 'Do you offer paid plans only?',
                  a: 'Yes. RaptorFlow is a paid product. If it\'s not a fit, we offer a 14-day money-back guarantee.',
                },
                {
                  q: 'Do you replace my strategy or help me execute it?',
                  a: 'We help you turn decisions into assets and execution—so you ship consistently without weekly resets.',
                },
                {
                  q: 'How do I get support?',
                  a: 'Email hello@raptorflow.com. We usually respond within 24 hours.',
                },
                {
                  q: 'Can I cancel anytime?',
                  a: 'Yes. You can cancel from your account settings. If you need help, email us.',
                },
              ].map((item) => (
                <section key={item.q} className="rounded-card border border-border bg-card p-6">
                  <h3 className="font-serif text-headline-sm text-foreground">{item.q}</h3>
                  <p className="mt-2 text-body-sm text-muted-foreground leading-relaxed">{item.a}</p>
                </section>
              ))}
            </div>

            <div className="mt-10 grid gap-6 lg:grid-cols-12 lg:items-start">
              <div className="lg:col-span-7 rounded-card border border-border bg-card p-7">
                <div className="text-editorial-caption">Trust</div>
                <div className="mt-2 font-serif text-headline-sm">What you can count on.</div>
                <div className="mt-5 grid gap-3 sm:grid-cols-2">
                  {[
                    { t: 'Cancel anytime', d: 'No long contracts. Leave when it no longer earns its keep.' },
                    { t: 'Support that replies', d: 'Email support with a human response within 24 hours.' },
                    { t: 'System over tools', d: 'Templates + cadence first. Tooling stays calm.' },
                    { t: 'Clear billing', d: 'Know what you get, what is capped, and what expands.' },
                  ].map((row) => (
                    <div key={row.t} className="rounded-2xl border border-border bg-background/60 p-4">
                      <div className="text-body-sm text-foreground">{row.t}</div>
                      <div className="mt-1 text-[12px] leading-relaxed text-muted-foreground">{row.d}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="lg:col-span-5 rounded-card border border-border bg-card p-7">
                <div className="text-editorial-caption">Still stuck?</div>
                <div className="mt-2 font-serif text-headline-sm">Talk to us.</div>
                <p className="mt-3 text-body-sm text-muted-foreground">
                  Email{' '}
                  <a className="underline" href="mailto:hello@raptorflow.com">
                    hello@raptorflow.com
                  </a>
                  .
                </p>
                <div className="mt-6 grid gap-3">
                  <Link
                    to="/start"
                    className="inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-editorial hover:opacity-90"
                  >
                    Get started
                  </Link>
                  <Link
                    to="/login"
                    className="inline-flex w-full items-center justify-center rounded-md border border-border bg-background px-4 py-2 text-sm font-medium text-foreground transition-editorial hover:bg-muted"
                  >
                    Sign in
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* FINAL CTA */}
        <section id="final" className="py-16 md:py-24">
          <div className="container-editorial">
            <div className="mb-8 h-px bg-gradient-to-r from-transparent via-border/80 to-transparent" />

            <div className="relative overflow-hidden rounded-3xl border border-border bg-card shadow-editorial-sm">
              <div className="pointer-events-none absolute inset-0">
                <div className="absolute -left-24 -top-24 h-80 w-80 rounded-full bg-primary/[0.10] blur-3xl" />
                <div className="absolute -bottom-28 -right-28 h-96 w-96 rounded-full bg-primary/[0.06] blur-3xl" />
                <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border/80 to-transparent opacity-70" />
              </div>

              <div className="relative grid gap-8 p-8 md:p-10 lg:grid-cols-12 lg:items-center">
                <div className="lg:col-span-6">
                  <div className="text-editorial-caption">Next step</div>
                  <h2 className="mt-3 font-serif text-headline-xl">
                    Install the cadence.
                    <br />
                    Ship the artifacts.
                  </h2>
                  <p className="mt-3 max-w-[65ch] text-body-sm text-muted-foreground">
                    Stop re-deciding the week. RaptorFlow gives you a calm 90-day map, three parallel Moves, and the daily
                    decisions that keep shipping.
                  </p>

                  <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:items-center">
                    <Link
                      to="/start"
                      className="inline-flex items-center justify-center rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground transition-editorial hover:opacity-90"
                    >
                      Get started
                    </Link>
                    <Link
                      to="/login"
                      className="inline-flex items-center justify-center rounded-md border border-border bg-background px-6 py-3 text-sm font-medium text-foreground transition-editorial hover:bg-muted"
                    >
                      Sign in
                    </Link>
                  </div>

                  <div className="mt-8 flex flex-wrap gap-2">
                    {['Cancel anytime', 'One decision/day', 'Assets shipped'].map((pill) => (
                      <span key={pill} className="pill-editorial pill-neutral">
                        {pill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="lg:col-span-6">
                  <div className="rounded-3xl border border-border bg-background/60 p-4">
                    <ArtworkSlot
                      id="final-cta-art"
                      placement="inline"
                      prompt="Editorial closing artwork: calm paper canvas with three parallel tracks labeled Signal / Convert / Stick; hairline dividers; subtle antique-gold highlight on one CTA; premium, quiet, not futuristic."
                      aspectRatio={16 / 12}
                      fallback={{ monogram: 'RF', grain: true, gradientClassName: 'bg-gradient-to-br from-muted to-card' }}
                      className="bg-muted"
                      alt="Closing editorial artwork placeholder"
                    />
                  </div>
                  <div className="mt-4 grid gap-3 sm:grid-cols-2">
                    <div className="rounded-2xl border border-border bg-background/60 p-4">
                      <div className="text-editorial-caption">Time to value</div>
                      <div className="mt-2 font-mono text-sm text-foreground">Day 1: a decision ships.</div>
                      <div className="mt-1 text-[12px] text-muted-foreground">You’ll see the cadence immediately.</div>
                    </div>
                    <div className="rounded-2xl border border-border bg-background/60 p-4">
                      <div className="text-editorial-caption">Support</div>
                      <div className="mt-2 font-mono text-sm text-foreground">hello@raptorflow.com</div>
                      <div className="mt-1 text-[12px] text-muted-foreground">Reply within 24 hours.</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

      </MarketingLayout>
    </HelmetProvider>
  )
}

export default PremiumLanding
