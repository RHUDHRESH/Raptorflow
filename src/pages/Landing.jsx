import { Link } from 'react-router-dom'
import {
  Sparkles,
  Target,
  Shield,
  ArrowRight,
  CheckCircle2,
  Clock3,
  BookOpen,
  Map,
  ClipboardList,
  Mail,
  Lock
} from 'lucide-react'
import { motion } from 'framer-motion'

const sectionFade = {
  initial: { opacity: 0, y: 16 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.25 },
  transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] },
}

export default function Landing() {
  return (
    <div className="min-h-screen bg-cream text-ink">
      {/* Top bar */}
          <header className="sticky top-0 z-20 border-b border-black/5 bg-white/90 backdrop-blur">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 md:px-6">
              <Link to="/landing" className="flex items-center gap-2">
                <span className="text-lg font-serif font-bold tracking-tight">RaptorFlow</span>
                <span className="text-micro text-gray-400">Editorial System</span>
              </Link>
              <div className="flex items-center gap-2">
                <Link to="/login" className="btn-ghost text-black">Log in</Link>
                <Link to="/register" className="btn-primary">Begin</Link>
              </div>
            </div>
          </header>

      <main className="px-4 md:px-6">
        {/* Hero */}
        <section className="relative mx-auto mt-10 max-w-6xl overflow-hidden border border-black/10 bg-white px-6 py-12 md:mt-16 md:px-10 md:py-16">
          <div className="floating-orb left-8 top-10 h-40 w-40 bg-gray-200" />
          <div className="floating-orb right-10 bottom-6 h-48 w-48 bg-gray-300" />
          <div className="relative z-10 space-y-8">
            <div className="flex items-center gap-3">
              <span className="badge-primary">Runway Dispatch</span>
              <span className="text-micro text-gray-400">Monochrome. Serious. Calm.</span>
            </div>
            <h1 className="text-hero leading-tight text-black">
              Marketing clarity in an afternoon.
            </h1>
            <p className="text-body max-w-2xl text-gray-700">
              RaptorFlow is a marketing command center. Define cohorts, plot moves, and leave with a weekly rhythm you can actually finish. No templates. No guru theatrics. Just a system.
            </p>
            <div className="flex flex-wrap items-center gap-3">
              <Link to="/register" className="btn-primary">
                Begin ritual
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link to="/strategy/wizard" className="btn-secondary">
                Preview the atelier
              </Link>
              <span className="text-micro text-gray-500">5–10 min to see your posture.</span>
            </div>
            <div className="grid gap-4 border-t border-black/5 pt-6 md:grid-cols-3">
              {[
                { label: 'Cohorts defined', value: '3–7', note: 'Real buyers, not personas' },
                { label: 'Weekly moves', value: '1–3', note: 'Finishable, time-boxed' },
                { label: 'Tone leaks', value: '0', note: 'Sentinel watches for drift' },
              ].map((item) => (
                <div key={item.label} className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full border border-black/10 bg-cream text-sm font-mono">
                    {item.value}
                  </div>
                  <div>
                    <p className="text-label">{item.label}</p>
                    <p className="text-caption">{item.note}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* System spread */}
        <motion.section
          className="mx-auto mt-16 max-w-6xl space-y-10"
          {...sectionFade}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-micro text-gray-500">System</p>
              <h2 className="text-heading">Your marketing atelier.</h2>
            </div>
            <Link to="/today" className="btn-ghost gap-2">
              See the daily view
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
          <div className="grid gap-6 md:grid-cols-3">
            {[
              {
                title: 'Cohort atelier',
                icon: Target,
                copy: 'Define rare cohorts with microproofs, objections, and language your buyers actually use.',
                detail: 'Built once, reused everywhere.',
              },
              {
                title: 'Move board',
                icon: Shield,
                copy: 'Run 1–3 lines of operation with posture-aware pacing. Offensive when the market is hot, defensive when you’re protecting altitude.',
                detail: 'Progress bars stay monochrome to reduce noise.',
              },
              {
                title: 'Sentinel',
                icon: Sparkles,
                copy: 'Lightweight watchtower that flags tone drift, fatigue, and cadence gaps—without adding another inbox.',
                detail: 'Only 5% oxblood for true alerts.',
              },
            ].map((item) => (
              <div key={item.title} className="card-hover h-full space-y-4">
                <div className="flex items-center gap-3">
                  <item.icon className="h-5 w-5 text-black" strokeWidth={1.5} />
                  <p className="text-micro text-gray-500">{item.title}</p>
                </div>
                <h3 className="text-title">{item.title}</h3>
                <p className="text-body text-gray-700">{item.copy}</p>
                <p className="text-caption text-gray-500">{item.detail}</p>
              </div>
            ))}
          </div>
        </motion.section>

        {/* Editorial principle */}
        <motion.section
          className="mx-auto mt-16 max-w-6xl space-y-8"
          {...sectionFade}
        >
          <div className="flex flex-col gap-3">
            <p className="text-micro text-gray-500">Editorial rulebook</p>
            <h2 className="text-heading">We keep the signal, cut the drama.</h2>
            <p className="text-body max-w-4xl text-gray-700">
              RaptorFlow borrows from magazines and military briefs: one serif headline, one subhead, one action. No “growth hacks”, no rainbow dashboards—only the artefacts you need to move the work.
            </p>
          </div>
          <div className="grid gap-6 md:grid-cols-3">
            {[
              { label: 'Clarity first', body: 'Every screen leads with a micro label and a single decision. We keep borders light and spacing generous.' },
              { label: 'Restraint', body: 'Monochrome palette with oxblood reserved for true alerts. Type hierarchy carries the weight, not color.' },
              { label: 'Finishable', body: 'Actions are time-boxed, status is binary, and progress bars are quiet so you can actually finish the move.' },
            ].map((item) => (
              <div key={item.label} className="card-hover h-full space-y-3">
                <p className="text-micro text-gray-500">{item.label}</p>
                <p className="text-body text-gray-700">{item.body}</p>
              </div>
            ))}
          </div>
        </motion.section>

        {/* Modules spread */}
        <motion.section
          className="mx-auto mt-16 max-w-6xl space-y-8"
          {...sectionFade}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-micro text-gray-500">Modules</p>
              <h2 className="text-heading">Everything in one runway.</h2>
            </div>
            <Link to="/muse" className="btn-ghost gap-2">
              Visit Muse
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            {[
              {
                title: 'Cohort atelier',
                icon: BookOpen,
                bullets: [
                  'Rare cohorts with pains, gains, and real objections.',
                  'Language bank captured from calls and notes.',
                  'Exports to briefs, docs, and slides in one click.'
                ],
              },
              {
                title: 'Move board',
                icon: Map,
                bullets: [
                  'Offensive, defensive, logistical, recon postures.',
                  'Limits: 3 lines of operation, 1–3 daily actions.',
                  'Progress bars stay monochrome to reduce noise.'
                ],
              },
              {
                title: 'Sentinel',
                icon: Shield,
                bullets: [
                  'Tone drift alerts with oxblood only when it matters.',
                  'Fatigue detection when cadence slips.',
                  'Surface risks without adding another inbox.'
                ],
              },
              {
                title: 'Reviews + exports',
                icon: ClipboardList,
                bullets: [
                  'Friday recap template—no slides needed.',
                  'Single-page PDF export in print-ready monochrome.',
                  'Action log for stakeholders who want receipts.'
                ],
              },
            ].map((item) => (
              <div key={item.title} className="card-hover h-full space-y-4">
                <div className="flex items-center gap-3">
                  <item.icon className="h-5 w-5 text-black" strokeWidth={1.5} />
                  <p className="text-micro text-gray-500">{item.title}</p>
                </div>
                <h3 className="text-title">{item.title}</h3>
                <ul className="space-y-2">
                  {item.bullets.map((bullet) => (
                    <li key={bullet} className="flex items-start gap-2">
                      <span className="mt-1 h-1 w-1 rounded-full bg-black" />
                      <p className="text-body text-gray-700">{bullet}</p>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </motion.section>

        {/* Editorial cadence */}
        <motion.section
          className="mx-auto mt-16 max-w-6xl overflow-hidden rounded-lg border border-black/10 bg-white"
          {...sectionFade}
          transition={{ duration: 0.5, delay: 0.1, ease: [0.4, 0, 0.2, 1] }}
        >
          <div className="grid gap-0 md:grid-cols-3">
            <div className="border-b border-black/10 p-8 md:border-b-0 md:border-r">
              <p className="text-micro text-gray-500">Monday</p>
              <h3 className="text-title mb-3">Brain dump, editorial style</h3>
              <p className="text-body text-gray-700">
                Offload the week in 10 minutes. The system labels intent, risk, and effort so you don’t.
              </p>
            </div>
            <div className="border-b border-black/10 p-8 md:border-b-0 md:border-r">
              <p className="text-micro text-gray-500">Mid-week</p>
              <h3 className="text-title mb-3">Moves into daily actions</h3>
              <p className="text-body text-gray-700">
                Three finishable actions per day. Each tied back to a cohort and a line of operation.
              </p>
            </div>
            <div className="p-8">
              <p className="text-micro text-gray-500">Friday</p>
              <h3 className="text-title mb-3">Recap without theatrics</h3>
              <p className="text-body text-gray-700">
                A one-page recap with signals, wins, and next moves. Exportable, monochrome, board-ready.
              </p>
            </div>
          </div>
        </motion.section>

        {/* Operating rhythm timeline */}
        <motion.section
          className="mx-auto mt-16 max-w-6xl space-y-8"
          {...sectionFade}
        >
          <div className="flex flex-col gap-2">
            <p className="text-micro text-gray-500">Timeline</p>
            <h2 className="text-heading">Seven days of calm execution.</h2>
          </div>
          <div className="grid gap-3">
            {[
              { day: 'Day 1', label: 'Intake', desc: 'Brain dump and inbox zero for ideas. We tag posture and urgency automatically.' },
              { day: 'Day 2', label: 'Cohort refresh', desc: 'Update microproofs, objections, and language from the week’s calls.' },
              { day: 'Day 3', label: 'Moves', desc: 'Lock 1–3 moves. Each gets a finish line and an owner.' },
              { day: 'Day 4', label: 'Daily actions', desc: 'Bite-sized tasks with time boxes. Ship, log, move on.' },
              { day: 'Day 5', label: 'Sentinel review', desc: 'Resolve tone leaks, cadence gaps, and fatigue flags.' },
              { day: 'Day 6', label: 'Recap', desc: 'One-page summary. Exportable. Board-ready. No slides.' },
              { day: 'Day 7', label: 'Reset', desc: 'Carry only what matters into the next sprint.' },
            ].map((item, idx) => (
              <div
                key={item.day}
                className="flex items-start gap-4 border border-black/5 bg-white px-4 py-4 md:px-6"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-full border border-black/10 bg-cream text-micro text-black">
                  {String(idx + 1).padStart(2, '0')}
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <p className="text-label">{item.day}</p>
                    <span className="text-caption text-gray-500">{item.label}</span>
                  </div>
                  <p className="text-body text-gray-700">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.section>

        {/* Deliverables */}
        <motion.section
          className="mx-auto mt-16 max-w-6xl space-y-8"
          {...sectionFade}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-micro text-gray-500">Deliverables</p>
              <h2 className="text-heading">What leaves the room.</h2>
            </div>
            <Link to="/strategy/wizard" className="btn-ghost gap-2">
              Generate a brief
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
          <div className="grid gap-6 md:grid-cols-3">
            {[
              { title: 'Runway brief', body: 'Single page. Cohorts, objective, posture, and three moves. Made to send, not to present.' },
              { title: 'Cadence log', body: 'Daily actions with timestamps and outcomes. Receipts without the bloat.' },
              { title: 'Signals board', body: 'Tone leaks, fatigue, risks, and callouts. Oxblood only when action is required.' },
            ].map((item) => (
              <div key={item.title} className="card-hover h-full space-y-3">
                <p className="text-micro text-gray-500">{item.title}</p>
                <p className="text-body text-gray-700">{item.body}</p>
                <div className="flex items-center gap-2 text-caption text-gray-500">
                  <CheckCircle2 className="h-3.5 w-3.5 text-black" strokeWidth={1.5} />
                  Export as PDF or copy to clipboard.
                </div>
              </div>
            ))}
          </div>
        </motion.section>

        {/* Proof and support */}
        <motion.section
          className="mx-auto mt-16 max-w-6xl space-y-10"
          {...sectionFade}
        >
          <div className="grid gap-6 md:grid-cols-3">
            <div className="card-hover h-full space-y-4">
              <p className="text-micro text-gray-500">Signals</p>
              <h3 className="text-title">Quiet dashboards.</h3>
              <p className="text-body text-gray-700">
                We keep charts minimal: posture mix, cadence streaks, and alert count. No vanity metrics, no rainbow gradients.
              </p>
            </div>
            <div className="card-hover h-full space-y-4">
              <p className="text-micro text-gray-500">Support</p>
              <h3 className="text-title">Humans on standby.</h3>
              <div className="space-y-2 text-body text-gray-700">
                <p className="flex items-center gap-2">
                  <Mail className="h-4 w-4 text-black" strokeWidth={1.5} />
                  support@raptorflow.in
                </p>
                <p className="text-caption text-gray-500">Response inside business hours. No bots.</p>
              </div>
            </div>
            <div className="card-hover h-full space-y-4">
              <p className="text-micro text-gray-500">Trust</p>
              <h3 className="text-title">Privacy first.</h3>
              <p className="text-body text-gray-700">
                We store your data in Supabase. Exports are yours. No public feeds, no surprise sharing.
              </p>
              <div className="flex items-center gap-2 text-caption text-gray-500">
                <Lock className="h-4 w-4 text-black" strokeWidth={1.5} />
                Minimal scopes. No extra trackers.
              </div>
            </div>
          </div>
        </motion.section>

        {/* FAQ */}
        <motion.section
          className="mx-auto mt-16 max-w-6xl space-y-6"
          {...sectionFade}
        >
          <div>
            <p className="text-micro text-gray-500">FAQ</p>
            <h2 className="text-heading">Straight answers.</h2>
          </div>
          <div className="grid gap-4">
            {[
              {
                q: 'Is this another content calendar?',
                a: 'No. We start with cohorts and postures, then map moves to daily actions. The calendar is an output, not the product.',
              },
              {
                q: 'How long to get value?',
                a: 'Most teams see clarity after the first sprint (one week). The intake takes under an hour, including cohorts.',
              },
              {
                q: 'Who is it for?',
                a: 'Solo founders, lean teams, and agencies who want fewer tasks with higher signal. If you hate guru theatrics, you will like this.',
              },
              {
                q: 'Do you lock me in?',
                a: 'No. Monthly billing. Export everything at any time. Your data is yours.',
              },
            ].map((item) => (
              <div key={item.q} className="card h-full border border-black/10">
                <div className="space-y-2">
                  <p className="text-label">{item.q}</p>
                  <p className="text-body text-gray-700">{item.a}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.section>

        {/* Proof strip */}
        <motion.section
          className="mx-auto mt-16 flex max-w-6xl flex-col gap-4 rounded-lg border border-black/10 bg-white px-6 py-8 md:flex-row md:items-center md:justify-between"
          {...sectionFade}
          transition={{ duration: 0.45, delay: 0.05, ease: [0.4, 0, 0.2, 1] }}
        >
          <div>
            <p className="text-micro text-gray-500">Signal</p>
            <h3 className="text-heading">Clarity beats volume.</h3>
            <p className="text-body text-gray-700 max-w-2xl">
              Teams cut posting frequency by 40% and still increase qualified responses because every move is tied to a cohort and an objective.
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full border border-black/15 bg-cream">
              <Clock3 className="h-5 w-5 text-black" strokeWidth={1.5} />
            </div>
            <div>
              <p className="text-label">6 hours saved / week</p>
              <p className="text-caption text-gray-500">Average after 2 sprints.</p>
            </div>
          </div>
        </motion.section>

        {/* Final CTA */}
        <motion.section
          className="mx-auto mt-16 mb-20 max-w-6xl overflow-hidden border border-black/10 bg-black px-8 py-12 text-white"
          {...sectionFade}
          transition={{ duration: 0.45, delay: 0.1, ease: [0.4, 0, 0.2, 1] }}
        >
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div className="space-y-3">
              <p className="text-micro text-white/60">Ready</p>
              <h3 className="text-display text-white">Step onto the runway.</h3>
              <p className="text-body text-white/80 max-w-xl">
                Run a single sprint with RaptorFlow. If you don’t leave with clearer cohorts, fewer tasks, and a calmer brain, don’t keep it.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link to="/register" className="btn-primary bg-white text-black hover:bg-gray-100">
                Start a sprint
              </Link>
              <Link
                to="/login"
                className="inline-flex items-center justify-center gap-2 px-6 py-3 text-sm font-medium uppercase tracking-wide border border-white/25 text-white transition-all duration-200 hover:bg-white/5"
              >
                Already inside? Log in
              </Link>
            </div>
          </div>
        </motion.section>
      </main>
    </div>
  )
}
