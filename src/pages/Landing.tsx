import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Play, Sparkles, Target, Zap, Check, ChevronRight } from 'lucide-react'

// ============================================================================
// NAVIGATION HEADER
// ============================================================================

const Header = () => {
  const navigate = useNavigate()
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <header className={`border-b border-line sticky top-0 z-50 transition-all duration-300 ${scrolled ? 'bg-canvas/95 backdrop-blur-xl shadow-sm' : 'bg-canvas/80 backdrop-blur-md'
      }`}>
      <nav className="max-w-6xl mx-auto px-6 md:px-8 lg:px-0 py-6 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3 group cursor-pointer">
          <div className="w-9 h-9 rounded-full border border-charcoal/20 flex items-center justify-center group-hover:border-aubergine transition-all duration-300 group-hover:scale-110 group-hover:rotate-12">
            <span className="font-serif italic text-sm text-aubergine">Rf</span>
          </div>
          <div className="font-serif text-2xl font-semibold tracking-tight text-aubergine italic">
            Raptor<span className="not-italic text-charcoal">flow</span>
          </div>
        </div>

        {/* Nav Links */}
        <div className="hidden md:flex items-center gap-10 text-xs uppercase tracking-[0.22em] text-charcoal/60">
          <a href="#product" className="hover:text-aubergine transition-colors relative group">
            Product
            <span className="absolute -bottom-1 left-0 w-0 h-px bg-aubergine group-hover:w-full transition-all duration-300"></span>
          </a>
          <a href="#how-it-works" className="hover:text-aubergine transition-colors relative group">
            How it works
            <span className="absolute -bottom-1 left-0 w-0 h-px bg-aubergine group-hover:w-full transition-all duration-300"></span>
          </a>
          <a href="#pillars" className="hover:text-aubergine transition-colors relative group">
            7 pillars
            <span className="absolute -bottom-1 left-0 w-0 h-px bg-aubergine group-hover:w-full transition-all duration-300"></span>
          </a>
          <a href="#pricing" className="hover:text-aubergine transition-colors relative group">
            Pricing
            <span className="absolute -bottom-1 left-0 w-0 h-px bg-aubergine group-hover:w-full transition-all duration-300"></span>
          </a>
        </div>

        {/* CTAs */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/login')}
            className="hidden sm:inline-flex text-xs uppercase tracking-[0.22em] text-charcoal/60 hover:text-aubergine transition-colors"
          >
            Log in
          </button>
          <button
            onClick={() => navigate('/start')}
            className="text-xs uppercase tracking-[0.22em] px-5 py-2.5 rounded-full bg-charcoal text-canvas hover:bg-aubergine transition-all duration-300 hover:shadow-xl hover:scale-105"
          >
            Start your plan
          </button>
        </div>
      </nav>
    </header>
  )
}

// ============================================================================
// HERO SECTION - SUBLIME & STATIONARY
// ============================================================================

const Hero = () => {
  const navigate = useNavigate()

  return (
    <section id="product" className="relative py-24 md:py-40 lg:py-48 border-b border-line bg-canvas overflow-hidden">
      {/* STATIONARY Sublime Artwork - Full Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Main Artwork - STATIONARY */}
        <div className="absolute top-0 right-0 w-full h-full md:w-[75%] md:h-[130%]">
          <img
            src="/hero-art.png"
            alt=""
            className="w-full h-full object-contain opacity-20 md:opacity-25"
            style={{
              filter: 'contrast(1.15) saturate(1.3) brightness(1.05)',
              mixBlendMode: 'multiply'
            }}
          />
        </div>

        {/* Layered Gradient Overlays */}
        <div className="absolute inset-0 bg-gradient-to-br from-canvas via-transparent to-transparent"></div>
        <div className="absolute inset-0 bg-gradient-to-t from-canvas/90 via-canvas/30 to-transparent"></div>
        <div className="absolute inset-0 bg-gradient-to-r from-canvas/60 via-transparent to-transparent"></div>

        {/* Animated Ambient Orbs */}
        <div className="absolute top-1/3 right-1/3 w-[600px] h-[600px] rounded-full bg-gradient-to-br from-aubergine/15 to-gold/15 blur-3xl animate-pulse" style={{ animationDuration: '5s' }}></div>
        <div className="absolute bottom-1/3 left-1/4 w-[700px] h-[700px] rounded-full bg-gradient-to-tr from-gold/10 to-aubergine/10 blur-3xl animate-pulse" style={{ animationDuration: '7s', animationDelay: '2.5s' }}></div>
      </div>

      {/* Subtle Texture */}
      <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'url(/pattern.png)', backgroundSize: '800px' }}></div>

      <div className="max-w-6xl mx-auto px-6 md:px-8 lg:px-0 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-16 md:gap-20 items-center">
          {/* Hero Copy */}
          <div className="md:col-span-7 space-y-8">
            <div className="flex items-center gap-3 animate-fade-in">
              <div className="w-1 h-1 rounded-full bg-gold animate-pulse"></div>
              <Sparkles className="w-4 h-4 text-gold animate-pulse" />
              <p className="text-[11px] tracking-[0.3em] uppercase text-gold font-medium">
                Founder's Editorial — Q1 2025
              </p>
            </div>

            <h1 className="font-serif text-[3.5rem] md:text-[4.5rem] lg:text-[6rem] leading-[0.9] animate-fade-in" style={{ animationDelay: '0.1s' }}>
              <span className="block mb-2">From <span className="italic text-aubergine">no real plan</span></span>
              <span className="block text-charcoal/90">to a 90-day</span>
              <span className="block text-charcoal/90">marketing war map.</span>
            </h1>

            <p className="text-lg md:text-xl text-charcoal/70 max-w-xl leading-relaxed animate-fade-in" style={{ animationDelay: '0.2s' }}>
              Raptorflow turns your business context into a structured 90-day marketing plan with
              <strong className="text-charcoal"> 3–5 focused moves</strong>, Muse-style creative briefs, and a calm control room for tracking what's actually working.
            </p>

            <div className="flex flex-col sm:flex-row gap-5 items-start sm:items-center animate-fade-in" style={{ animationDelay: '0.3s' }}>
              <button
                onClick={() => navigate('/start')}
                className="group inline-flex items-center gap-3 text-sm uppercase tracking-[0.2em] px-8 py-4 rounded-full bg-charcoal text-canvas hover:bg-aubergine transition-all duration-300 hover:shadow-2xl hover:scale-105"
              >
                Generate my 90-day outline
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              <button className="group inline-flex items-center gap-2 text-sm uppercase tracking-[0.2em] text-charcoal/70 hover:text-aubergine transition-colors">
                <div className="w-8 h-8 rounded-full border border-charcoal/20 group-hover:border-aubergine flex items-center justify-center transition-colors">
                  <Play className="w-3 h-3 fill-current" />
                </div>
                3-min walkthrough
              </button>
            </div>

            <div className="flex flex-wrap gap-8 text-xs uppercase tracking-[0.2em] text-charcoal/50 animate-fade-in" style={{ animationDelay: '0.4s' }}>
              <div className="flex items-center gap-2 group cursor-default">
                <Check className="w-4 h-4 text-gold" />
                Built for founders, not marketers
              </div>
              <div className="flex items-center gap-2 group cursor-default">
                <Check className="w-4 h-4 text-gold" />
                Organic-first, no ad spend required
              </div>
            </div>
          </div>

          {/* Hero Preview Card */}
          <div className="md:col-span-5 relative animate-fade-in" style={{ animationDelay: '0.5s' }}>
            <div className="relative bg-gradient-to-br from-white/80 to-white/60 backdrop-blur-xl border border-line/60 rounded-3xl p-10 shadow-2xl hover:shadow-3xl transition-all duration-700 group">
              {/* Floating Decorative Rings */}
              <div className="absolute -top-16 -right-10 w-40 h-40 rounded-full border-2 border-gold/30 pointer-events-none group-hover:scale-110 group-hover:rotate-12 transition-all duration-700"></div>
              <div className="absolute top-32 -right-8 w-24 h-24 rounded-full border border-aubergine/20 pointer-events-none group-hover:scale-110 group-hover:-rotate-12 transition-all duration-700"></div>

              <div className="flex items-center justify-between mb-8">
                <p className="text-[10px] uppercase tracking-[0.3em] text-charcoal/50 font-medium">
                  Preview — Your next 90 days
                </p>
                <span className="text-[10px] px-3 py-1.5 rounded-full border border-gold/30 text-gold uppercase tracking-[0.2em] bg-gold/5">
                  Live
                </span>
              </div>

              <div className="space-y-6 mb-8">
                <div>
                  <p className="text-[11px] uppercase tracking-[0.24em] text-charcoal/40 mb-2">
                    Primary goal
                  </p>
                  <p className="font-serif text-2xl text-charcoal leading-tight">
                    10 new paying customers in 90 days.
                  </p>
                </div>
                <div>
                  <p className="text-[11px] uppercase tracking-[0.24em] text-charcoal/40 mb-2">
                    Current focus
                  </p>
                  <p className="text-sm text-charcoal/70 leading-relaxed">
                    Bootstrapped B2B founders, 5–50k MRR. Outbound + founder-led content.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-5 text-xs mb-8">
                {[
                  { phase: '01', title: 'Foundation', desc: 'Clarify positioning. Ship 1 channel.' },
                  { phase: '02', title: 'Activation', desc: 'Double down on what pulls demos.' },
                  { phase: '03', title: 'Systemize', desc: 'Kill what\'s dead. Systemize follow-ups.' }
                ].map((item, i) => (
                  <div key={i} className="space-y-2 group/phase">
                    <p className="uppercase tracking-[0.2em] text-charcoal/40 text-[10px]">Phase {item.phase}</p>
                    <p className="font-serif text-base text-charcoal group-hover/phase:text-aubergine transition-colors">{item.title}</p>
                    <p className="text-[11px] text-charcoal/60 leading-relaxed">{item.desc}</p>
                  </div>
                ))}
              </div>

              <div className="pt-6 border-t border-charcoal/10 flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs text-charcoal/50">
                  <span className="w-2 h-2 rounded-full bg-gold animate-pulse"></span>
                  3 moves • 7-pillar coverage
                </div>
                <button className="group/btn inline-flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-charcoal/70 hover:text-aubergine transition-colors">
                  See full plan
                  <ChevronRight className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

// ============================================================================
// VALUE STRIP - ENHANCED
// ============================================================================

const ValueStrip = () => {
  const values = [
    {
      icon: Target,
      label: 'Clarity',
      title: "Know exactly who you're hunting.",
      description: "The 7-pillar intake locks down your audience, value prop, and proof so your 90-day plan isn't built on vibes and buzzwords."
    },
    {
      icon: Zap,
      label: 'Focus',
      title: '3-5 moves, not 37 random tactics.',
      description: 'Raptorflow cuts the noise down to a small set of moves you can realistically run, given your time, team, and channels.'
    },
    {
      icon: Sparkles,
      label: 'Control',
      title: 'A calm operations brain for marketing.',
      description: 'The Matrix view tracks moves by status, pacing, budget, and metrics so you know what to kill and what to double, without dashboards hell.'
    }
  ]

  return (
    <section className="py-20 md:py-28 border-b border-line bg-gradient-to-b from-white/80 via-canvas to-white/60 relative overflow-hidden">
      {/* Ambient Background */}
      <div className="absolute inset-0 opacity-30" style={{ backgroundImage: 'url(/pattern.png)', backgroundSize: '1000px' }}></div>

      <div className="max-w-6xl mx-auto px-6 md:px-8 lg:px-0 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 md:gap-12">
          {values.map((value, index) => {
            const Icon = value.icon
            return (
              <div
                key={index}
                className="group relative"
                style={{ animationDelay: `${index * 150}ms` }}
              >
                {/* Glow effect on hover */}
                <div className="absolute inset-0 bg-gradient-to-br from-aubergine/5 to-gold/5 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-xl"></div>

                <div className="relative border border-line/80 rounded-3xl p-8 md:p-10 bg-white/70 backdrop-blur-sm hover:bg-white/90 hover:border-aubergine/30 hover:shadow-2xl transition-all duration-500">
                  <div className="flex items-center gap-4 mb-5">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-aubergine/10 to-gold/10 flex items-center justify-center group-hover:scale-110 group-hover:rotate-6 transition-all duration-300">
                      <Icon className="w-6 h-6 text-aubergine" />
                    </div>
                    <p className="text-xs uppercase tracking-[0.24em] text-charcoal/50 font-medium">
                      {value.label}
                    </p>
                  </div>
                  <h3 className="font-serif text-2xl mb-4 group-hover:text-aubergine transition-colors leading-tight">{value.title}</h3>
                  <p className="text-sm text-charcoal/70 leading-relaxed">
                    {value.description}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

// ============================================================================

// ============================================================================
// PULL QUOTE - IMPROVED READABILITY
// ============================================================================

const PullQuote = () => {
  return (
    <section className="py-28 md:py-40 border-b border-line bg-gradient-to-br from-aubergine/8 via-canvas to-gold/8 relative overflow-hidden">
      <div className="absolute inset-0 opacity-[0.08]" style={{ backgroundImage: 'url(/pattern.png)', backgroundSize: '1200px' }}></div>

      {/* Floating orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-gradient-to-br from-gold/20 to-transparent blur-3xl"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full bg-gradient-to-tl from-aubergine/20 to-transparent blur-3xl"></div>

      <div className="max-w-5xl mx-auto px-6 md:px-8 text-center relative z-10">
        <div className="inline-block mb-8">
          <span className="text-8xl md:text-9xl font-serif text-gold/20">"</span>
        </div>
        <h2 className="font-serif text-4xl md:text-5xl lg:text-6xl leading-[1.2] mb-10 text-charcoal">
          Most founders don't need{' '}
          <span className="italic text-aubergine block md:inline">more tactics.</span>
          <br />
          They need a plan they can{' '}
          <span className="italic text-aubergine block md:inline">actually execute.</span>
        </h2>
        <div className="flex items-center justify-center gap-4">
          <div className="w-16 h-px bg-gradient-to-r from-transparent via-gold/50 to-transparent"></div>
          <p className="text-xs uppercase tracking-[0.35em] text-charcoal/50 font-medium">
            The Raptorflow Philosophy
          </p>
          <div className="w-16 h-px bg-gradient-to-r from-transparent via-gold/50 to-transparent"></div>
        </div>
      </div>
    </section>
  )
}

// ============================================================================
// HOW IT WORKS - STUNNING NUMBERS
// ============================================================================

const HowItWorks = () => {
  return (
    <section id="how-it-works" className="py-24 md:py-32 border-b border-line bg-canvas relative overflow-hidden">
      {/* Subtle background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-gradient-to-br from-gold/5 to-aubergine/5 blur-3xl"></div>

      <div className="max-w-6xl mx-auto px-6 md:px-8 lg:px-0 relative z-10">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-16 md:gap-20">
          <div className="md:w-2/5 md:sticky md:top-32">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-12 h-px bg-gold"></div>
              <p className="text-xs uppercase tracking-[0.3em] text-gold font-medium">
                How it works
              </p>
            </div>
            <h2 className="font-serif text-4xl md:text-5xl leading-tight mb-6">
              Answer a few sharp questions.<br />
              Get a 90-day war plan back.
            </h2>
            <p className="text-base text-charcoal/70 leading-relaxed">
              No jargon, no AI theatre. Just a structured conversation that turns
              what you already know into a plan you can run on Monday.
            </p>
          </div>

          <div className="md:w-3/5 space-y-16">
            {[
              { num: '01', title: 'Intake', desc: 'Plug in your answers, site, and deck. We map it across audience, value, differentiation, competition, discovery, remarkability, and proof.' },
              { num: '02', title: 'War plan', desc: 'Raptorflow drafts a 90-day plan broken into 3 phases and 3–5 moves, aligned to your goals and constraints.' },
              { num: '03', title: 'Execution briefs', desc: 'Muse-style briefs turn each move into emails, pages, scripts, and posts your team or tools can execute without re-thinking strategy.' }
            ].map((step, index) => (
              <div key={index} className="group relative">
                {/* Stunning Number Design */}
                <div className="flex items-start gap-8">
                  <div className="relative flex-shrink-0">
                    {/* Background glow */}
                    <div className="absolute inset-0 bg-gradient-to-br from-gold/20 to-aubergine/20 blur-2xl rounded-full scale-150 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

                    {/* Number container */}
                    <div className="relative w-20 h-20 rounded-2xl bg-gradient-to-br from-aubergine/10 to-gold/10 border border-gold/30 flex items-center justify-center group-hover:scale-110 group-hover:rotate-3 transition-all duration-500">
                      <span className="font-serif text-4xl font-bold bg-gradient-to-br from-aubergine to-gold bg-clip-text text-transparent">
                        {step.num}
                      </span>
                    </div>
                  </div>

                  <div className="flex-1 pt-2">
                    <h3 className="text-xl font-semibold uppercase tracking-[0.12em] mb-3 group-hover:text-aubergine transition-colors">
                      {step.title}
                    </h3>
                    <p className="text-base text-charcoal/70 leading-relaxed">
                      {step.desc}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

// ============================================================================
// 7 PILLARS - EDITORIAL WITH ARTISTIC ELEMENTS  
// ============================================================================

const SevenPillars = () => {
  return (
    <section id="pillars" className="py-32 md:py-48 border-b border-line relative overflow-hidden">
      {/* Dramatic Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-aubergine/10 via-canvas to-gold/10"></div>
      <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'url(/pattern.png)', backgroundSize: '1400px' }}></div>

      {/* Large animated orbs */}
      <div className="absolute top-1/4 right-1/3 w-[600px] h-[600px] rounded-full bg-gradient-to-br from-gold/20 to-transparent blur-3xl animate-pulse" style={{ animationDuration: '7s' }}></div>
      <div className="absolute bottom-1/4 left-1/3 w-[700px] h-[700px] rounded-full bg-gradient-to-tl from-aubergine/20 to-transparent blur-3xl animate-pulse" style={{ animationDuration: '9s', animationDelay: '3s' }}></div>

      <div className="max-w-7xl mx-auto px-6 md:px-8 lg:px-12 relative z-10">
        {/* Dramatic Header */}
        <div className="text-center max-w-4xl mx-auto mb-24">
          <div className="flex items-center justify-center gap-4 mb-8">
            <div className="w-20 h-px bg-gradient-to-r from-transparent via-gold to-transparent"></div>
            <p className="text-xs uppercase tracking-[0.4em] text-gold font-bold">
              The 7 Pillars
            </p>
            <div className="w-20 h-px bg-gradient-to-r from-transparent via-gold to-transparent"></div>
          </div>
          <h2 className="font-serif text-6xl md:text-7xl lg:text-8xl leading-[0.95] mb-8">
            The strategy spine<br />behind every plan.
          </h2>
          <p className="text-xl text-charcoal/70 leading-relaxed max-w-2xl mx-auto">
            Every campaign, move, and brief must answer to these seven.<br className="hidden md:block" />
            No more random tactics unlinked from positioning.
          </p>
        </div>

        {/* ASYMMETRIC EDITORIAL LAYOUT WITH ART */}
        <div className="relative">
          {/* Row 1: LARGE + MEDIUM */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 mb-8">
            {/* 01 - Audience - LARGE with CIRCULAR ART */}
            <div className="md:col-span-7 group relative">
              <div className="absolute -inset-6 bg-gradient-to-br from-aubergine/25 to-gold/25 rounded-3xl opacity-0 group-hover:opacity-100 transition-all duration-700 blur-3xl"></div>
              <div className="relative bg-white/70 backdrop-blur-md border-2 border-line/60 rounded-3xl p-12 hover:bg-white/90 hover:border-gold/50 hover:shadow-2xl transition-all duration-500 h-full overflow-hidden">
                {/* Artistic Element - Concentric Circles */}
                <div className="absolute -right-20 -top-20 w-64 h-64 opacity-10 group-hover:opacity-20 transition-opacity duration-500">
                  <div className="absolute inset-0 rounded-full border-4 border-aubergine"></div>
                  <div className="absolute inset-8 rounded-full border-2 border-aubergine"></div>
                  <div className="absolute inset-16 rounded-full border border-aubergine"></div>
                </div>

                <div className="mb-6">
                  <span className="text-xs uppercase tracking-[0.3em] text-gold/60 font-bold">01</span>
                </div>
                <h3 className="font-serif text-4xl md:text-5xl mb-6 group-hover:text-aubergine transition-colors leading-tight">
                  Audience
                </h3>
                <p className="text-lg text-charcoal/70 leading-relaxed">
                  Know exactly who to hunt first.
                </p>
                <div className="absolute top-8 right-8 w-3 h-3 rounded-full bg-gold/50 group-hover:scale-[2] group-hover:bg-gold transition-all duration-500"></div>
              </div>
            </div>

            {/* 02 - Value prop - MEDIUM with STAR ART */}
            <div className="md:col-span-5 group relative">
              <div className="absolute -inset-6 bg-gradient-to-br from-gold/25 to-aubergine/25 rounded-3xl opacity-0 group-hover:opacity-100 transition-all duration-700 blur-3xl"></div>
              <div className="relative bg-white/60 backdrop-blur-md border border-line/60 rounded-3xl p-10 hover:bg-white/85 hover:border-aubergine/50 hover:shadow-2xl transition-all duration-500 h-full overflow-hidden">
                {/* Artistic Element - Star Burst */}
                <div className="absolute -right-16 -bottom-16 w-48 h-48 opacity-10 group-hover:opacity-20 transition-opacity duration-500">
                  <svg viewBox="0 0 100 100" className="w-full h-full text-gold">
                    <polygon points="50,10 61,35 89,35 67,52 75,78 50,63 25,78 33,52 11,35 39,35" fill="currentColor" opacity="0.3" />
                    <polygon points="50,20 58,38 78,38 63,49 68,68 50,56 32,68 37,49 22,38 42,38" fill="currentColor" opacity="0.5" />
                  </svg>
                </div>

                <div className="mb-5">
                  <span className="text-xs uppercase tracking-[0.3em] text-aubergine/60 font-bold">02</span>
                </div>
                <h3 className="font-serif text-3xl md:text-4xl mb-5 group-hover:text-aubergine transition-colors leading-tight">
                  Value prop
                </h3>
                <p className="text-base text-charcoal/70 leading-relaxed">
                  Clarify why anyone should buy from you now.
                </p>
              </div>
            </div>
          </div>

          {/* Row 2: SMALL + MEDIUM + SMALL */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 mb-8">
            {/* 03 - Differentiation - SMALL with LAYERED SQUARES */}
            <div className="md:col-span-4 group relative">
              <div className="absolute -inset-4 bg-gradient-to-br from-aubergine/20 to-gold/20 rounded-3xl opacity-0 group-hover:opacity-100 transition-all duration-700 blur-2xl"></div>
              <div className="relative bg-white/50 backdrop-blur-sm border border-line/60 rounded-3xl p-8 hover:bg-white/80 hover:border-gold/50 hover:shadow-xl transition-all duration-500 h-full overflow-hidden">
                {/* Artistic Element - Layered Squares */}
                <div className="absolute -left-8 -bottom-8 w-32 h-32 opacity-10 group-hover:opacity-20 transition-all duration-500 group-hover:rotate-12">
                  <div className="absolute inset-0 border-4 border-aubergine rounded-lg rotate-12"></div>
                  <div className="absolute inset-4 border-2 border-aubergine rounded-lg rotate-6"></div>
                  <div className="absolute inset-8 border border-aubergine rounded-lg"></div>
                </div>

                <div className="mb-4">
                  <span className="text-xs uppercase tracking-[0.3em] text-gold/60 font-bold">03</span>
                </div>
                <h3 className="font-serif text-2xl md:text-3xl mb-4 group-hover:text-aubergine transition-colors leading-tight">
                  Differentiation
                </h3>
                <p className="text-sm text-charcoal/70 leading-relaxed">
                  What you can say they can't copy in 2 weeks.
                </p>
              </div>
            </div>

            {/* 04 - Competition - MEDIUM with TARGET CIRCLES */}
            <div className="md:col-span-4 group relative">
              <div className="absolute -inset-6 bg-gradient-to-br from-gold/25 to-aubergine/25 rounded-3xl opacity-0 group-hover:opacity-100 transition-all duration-700 blur-3xl"></div>
              <div className="relative bg-white/60 backdrop-blur-md border border-line/60 rounded-3xl p-10 hover:bg-white/85 hover:border-aubergine/50 hover:shadow-2xl transition-all duration-500 h-full overflow-hidden">
                {/* Artistic Element - Target Circles */}
                <div className="absolute -right-12 top-1/2 -translate-y-1/2 w-40 h-40 opacity-10 group-hover:opacity-20 transition-opacity duration-500">
                  <div className="absolute inset-0 rounded-full border-4 border-gold"></div>
                  <div className="absolute inset-6 rounded-full border-2 border-gold"></div>
                  <div className="absolute inset-12 rounded-full border border-gold"></div>
                  <div className="absolute inset-16 rounded-full bg-gold"></div>
                </div>

                <div className="mb-5">
                  <span className="text-xs uppercase tracking-[0.3em] text-aubergine/60 font-bold">04</span>
                </div>
                <h3 className="font-serif text-3xl md:text-4xl mb-5 group-hover:text-aubergine transition-colors leading-tight">
                  Competition
                </h3>
                <p className="text-base text-charcoal/70 leading-relaxed">
                  Where you can flank existing alternatives.
                </p>
              </div>
            </div>

            {/* 05 - Discovery - SMALL with SEARCH LENS */}
            <div className="md:col-span-4 group relative">
              <div className="absolute -inset-4 bg-gradient-to-br from-aubergine/20 to-gold/20 rounded-3xl opacity-0 group-hover:opacity-100 transition-all duration-700 blur-2xl"></div>
              <div className="relative bg-white/50 backdrop-blur-sm border border-line/60 rounded-3xl p-8 hover:bg-white/80 hover:border-gold/50 hover:shadow-xl transition-all duration-500 h-full overflow-hidden">
                {/* Artistic Element - Search Lens */}
                <div className="absolute -right-10 -top-10 w-36 h-36 opacity-10 group-hover:opacity-20 transition-all duration-500 group-hover:scale-110">
                  <div className="absolute inset-0 rounded-full border-4 border-aubergine"></div>
                  <div className="absolute bottom-2 right-2 w-12 h-1 bg-aubergine origin-top-right rotate-45"></div>
                </div>

                <div className="mb-4">
                  <span className="text-xs uppercase tracking-[0.3em] text-gold/60 font-bold">05</span>
                </div>
                <h3 className="font-serif text-2xl md:text-3xl mb-4 group-hover:text-aubergine transition-colors leading-tight">
                  Discovery
                </h3>
                <p className="text-sm text-charcoal/70 leading-relaxed">
                  How they actually find you.
                </p>
              </div>
            </div>
          </div>

          {/* Row 3: MEDIUM + LARGE */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
            {/* 06 - Remarkability - MEDIUM with SPARKLE */}
            <div className="md:col-span-5 group relative">
              <div className="absolute -inset-6 bg-gradient-to-br from-gold/25 to-aubergine/25 rounded-3xl opacity-0 group-hover:opacity-100 transition-all duration-700 blur-3xl"></div>
              <div className="relative bg-white/60 backdrop-blur-md border border-line/60 rounded-3xl p-10 hover:bg-white/85 hover:border-aubergine/50 hover:shadow-2xl transition-all duration-500 h-full overflow-hidden">
                {/* Artistic Element - Sparkle Star */}
                <div className="absolute -left-12 -top-12 w-44 h-44 opacity-10 group-hover:opacity-20 transition-all duration-500 group-hover:rotate-45">
                  <svg viewBox="0 0 100 100" className="w-full h-full text-gold">
                    <path d="M50 10 L55 45 L90 50 L55 55 L50 90 L45 55 L10 50 L45 45 Z" fill="currentColor" opacity="0.4" />
                    <path d="M50 25 L53 47 L75 50 L53 53 L50 75 L47 53 L25 50 L47 47 Z" fill="currentColor" opacity="0.6" />
                  </svg>
                </div>

                <div className="mb-5">
                  <span className="text-xs uppercase tracking-[0.3em] text-aubergine/60 font-bold">06</span>
                </div>
                <h3 className="font-serif text-3xl md:text-4xl mb-5 group-hover:text-aubergine transition-colors leading-tight">
                  Remarkability
                </h3>
                <p className="text-base text-charcoal/70 leading-relaxed">
                  The story worth talking about.
                </p>
              </div>
            </div>

            {/* 07 - Proof - LARGE with CHECKMARK SHIELD */}
            <div className="md:col-span-7 group relative">
              <div className="absolute -inset-6 bg-gradient-to-br from-aubergine/25 to-gold/25 rounded-3xl opacity-0 group-hover:opacity-100 transition-all duration-700 blur-3xl"></div>
              <div className="relative bg-white/70 backdrop-blur-md border-2 border-line/60 rounded-3xl p-12 hover:bg-white/90 hover:border-gold/50 hover:shadow-2xl transition-all duration-500 h-full overflow-hidden">
                {/* Artistic Element - Shield with Check */}
                <div className="absolute -right-16 -bottom-16 w-56 h-56 opacity-10 group-hover:opacity-20 transition-opacity duration-500">
                  <svg viewBox="0 0 100 100" className="w-full h-full text-aubergine">
                    <path d="M50 10 L80 25 L80 50 Q80 75 50 90 Q20 75 20 50 L20 25 Z" fill="currentColor" opacity="0.3" />
                    <path d="M35 50 L45 60 L65 35" stroke="currentColor" strokeWidth="4" fill="none" opacity="0.6" />
                  </svg>
                </div>

                <div className="mb-6">
                  <span className="text-xs uppercase tracking-[0.3em] text-gold/60 font-bold">07</span>
                </div>
                <h3 className="font-serif text-4xl md:text-5xl mb-6 group-hover:text-aubergine transition-colors leading-tight">
                  Proof
                </h3>
                <p className="text-lg text-charcoal/70 leading-relaxed">
                  Evidence that makes it believable.
                </p>
                <div className="absolute top-8 right-8 w-3 h-3 rounded-full bg-gold/50 group-hover:scale-[2] group-hover:bg-gold transition-all duration-500"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

// ============================================================================
// PRICING - PREMIUM
// ============================================================================

const Pricing = () => {
  const navigate = useNavigate()

  const plans = [
    {
      name: 'Ascent',
      price: '₹3,500',
      subtitle: 'For solo builders',
      description: 'One founder, one product, one focused 90-day war plan.',
      features: [
        '1 active 90-day plan',
        '3–5 moves with weekly breakdown',
        'Muse briefs for core assets',
        'Email support'
      ],
      cta: 'Start here',
      action: () => navigate('/start'),
      featured: false
    },
    {
      name: 'Glide',
      price: '₹7,000',
      subtitle: 'For small teams',
      description: 'Run and adjust multiple moves with clearer ownership and tracking.',
      features: [
        '2 active 90-day plans',
        'Moves mapped to owners',
        'Matrix insights on what to kill/double',
        'Priority support'
      ],
      cta: 'Talk to us',
      action: () => window.open('mailto:support@raptorflow.in', '_blank'),
      featured: true
    },
    {
      name: 'Soar',
      price: '₹10,000',
      subtitle: 'For operators',
      description: 'Use Raptorflow as the planning brain behind client work.',
      features: [
        'Multi-client war plans',
        'Shared templates + briefs',
        'Priority input on roadmap',
        'Dedicated account manager'
      ],
      cta: 'Join the list',
      action: () => window.open('mailto:support@raptorflow.in?subject=Soar Plan Interest', '_blank'),
      featured: false
    }
  ]

  return (
    <section id="pricing" className="py-20 md:py-28 border-b border-line bg-canvas relative overflow-hidden">
      {/* Ambient glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full bg-gradient-to-br from-aubergine/10 to-gold/10 blur-3xl"></div>

      <div className="max-w-6xl mx-auto px-6 md:px-8 lg:px-0 relative z-10">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-12 md:gap-16 mb-16">
          <div className="md:w-2/5">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-px bg-gold"></div>
              <p className="text-xs uppercase tracking-[0.3em] text-gold font-medium">
                Plans
              </p>
            </div>
            <h2 className="font-serif text-3xl md:text-4xl leading-tight mb-5">
              Start with one war plan. Upgrade when you're ready.
            </h2>
            <p className="text-base text-charcoal/70 leading-relaxed">
              See your full 90-day plan before committing. Then choose how deep
              you want Raptorflow in your operations.
            </p>
          </div>

          <div className="md:w-3/5 grid grid-cols-1 md:grid-cols-3 gap-6">
            {plans.map((plan, index) => (
              <div
                key={plan.name}
                className={`relative rounded-3xl p-8 transition-all duration-500 ${plan.featured
                  ? 'border-2 border-gold bg-white hover:shadow-2xl scale-105'
                  : 'border border-line bg-white/40 hover:bg-white/70 hover:border-aubergine/30 hover:shadow-xl'
                  }`}
              >
                {plan.featured && (
                  <span className="absolute -top-4 left-1/2 -translate-x-1/2 text-xs uppercase tracking-[0.24em] px-4 py-1.5 rounded-full bg-charcoal text-canvas font-medium whitespace-nowrap">
                    Most popular
                  </span>
                )}

                <div className="mb-6">
                  <p className="text-xs uppercase tracking-[0.24em] text-charcoal/60 mb-2 font-medium">
                    {plan.name}
                  </p>
                  <div className="flex items-baseline gap-2 mb-2">
                    <p className="font-serif text-4xl text-charcoal">{plan.price}</p>
                    <p className="text-sm text-charcoal/50">/month</p>
                  </div>
                  <h3 className="font-serif text-xl mb-3">{plan.subtitle}</h3>
                  <p className="text-sm text-charcoal/70 leading-relaxed">
                    {plan.description}
                  </p>
                </div>

                <ul className="text-sm text-charcoal/70 space-y-3 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <Check className="w-4 h-4 text-gold mt-0.5 flex-shrink-0" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={plan.action}
                  className={`w-full text-sm uppercase tracking-[0.2em] py-3 rounded-full transition-all duration-300 ${plan.featured
                    ? 'bg-charcoal text-canvas hover:bg-aubergine hover:shadow-lg'
                    : 'border border-charcoal/30 hover:border-aubergine hover:bg-aubergine hover:text-canvas'
                    }`}
                >
                  {plan.cta}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Trust indicators */}
        <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-12 pt-12 border-t border-line/50">
          <div className="flex items-center gap-3 text-sm text-charcoal/60">
            <Check className="w-5 h-5 text-gold" />
            <span>30-day money-back guarantee</span>
          </div>
          <div className="flex items-center gap-3 text-sm text-charcoal/60">
            <Check className="w-5 h-5 text-gold" />
            <span>Cancel anytime, no questions asked</span>
          </div>
          <div className="flex items-center gap-3 text-sm text-charcoal/60">
            <Check className="w-5 h-5 text-gold" />
            <span>See full plan before payment</span>
          </div>
        </div>
      </div>
    </section>
  )
}

// ============================================================================
// FOOTER
// ============================================================================

const Footer = () => {
  return (
    <footer className="py-16 text-center bg-canvas border-t border-line">
      <div className="max-w-6xl mx-auto px-6 md:px-8 lg:px-0">
        <p className="font-serif italic text-xl mb-3 text-charcoal/70">
          "Good marketing is just disciplined attention to the right battles."
        </p>
        <p className="text-xs uppercase tracking-[0.3em] text-charcoal/40 font-medium">
          Raptorflow — 2025
        </p>
      </div>
    </footer>
  )
}

// ============================================================================
// MAIN LANDING PAGE
// ============================================================================

export default function Landing() {
  return (
    <div className="min-h-screen bg-canvas antialiased selection:bg-gold selection:text-white font-sans">
      <Header />
      <main>
        <Hero />
        <ValueStrip />
        <PullQuote />
        <HowItWorks />
        <SevenPillars />
        <Pricing />
      </main>
      <Footer />
    </div>
  )
}
