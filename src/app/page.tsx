"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { MotionPathPlugin } from "gsap/MotionPathPlugin";
import Link from "next/link";
import {
  ArrowRight,
  Lock,
  Zap,
  Target,
  Sparkles,
  BarChart3,
  Check,
  ChevronDown,
  Play,
  Pause,
  RotateCcw,
  Eye,
  Layers,
  TrendingUp,
  Users,
  Compass,
  Shield,
  Clock,
  GitBranch,
  MousePointer2,
} from "lucide-react";
import { PageLoader } from "@/components/landing/PageLoader";
import { FloatingNav } from "@/components/landing/FloatingNav";
import { Logo } from "@/components/brand";

// Register GSAP plugins
if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger, MotionPathPlugin);
}

// ═══════════════════════════════════════════════════════════════════════════════
// RAPTORFLOW LANDING PAGE v2.0
// "The Marketing OS for Operators"
// 10x more components, animations, and intricate artwork
// ═══════════════════════════════════════════════════════════════════════════════

export default function LandingPage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [activeDemo, setActiveDemo] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);

  useEffect(() => {
    if (!containerRef.current || !isLoaded) return;

    const ctx = gsap.context(() => {
      // ═══════════════════════════════════════════════════════════════════════
      // HERO SECTION - Cinematic reveal
      // ═══════════════════════════════════════════════════════════════════════
      const heroTl = gsap.timeline({ delay: 0.3 });
      
      heroTl
        .fromTo(".hero-badge", 
          { scale: 0, opacity: 0 }, 
          { scale: 1, opacity: 1, duration: 0.6, ease: "back.out(1.7)" }
        )
        .fromTo(".hero-line1", 
          { y: 120, opacity: 0, rotateX: 45 }, 
          { y: 0, opacity: 1, rotateX: 0, duration: 1.2, ease: "power4.out" }, 
          "-=0.3"
        )
        .fromTo(".hero-line2", 
          { y: 120, opacity: 0, rotateX: 45 }, 
          { y: 0, opacity: 1, rotateX: 0, duration: 1.2, ease: "power4.out" }, 
          "-=0.9"
        )
        .fromTo(".hero-truth", 
          { scale: 0.8, opacity: 0, filter: "blur(20px)" }, 
          { scale: 1, opacity: 1, filter: "blur(0px)", duration: 1.4, ease: "power3.out" }, 
          "-=0.6"
        )
        .fromTo(".hero-underline", 
          { scaleX: 0 }, 
          { scaleX: 1, duration: 0.8, ease: "power2.inOut" }, 
          "-=0.4"
        )
        .fromTo(".hero-subhead", 
          { y: 40, opacity: 0 }, 
          { y: 0, opacity: 1, duration: 0.8, ease: "power2.out" }, 
          "-=0.4"
        )
        .fromTo(".hero-cta", 
          { y: 30, opacity: 0 }, 
          { y: 0, opacity: 1, duration: 0.6, ease: "power2.out" }, 
          "-=0.3"
        )
        .fromTo(".hero-social", 
          { y: 20, opacity: 0 }, 
          { y: 0, opacity: 1, duration: 0.5, ease: "power2.out" }, 
          "-=0.2"
        );

      // Hero parallax on scroll
      gsap.to(".hero-content", {
        yPercent: 50,
        ease: "none",
        scrollTrigger: {
          trigger: ".hero-section",
          start: "top top",
          end: "bottom top",
          scrub: true,
        },
      });

      // ═══════════════════════════════════════════════════════════════════════
      // FLOATING ORBS ANIMATION
      // ═══════════════════════════════════════════════════════════════════════
      gsap.utils.toArray<HTMLElement>(".floating-orb").forEach((orb, i) => {
        gsap.to(orb, {
          y: `${(i % 2 === 0 ? -1 : 1) * 30}`,
          x: `${(i % 3 === 0 ? -1 : 1) * 20}`,
          duration: 3 + i * 0.5,
          repeat: -1,
          yoyo: true,
          ease: "sine.inOut",
        });
      });

      // ═══════════════════════════════════════════════════════════════════════
      // PROBLEM SECTION - Pinned scroll
      // ═══════════════════════════════════════════════════════════════════════
      const problemCards = gsap.utils.toArray<HTMLElement>(".problem-card");
      
      ScrollTrigger.create({
        trigger: ".problem-section",
        start: "top 20%",
        end: "+=800",
        pin: ".problem-visual",
        pinSpacing: false,
      });

      problemCards.forEach((card, i) => {
        gsap.fromTo(card,
          { x: 100, opacity: 0, rotateY: -15 },
          {
            x: 0,
            opacity: 1,
            rotateY: 0,
            duration: 0.8,
            ease: "power2.out",
            scrollTrigger: {
              trigger: card,
              start: "top 80%",
              toggleActions: "play none none reverse",
            },
          }
        );
      });

      // ═══════════════════════════════════════════════════════════════════════
      // COCKPIT DIAGRAM - Complex SVG animation
      // ═══════════════════════════════════════════════════════════════════════
      const cockpitTl = gsap.timeline({
        scrollTrigger: {
          trigger: ".cockpit-section",
          start: "top 60%",
          end: "center center",
          scrub: 1,
        },
      });

      cockpitTl
        .fromTo(".cockpit-center", 
          { scale: 0, opacity: 0 }, 
          { scale: 1, opacity: 1, ease: "back.out(1.7)" }
        )
        .fromTo(".cockpit-line", 
          { strokeDashoffset: 300 }, 
          { strokeDashoffset: 0, stagger: 0.1 }, 
          "-=0.5"
        )
        .fromTo(".cockpit-node", 
          { scale: 0 }, 
          { scale: 1, stagger: 0.1, ease: "back.out(2)" }, 
          "-=0.3"
        );

      // ═══════════════════════════════════════════════════════════════════════
      // FEATURE CARDS - Staggered 3D reveal
      // ═══════════════════════════════════════════════════════════════════════
      gsap.fromTo(".feature-card",
        { 
          y: 100, 
          opacity: 0, 
          rotateX: 25,
          transformPerspective: 1000,
        },
        {
          y: 0,
          opacity: 1,
          rotateX: 0,
          duration: 0.8,
          stagger: {
            each: 0.15,
            from: "start",
          },
          ease: "power2.out",
          scrollTrigger: {
            trigger: ".features-grid",
            start: "top 75%",
          },
        }
      );

      // Feature card hover parallax
      gsap.utils.toArray<HTMLElement>(".feature-card").forEach((card) => {
        card.addEventListener("mouseenter", () => {
          gsap.to(card, { y: -8, scale: 1.02, duration: 0.3, ease: "power2.out" });
        });
        card.addEventListener("mouseleave", () => {
          gsap.to(card, { y: 0, scale: 1, duration: 0.3, ease: "power2.out" });
        });
      });

      // ═══════════════════════════════════════════════════════════════════════
      // STATS COUNTER - Animated counting
      // ═══════════════════════════════════════════════════════════════════════
      gsap.utils.toArray<HTMLElement>(".stat-number").forEach((stat) => {
        const value = parseInt(stat.dataset.value || "0");
        const suffix = stat.dataset.suffix || "";
        
        ScrollTrigger.create({
          trigger: stat,
          start: "top 85%",
          onEnter: () => {
            gsap.to(stat, {
              innerText: value,
              duration: 2.5,
              ease: "power2.out",
              snap: { innerText: 1 },
              onUpdate: function() {
                stat.innerText = Math.round(parseFloat(stat.innerText || "0")) + suffix;
              },
            });
          },
          once: true,
        });
      });

      // ═══════════════════════════════════════════════════════════════════════
      // DEMO SECTION - Interactive tabs
      // ═══════════════════════════════════════════════════════════════════════
      gsap.fromTo(".demo-container",
        { y: 60, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 1,
          ease: "power2.out",
          scrollTrigger: {
            trigger: ".demo-section",
            start: "top 70%",
          },
        }
      );

      // ═══════════════════════════════════════════════════════════════════════
      // PRINCIPLES - Horizontal scroll reveal
      // ═══════════════════════════════════════════════════════════════════════
      gsap.utils.toArray<HTMLElement>(".principle-card").forEach((card, i) => {
        gsap.fromTo(card,
          { x: i % 2 === 0 ? -60 : 60, opacity: 0 },
          {
            x: 0,
            opacity: 1,
            duration: 0.8,
            ease: "power2.out",
            scrollTrigger: {
              trigger: card,
              start: "top 85%",
              toggleActions: "play none none reverse",
            },
          }
        );
      });

      // ═══════════════════════════════════════════════════════════════════════
      // PERSONA CARDS - Staggered reveal
      // ═══════════════════════════════════════════════════════════════════════
      gsap.fromTo(".persona-card",
        { y: 60, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.7,
          stagger: 0.15,
          ease: "power2.out",
          scrollTrigger: {
            trigger: ".persona-grid",
            start: "top 75%",
          },
        }
      );

      // ═══════════════════════════════════════════════════════════════════════
      // INTEGRATIONS - Orbit animation
      // ═══════════════════════════════════════════════════════════════════════
      gsap.to(".orbit-ring", {
        rotation: 360,
        duration: 60,
        repeat: -1,
        ease: "none",
      });

      gsap.to(".orbit-icon", {
        rotation: -360,
        duration: 60,
        repeat: -1,
        ease: "none",
      });

      // ═══════════════════════════════════════════════════════════════════════
      // PATH JOURNEY - SVG motion path
      // ═══════════════════════════════════════════════════════════════════════
      gsap.to(".journey-dot", {
        motionPath: {
          path: ".journey-path",
          align: ".journey-path",
          alignOrigin: [0.5, 0.5],
        },
        duration: 4,
        repeat: -1,
        ease: "none",
        scrollTrigger: {
          trigger: ".journey-section",
          start: "top 80%",
          toggleActions: "play pause resume pause",
        },
      });

      // ═══════════════════════════════════════════════════════════════════════
      // GLOBE SECTION - 3D perspective
      // ═══════════════════════════════════════════════════════════════════════
      gsap.fromTo(".globe-container",
        { rotateX: 20, opacity: 0 },
        {
          rotateX: 0,
          opacity: 1,
          duration: 1.2,
          ease: "power2.out",
          scrollTrigger: {
            trigger: ".globe-section",
            start: "top 70%",
          },
        }
      );

      // Pulse animation for globe dots
      gsap.utils.toArray<HTMLElement>(".globe-dot").forEach((dot, i) => {
        gsap.to(dot, {
          opacity: 0.3,
          duration: 1.5,
          repeat: -1,
          yoyo: true,
          delay: i * 0.1,
          ease: "sine.inOut",
        });
      });

    }, containerRef);

    return () => ctx.revert();
  }, [isLoaded]);

  // Demo autoplay
  useEffect(() => {
    if (!isPlaying) return;
    const interval = setInterval(() => {
      setActiveDemo((prev) => (prev + 1) % 4);
    }, 4000);
    return () => clearInterval(interval);
  }, [isPlaying]);

  return (
    <>
      <PageLoader onComplete={() => setIsLoaded(true)} />
      <FloatingNav />
      
      <div ref={containerRef} className="min-h-screen bg-[var(--bg-canvas)] overflow-x-hidden">
        
        {/* ═══════════════════════════════════════════════════════════════════════
            TOP NAVIGATION — Fixed header with intricate Logo
        ═══════════════════════════════════════════════════════════════════════ */}
        <header className="fixed top-0 left-0 right-0 z-40 px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            {/* Logo with magnetic hover */}
            <Link href="/" className="flex items-center gap-3 group">
              <Logo 
                size={36} 
                mode="light" 
                variant="static"
                magnetic={true}
                className="transition-transform duration-300 group-hover:scale-105" 
              />
              <span className="font-semibold text-xl text-[#2A2529] hidden sm:block tracking-tight">
                RaptorFlow
              </span>
            </Link>

            {/* Center Navigation */}
            <nav className="hidden md:flex items-center gap-1 bg-[#F7F5EF]/80 backdrop-blur-md border border-[#E3DED3] rounded-full px-2 py-1">
              {[
                { label: "Features", href: "#features" },
                { label: "Demo", href: "#demo" },
                { label: "Docs", href: "/docs" },
                { label: "Support", href: "/support" },
              ].map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  className="px-4 py-2 rf-body-sm text-[#5C565B] hover:text-[#2A2529] rounded-full hover:bg-[#F3F0E7] transition-all"
                >
                  {item.label}
                </a>
              ))}
            </nav>

            {/* Right Actions */}
            <div className="flex items-center gap-3">
              <Link 
                href="/login" 
                className="hidden sm:block rf-body-sm text-[#5C565B] hover:text-[#2A2529] px-4 py-2 transition-colors"
              >
                Sign In
              </Link>
              <Link 
                href="/dashboard" 
                className="rf-btn rf-btn-primary h-10 px-5 text-sm flex items-center gap-2 bg-[#2A2529] text-[#F3F0E7] rounded-lg hover:bg-[#3A3539] transition-colors"
              >
                Start Building
                <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        </header>

        {/* ═══════════════════════════════════════════════════════════════════════
            HERO SECTION - Full viewport with parallax
        ═══════════════════════════════════════════════════════════════════════ */}
        <section className="hero-section relative min-h-screen flex items-center justify-center px-6 pt-20 overflow-hidden">
          {/* Animated background orbs */}
          <div className="absolute inset-0 pointer-events-none overflow-hidden">
            <div className="floating-orb absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-[var(--ink-1)] opacity-[0.03] rounded-full blur-3xl" />
            <div className="floating-orb absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-[var(--ink-1)] opacity-[0.04] rounded-full blur-3xl" />
            <div className="floating-orb absolute top-1/2 left-1/2 w-[300px] h-[300px] bg-[var(--status-success)] opacity-[0.02] rounded-full blur-3xl" />
            
            {/* Grid pattern */}
            <div className="absolute inset-0 opacity-[0.02]" style={{
              backgroundImage: `linear-gradient(var(--ink-1) 1px, transparent 1px), linear-gradient(90deg, var(--ink-1) 1px, transparent 1px)`,
              backgroundSize: '60px 60px'
            }} />
          </div>

          <div className="hero-content max-w-6xl mx-auto text-center relative z-10">
            {/* Animated badge */}
            <div className="hero-badge inline-flex items-center gap-2 px-4 py-2 bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-full mb-8 backdrop-blur-sm">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--status-success)] opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--status-success)]"></span>
              </span>
              <span className="rf-mono-xs text-[var(--ink-2)] uppercase tracking-wider">Now in Public Beta</span>
            </div>

            {/* Main headline with 3D perspective */}
            <div className="perspective-1000">
              <h1 className="hero-headline text-[clamp(48px,12vw,120px)] leading-[1.05] font-bold tracking-tight">
                <span className="hero-line1 block text-[var(--ink-1)]">Marketing is not</span>
                <span className="hero-line2 block text-[var(--ink-3)] mt-2">a funnel.</span>
                <span className="hero-line1 block text-[var(--ink-1)] mt-4">It&apos;s a</span>
                <span className="hero-truth relative inline-block mt-4">
                  <span className="relative z-10 text-[var(--ink-1)]">truth machine.</span>
                  <span className="hero-underline absolute -bottom-2 left-0 w-full h-3 bg-[var(--ink-1)] opacity-20 origin-left" />
                  <svg className="absolute -bottom-4 left-0 w-full h-6" viewBox="0 0 400 12" preserveAspectRatio="none">
                    <path d="M0,6 Q100,0 200,6 T400,6" fill="none" stroke="var(--ink-1)" strokeWidth="2" opacity="0.3" />
                  </svg>
                </span>
              </h1>
            </div>

            {/* Subhead with blur reveal */}
            <p className="hero-subhead rf-body text-[var(--ink-2)] max-w-3xl mx-auto mb-10 text-lg md:text-xl mt-8 leading-relaxed">
              RaptorFlow is the marketing OS for operators who demand precision. 
              Build your foundation. Lock your strategy. Execute with AI that knows your business—not generic templates.
            </p>

            {/* CTAs with magnetic effect */}
            <div className="hero-cta flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/dashboard" className="group relative rf-btn rf-btn-primary h-14 px-8 text-base overflow-hidden">
                <span className="relative z-10 flex items-center gap-2">
                  Start Building Free
                  <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-[var(--ink-1)] to-[var(--ink-2)] opacity-0 group-hover:opacity-100 transition-opacity" />
              </Link>
              <button 
                onClick={() => document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth' })}
                className="group rf-btn rf-btn-secondary h-14 px-8 text-base flex items-center gap-2"
              >
                <Play size={18} className="text-[var(--ink-2)]" />
                See It In Action
              </button>
            </div>

            {/* Beta badge */}
            <div className="hero-social mt-16 flex flex-col items-center gap-4">
              <div className="flex items-center gap-4 px-6 py-3 bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-full">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--status-success)] opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--status-success)]"></span>
                </span>
                <span className="rf-body-sm text-[var(--ink-2)]">
                  Public Beta — <Link href="/dashboard" className="text-[var(--ink-1)] font-medium hover:underline">Be among the first →</Link>
                </span>
              </div>
              <p className="rf-body-sm text-[var(--ink-3)]">
                Built for operators at early-stage SaaS companies
              </p>
            </div>
          </div>

          {/* Animated scroll indicator */}
          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-3">
            <span className="rf-mono-xs text-[var(--ink-3)] uppercase tracking-wider">Scroll to explore</span>
            <div className="w-6 h-10 border-2 border-[var(--border-2)] rounded-full flex items-start justify-center p-2">
              <div className="w-1.5 h-2.5 bg-[var(--ink-2)] rounded-full animate-bounce" />
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════════════════
            PROBLEM SECTION - Pinned scroll with cards
        ═══════════════════════════════════════════════════════════════════════ */}
        <section className="problem-section py-32 px-6 min-h-screen">
          <div className="max-w-6xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-16 items-start">
              {/* Left: Sticky visual */}
              <div className="problem-visual lg:sticky lg:top-32">
                <span className="rf-mono-xs text-[var(--status-error)] uppercase tracking-wider flex items-center gap-2">
                  <span className="w-8 h-px bg-[var(--status-error)]" />
                  The Problem
                </span>
                <h2 className="rf-h1 mt-6 mb-6 text-4xl md:text-5xl">
                  Marketing has become a <span className="text-[var(--status-error)]">circus</span> of disconnected tools.
                </h2>
                <p className="rf-body text-[var(--ink-2)] mb-8">
                  The average marketing team juggles 12+ tools. Strategy lives in docs no one reads. 
                  Campaigns scatter across platforms. And AI? It generates content that sounds like everyone else.
                </p>
                
                {/* Visual chaos representation */}
                <div className="relative h-64 mt-8">
                  {[0, 1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className="absolute w-20 h-20 bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-[var(--radius-md)] flex items-center justify-center shadow-lg"
                      style={{
                        top: `${15 + (i % 3) * 25}%`,
                        left: `${10 + (i % 2) * 50}%`,
                        transform: `rotate(${(i - 2) * 12}deg)`,
                        animationDelay: `${i * 0.2}s`,
                      }}
                    >
                      <div className="w-8 h-8 rounded bg-[var(--border-1)]" />
                    </div>
                  ))}
                  {/* Connection lines that break */}
                  <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-20">
                    <line x1="20%" y1="30%" x2="60%" y2="50%" stroke="var(--status-error)" strokeWidth="2" strokeDasharray="5,5" />
                    <line x1="60%" y1="30%" x2="30%" y2="70%" stroke="var(--status-error)" strokeWidth="2" strokeDasharray="5,5" />
                    <line x1="30%" y1="50%" x2="70%" y2="60%" stroke="var(--status-error)" strokeWidth="2" strokeDasharray="5,5" />
                  </svg>
                </div>
              </div>

              {/* Right: Scrolling cards */}
              <div className="space-y-6">
                {[
                  {
                    icon: Layers,
                    title: "Tool Sprawl",
                    description: "Strategy in Notion. Campaigns in Asana. Analytics in Google. Content in 6 different AI tools. Nothing talks to anything.",
                    stat: "12+ avg tools",
                  },
                  {
                    icon: Shield,
                    title: "Strategy Decay",
                    description: "Your positioning lives in a doc from 6 months ago. Nobody references it. Every campaign reinvents the wheel.",
                    stat: "73% outdated",
                  },
                  {
                    icon: Clock,
                    title: "Context Loss",
                    description: "Why did we make that decision? Who knows. The reasoning is buried in Slack threads and forgotten meetings.",
                    stat: "Zero memory",
                  },
                  {
                    icon: TrendingUp,
                    title: "Generic AI Slop",
                    description: "ChatGPT doesn't know your ICPs. Doesn't understand your positioning. Generates content that sounds like your competitors.",
                    stat: "100% generic",
                  },
                ].map((problem, i) => (
                  <div
                    key={i}
                    className="problem-card p-8 bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-[var(--radius-lg)] hover:border-[var(--status-error)]/30 transition-colors group"
                  >
                    <div className="flex items-start gap-6">
                      <div className="w-14 h-14 rounded-[var(--radius-md)] bg-[var(--status-error)]/10 flex items-center justify-center flex-shrink-0 group-hover:bg-[var(--status-error)]/20 transition-colors">
                        <problem.icon size={28} className="text-[var(--status-error)]" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="rf-h4">{problem.title}</h3>
                          <span className="rf-mono-xs px-2 py-1 bg-[var(--status-error)]/10 text-[var(--status-error)] rounded-full">
                            {problem.stat}
                          </span>
                        </div>
                        <p className="rf-body text-[var(--ink-2)]">{problem.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════════════════
            SOLUTION SECTION - Cockpit + Autopilot
        ═══════════════════════════════════════════════════════════════════════ */}
        <section className="cockpit-section py-32 px-6 bg-[var(--bg-surface)]">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-20">
              <span className="rf-mono-xs text-[var(--ink-1)] uppercase tracking-wider flex items-center justify-center gap-3">
                <span className="w-8 h-px bg-[var(--ink-1)]" />
                The Solution
                <span className="w-8 h-px bg-[var(--ink-1)]" />
              </span>
              <h2 className="rf-h1 mt-6 mb-6 text-5xl md:text-7xl">
                Cockpit <span className="text-[var(--ink-3)]">+</span> Autopilot
              </h2>
              <p className="rf-body text-[var(--ink-2)] max-w-2xl mx-auto text-lg">
                You&apos;re the operator. The system is your instrument panel. 
                AI proposes, you decide. Nothing happens without your commit.
              </p>
            </div>

            <div className="grid lg:grid-cols-2 gap-16 items-center">
              {/* Interactive diagram */}
              <div className="relative aspect-square max-w-lg mx-auto">
                <svg viewBox="0 0 400 400" className="w-full h-full">
                  {/* Outer ring */}
                  <circle cx="200" cy="200" r="180" fill="none" stroke="var(--border-1)" strokeWidth="1" strokeDasharray="4,4" opacity="0.5" />
                  
                  {/* Connecting lines */}
                  <line className="cockpit-line" x1="200" y1="120" x2="200" y2="60" stroke="var(--border-2)" strokeWidth="2" strokeDasharray="300" strokeDashoffset="300" />
                  <line className="cockpit-line" x1="280" y1="200" x2="340" y2="200" stroke="var(--border-2)" strokeWidth="2" strokeDasharray="300" strokeDashoffset="300" />
                  <line className="cockpit-line" x1="200" y1="280" x2="200" y2="340" stroke="var(--border-2)" strokeWidth="2" strokeDasharray="300" strokeDashoffset="300" />
                  <line className="cockpit-line" x1="120" y1="200" x2="60" y2="200" stroke="var(--border-2)" strokeWidth="2" strokeDasharray="300" strokeDashoffset="300" />
                  
                  {/* Center - You */}
                  <g className="cockpit-center">
                    <circle cx="200" cy="200" r="50" fill="var(--ink-1)" />
                    <text x="200" y="195" textAnchor="middle" fill="var(--ink-inverse)" className="rf-mono-xs font-bold">YOU</text>
                    <text x="200" y="212" textAnchor="middle" fill="var(--ink-inverse)" className="rf-mono-xs" opacity="0.7">Operator</text>
                  </g>
                  
                  {/* Module nodes */}
                  <g className="cockpit-node" transform="translate(160, 20)">
                    <rect width="80" height="40" rx="8" fill="var(--bg-canvas)" stroke="var(--border-1)" />
                    <text x="40" y="25" textAnchor="middle" fill="var(--ink-2)" className="rf-mono-xs">FOUNDATION</text>
                  </g>
                  
                  <g className="cockpit-node" transform="translate(340, 180)">
                    <rect width="80" height="40" rx="8" fill="var(--bg-canvas)" stroke="var(--border-1)" />
                    <text x="40" y="25" textAnchor="middle" fill="var(--ink-2)" className="rf-mono-xs">MOVES</text>
                  </g>
                  
                  <g className="cockpit-node" transform="translate(160, 340)">
                    <rect width="80" height="40" rx="8" fill="var(--bg-canvas)" stroke="var(--border-1)" />
                    <text x="40" y="25" textAnchor="middle" fill="var(--ink-2)" className="rf-mono-xs">CAMPAIGNS</text>
                  </g>
                  
                  <g className="cockpit-node" transform="translate(20, 180)">
                    <rect width="80" height="40" rx="8" fill="var(--bg-canvas)" stroke="var(--border-1)" />
                    <text x="40" y="25" textAnchor="middle" fill="var(--ink-2)" className="rf-mono-xs">MUSE</text>
                  </g>
                </svg>

                {/* Orbiting particles */}
                <div className="absolute inset-0 animate-spin" style={{ animationDuration: '20s' }}>
                  <div className="absolute top-0 left-1/2 w-2 h-2 bg-[var(--ink-1)] rounded-full" />
                </div>
              </div>

              {/* Feature breakdown */}
              <div className="space-y-8">
                {[
                  {
                    icon: Target,
                    title: "Cockpit (You)",
                    color: "var(--ink-1)",
                    points: [
                      "See options, tradeoffs, and confidence scores",
                      "Choose direction and edit any assumption",
                      "Lock what becomes truth",
                      "Maintain full reversibility",
                    ],
                  },
                  {
                    icon: Sparkles,
                    title: "Autopilot (AI)",
                    color: "var(--status-info)",
                    points: [
                      "Generates drafts based on your foundation",
                      "Tracks changes and maintains decision log",
                      "Suggests next moves based on goals",
                      "Never publishes without your commit",
                    ],
                  },
                ].map((section, i) => (
                  <div key={i} className="group">
                    <div className="flex items-center gap-4 mb-4">
                      <div 
                        className="w-12 h-12 rounded-[var(--radius-md)] flex items-center justify-center transition-transform group-hover:scale-110"
                        style={{ backgroundColor: `${section.color}15` }}
                      >
                        <section.icon size={24} style={{ color: section.color }} />
                      </div>
                      <h3 className="rf-h3">{section.title}</h3>
                    </div>
                    <ul className="space-y-3 pl-16">
                      {section.points.map((point, j) => (
                        <li key={j} className="flex items-start gap-3">
                          <span className="w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0" style={{ backgroundColor: section.color }} />
                          <span className="rf-body text-[var(--ink-2)]">{point}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}

                <div className="p-6 bg-[var(--bg-canvas)] rounded-[var(--radius-md)] border border-[var(--border-1)] mt-8">
                  <p className="rf-body text-[var(--ink-2)] italic">
                    &ldquo;The best AI is invisible infrastructure. You steer. It handles the grinding.&rdquo;
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════════════════
            FEATURES GRID - 3D card reveals
        ═══════════════════════════════════════════════════════════════════════ */}
        <section id="features" className="py-32 px-6">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-20">
              <span className="rf-mono-xs text-[var(--ink-1)] uppercase tracking-wider">Modules</span>
              <h2 className="rf-h1 mt-6 mb-6">Four systems. One truth.</h2>
              <p className="rf-body text-[var(--ink-2)] max-w-2xl mx-auto">
                Each module locks into the others. Your foundation informs your moves. 
                Your moves feed your campaigns. Everything connects.
              </p>
            </div>

            <div className="features-grid grid md:grid-cols-2 gap-6">
              {[
                {
                  icon: Lock,
                  title: "Foundation",
                  subtitle: "Ground truth",
                  description: "Lock your positioning, ICPs, and messaging. Everything else builds from here. Version controlled. Always reversible.",
                  stat: "Synthesized",
                  color: "var(--ink-1)",
                  features: ["Positioning statement", "ICP definitions", "Brand voice", "Channel strategy"],
                },
                {
                  icon: Zap,
                  title: "Moves",
                  subtitle: "Strategic sprints",
                  description: "5 categories of strategic moves. Ignite, Capture, Authority, Repair, Rally. Each with AI-generated execution plans.",
                  stat: "5 Categories",
                  color: "var(--status-warning)",
                  features: ["14-day sprints", "Execution checklists", "Daily agendas", "Progress tracking"],
                },
                {
                  icon: Sparkles,
                  title: "Muse",
                  subtitle: "Context-aware AI",
                  description: "AI that knows your foundation. Pull-based suggestions that live in the proposal drawer. Never pushy. Always relevant.",
                  stat: "Context-Aware",
                  color: "var(--status-info)",
                  features: ["Foundation-aware", "Proposal drawer", "Content generation", "Variant testing"],
                },
                {
                  icon: BarChart3,
                  title: "Campaigns",
                  subtitle: "Outcome-linked",
                  description: "Every task ties to a metric and hypothesis. No project management theater. Just execution tied to outcomes.",
                  stat: "Tracked",
                  color: "var(--status-success)",
                  features: ["Hypothesis tracking", "Outcome metrics", "Timeline view", "Team collaboration"],
                },
              ].map((feature, i) => (
                <div
                  key={i}
                  className="feature-card group relative p-8 bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-[var(--radius-lg)] hover:border-[var(--border-2)] transition-all duration-300 overflow-hidden"
                  style={{ transformStyle: 'preserve-3d' }}
                >
                  {/* Hover glow effect */}
                  <div 
                    className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                    style={{ 
                      background: `radial-gradient(circle at 50% 0%, ${feature.color}10, transparent 70%)` 
                    }}
                  />

                  <div className="relative">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-6">
                      <div 
                        className="w-14 h-14 rounded-[var(--radius-md)] flex items-center justify-center transition-transform duration-300 group-hover:scale-110"
                        style={{ backgroundColor: `${feature.color}15` }}
                      >
                        <feature.icon size={28} style={{ color: feature.color }} />
                      </div>
                      <span 
                        className="rf-mono-xs px-3 py-1 rounded-full"
                        style={{ backgroundColor: `${feature.color}15`, color: feature.color }}
                      >
                        {feature.stat}
                      </span>
                    </div>

                    {/* Content */}
                    <div className="mb-6">
                      <h3 className="rf-h3 mb-1 group-hover:translate-x-1 transition-transform duration-300">{feature.title}</h3>
                      <p className="rf-mono-xs text-[var(--ink-3)] uppercase tracking-wider mb-3">{feature.subtitle}</p>
                      <p className="rf-body text-[var(--ink-2)]">{feature.description}</p>
                    </div>

                    {/* Feature list */}
                    <div className="flex flex-wrap gap-2">
                      {feature.features.map((f, j) => (
                        <span key={j} className="rf-mono-xs px-2 py-1 bg-[var(--bg-canvas)] rounded text-[var(--ink-2)]">
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════════════════
            DEMO SECTION - Interactive tabs
        ═══════════════════════════════════════════════════════════════════════ */}
        <section id="demo" className="demo-section py-32 px-6 bg-[var(--bg-surface)]">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <span className="rf-mono-xs text-[var(--ink-1)] uppercase tracking-wider">See It In Action</span>
              <h2 className="rf-h1 mt-6 mb-6">How operators use RaptorFlow</h2>
            </div>

            <div className="demo-container grid lg:grid-cols-3 gap-8">
              {/* Tab navigation */}
              <div className="space-y-4">
                {[
                  { title: "Lock Your Foundation", duration: "0:00 - 0:45" },
                  { title: "Generate Strategic Moves", duration: "0:45 - 1:30" },
                  { title: "Execute With Muse", duration: "1:30 - 2:15" },
                  { title: "Track & Optimize", duration: "2:15 - 3:00" },
                ].map((demo, i) => (
                  <button
                    key={i}
                    onClick={() => setActiveDemo(i)}
                    className={`w-full text-left p-4 rounded-[var(--radius-md)] border transition-all ${
                      activeDemo === i 
                        ? 'bg-[var(--ink-1)] border-[var(--ink-1)] text-[var(--ink-inverse)]' 
                        : 'bg-[var(--bg-canvas)] border-[var(--border-1)] hover:border-[var(--border-2)]'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          activeDemo === i ? 'bg-[var(--ink-inverse)]/20' : 'bg-[var(--bg-surface)]'
                        }`}>
                          {activeDemo === i ? <Pause size={14} /> : <Play size={14} />}
                        </div>
                        <div>
                          <p className={`font-medium ${activeDemo === i ? 'text-[var(--ink-inverse)]' : 'text-[var(--ink-1)]'}`}>
                            {demo.title}
                          </p>
                          <p className={`rf-mono-xs ${activeDemo === i ? 'text-[var(--ink-inverse)]/70' : 'text-[var(--ink-3)]'}`}>
                            {demo.duration}
                          </p>
                        </div>
                      </div>
                      {activeDemo === i && (
                        <div className="w-16 h-1 bg-[var(--ink-inverse)]/20 rounded-full overflow-hidden">
                          <div className="h-full bg-[var(--ink-inverse)] animate-[loading_4s_linear]" />
                        </div>
                      )}
                    </div>
                  </button>
                ))}

                {/* Autoplay toggle */}
                <button 
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="flex items-center gap-2 text-[var(--ink-3)] hover:text-[var(--ink-1)] transition-colors mt-4"
                >
                  {isPlaying ? <Pause size={16} /> : <Play size={16} />}
                  <span className="rf-body-sm">{isPlaying ? 'Autoplay on' : 'Autoplay off'}</span>
                </button>
              </div>

              {/* Demo display */}
              <div className="lg:col-span-2">
                <div className="relative aspect-video bg-[var(--ink-1)] rounded-[var(--radius-lg)] overflow-hidden">
                  {/* Mock UI */}
                  <div className="absolute inset-0 p-8">
                    <div className="h-full bg-[var(--bg-surface)] rounded-[var(--radius-md)] p-6">
                      {activeDemo === 0 && (
                        <div className="space-y-4">
                          <div className="flex items-center gap-4 pb-4 border-b border-[var(--border-1)]">
                            <div className="w-10 h-10 rounded bg-[var(--ink-1)]" />
                            <div className="flex-1">
                              <div className="h-4 w-32 bg-[var(--border-1)] rounded" />
                              <div className="h-3 w-24 bg-[var(--border-2)] rounded mt-2" />
                            </div>
                          </div>
                          <div className="space-y-3">
                            <div className="h-3 w-full bg-[var(--border-1)] rounded" />
                            <div className="h-3 w-5/6 bg-[var(--border-1)] rounded" />
                            <div className="h-3 w-4/6 bg-[var(--border-1)] rounded" />
                          </div>
                        </div>
                      )}
                      {activeDemo === 1 && (
                        <div className="grid grid-cols-3 gap-4">
                          {[1, 2, 3].map((i) => (
                            <div key={i} className="p-4 bg-[var(--bg-canvas)] rounded-[var(--radius-md)]">
                              <div className="w-8 h-8 rounded bg-[var(--status-warning)]/20 mb-3" />
                              <div className="h-3 w-full bg-[var(--border-1)] rounded" />
                            </div>
                          ))}
                        </div>
                      )}
                      {activeDemo === 2 && (
                        <div className="flex gap-4 h-full">
                          <div className="w-2/3 space-y-4">
                            <div className="p-4 bg-[var(--status-info)]/10 rounded-[var(--radius-md)]">
                              <div className="h-3 w-full bg-[var(--border-1)] rounded" />
                            </div>
                            <div className="p-4 bg-[var(--bg-canvas)] rounded-[var(--radius-md)]">
                              <div className="h-3 w-full bg-[var(--border-1)] rounded" />
                            </div>
                          </div>
                          <div className="w-1/3 bg-[var(--bg-canvas)] rounded-[var(--radius-md)] p-4">
                            <div className="h-3 w-full bg-[var(--border-1)] rounded mb-2" />
                            <div className="h-3 w-2/3 bg-[var(--border-2)] rounded" />
                          </div>
                        </div>
                      )}
                      {activeDemo === 3 && (
                        <div className="space-y-4">
                          <div className="flex items-end gap-4 h-32">
                            {[40, 65, 45, 80, 55, 70].map((h, i) => (
                              <div key={i} className="flex-1 bg-[var(--status-success)]/20 rounded-t" style={{ height: `${h}%` }} />
                            ))}
                          </div>
                          <div className="flex justify-between">
                            {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((d) => (
                              <span key={d} className="rf-mono-xs text-[var(--ink-3)]">{d}</span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Play overlay */}
                  <div className="absolute inset-0 flex items-center justify-center bg-black/20 opacity-0 hover:opacity-100 transition-opacity">
                    <button className="w-16 h-16 rounded-full bg-[var(--ink-inverse)] flex items-center justify-center">
                      <Play size={24} className="text-[var(--ink-1)] ml-1" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════════════════
            STATS SECTION - Dark interlude with counters
        ═══════════════════════════════════════════════════════════════════════ */}
        <section className="py-24 px-6 bg-[var(--ink-1)] text-[var(--ink-inverse)] relative overflow-hidden">
          {/* Background pattern */}
          <div className="absolute inset-0 opacity-5">
            <div className="absolute inset-0" style={{
              backgroundImage: `radial-gradient(circle at 2px 2px, var(--ink-inverse) 1px, transparent 0)`,
              backgroundSize: '40px 40px'
            }} />
          </div>

          <div className="max-w-6xl mx-auto relative">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-12">
              {[
                { value: 47, suffix: "%", label: "Faster execution", sub: "vs traditional workflows" },
                { value: 6, suffix: "", label: "Tools replaced", sub: "Consolidated into one OS" },
                { value: 100, suffix: "%", label: "Decision log", sub: "Never lose context again" },
                { value: 0, suffix: "", label: "AI slop", sub: "Context-aware only" },
              ].map((stat, i) => (
                <div key={i} className="reveal-section text-center">
                  <div className="text-5xl md:text-7xl font-bold mb-3 font-[family-name:var(--font-ui)]">
                    <span className="stat-number" data-value={stat.value} data-suffix={stat.suffix}>0</span>
                    <span className="text-[var(--ink-inverse)]/60">{stat.suffix}</span>
                  </div>
                  <p className="rf-body font-medium mb-1">{stat.label}</p>
                  <p className="rf-body-sm opacity-60">{stat.sub}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════════════════
            PRINCIPLES SECTION - Alternating layout
        ═══════════════════════════════════════════════════════════════════════ */}
        <section className="py-32 px-6">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-20">
              <span className="rf-mono-xs text-[var(--ink-1)] uppercase tracking-wider">Principles</span>
              <h2 className="rf-h1 mt-6 mb-6">How we think about marketing</h2>
              <p className="rf-body text-[var(--ink-2)] max-w-2xl mx-auto">
                These aren&apos;t features. They&apos;re the philosophy that guides every decision we make.
              </p>
            </div>

            <div className="space-y-6">
              {[
                {
                  icon: Compass,
                  title: "Truth over trends",
                  description: "Your foundation is the source of truth. Not templates, not 'best practices', not what worked for someone else. Build from first principles.",
                },
                {
                  icon: GitBranch,
                  title: "Lock, don't lose",
                  description: "When something works, lock it. Version it. But never lose the ability to iterate from a stable baseline. Draft → Lock → Live.",
                },
                {
                  icon: MousePointer2,
                  title: "Pull, not push",
                  description: "AI suggestions live in the proposal drawer. The work surface stays clean. You choose when to engage. No interruptions.",
                },
                {
                  icon: Eye,
                  title: "One decision per screen",
                  description: "Every view answers: What's the goal? What's the best move? What happens if I click? Clarity is not simplicity. It's the removal of ambiguity.",
                },
              ].map((principle, i) => (
                <div
                  key={i}
                  className={`principle-card flex items-start gap-8 p-8 bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-[var(--radius-lg)] hover:border-[var(--border-2)] transition-all group ${
                    i % 2 === 0 ? '' : 'lg:flex-row-reverse'
                  }`}
                >
                  <div className="w-16 h-16 rounded-[var(--radius-md)] bg-[var(--bg-canvas)] flex items-center justify-center flex-shrink-0 group-hover:bg-[var(--ink-1)] group-hover:text-[var(--ink-inverse)] transition-colors">
                    <principle.icon size={28} />
                  </div>
                  <div className="flex-1">
                    <h3 className="rf-h3 mb-3">{principle.title}</h3>
                    <p className="rf-body text-[var(--ink-2)] text-lg leading-relaxed">{principle.description}</p>
                  </div>
                  <div className="text-6xl font-bold text-[var(--border-1)] opacity-30">
                    0{i + 1}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════════════════
            BUILT FOR - Target personas (no testimonials yet - we're brand new!)
        ═══════════════════════════════════════════════════════════════════════ */}
        <section className="py-32 px-6 bg-[var(--bg-surface)]">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <span className="rf-mono-xs text-[var(--ink-1)] uppercase tracking-wider">Built For</span>
              <h2 className="rf-h1 mt-6 mb-6">Operators who are done with the circus.</h2>
              <p className="rf-body text-[var(--ink-2)] max-w-2xl mx-auto">
                We built RaptorFlow for a specific kind of marketer. One who thinks in systems, not tactics.
              </p>
            </div>

            <div className="persona-grid grid md:grid-cols-3 gap-8">
              {[
                {
                  icon: Target,
                  title: "The Solo Founder",
                  description: "You're wearing 12 hats. Marketing can't be one of them. You need a system that thinks so you don't have to.",
                  traits: ["Pre-PMF", "No marketing team", "Wants clarity, not complexity"],
                  color: "var(--status-info)",
                },
                {
                  icon: BarChart3,
                  title: "The Head of Growth",
                  description: "Your team is drowning in tools. Strategy lives in a Notion doc no one reads. You need a single source of truth.",
                  traits: ["Series A/B", "Small team", "Needs accountability"],
                  color: "var(--status-success)",
                },
                {
                  icon: Users,
                  title: "The Marketing Lead",
                  description: "You're tired of explaining the same positioning to every new agency. You want to lock it and move on.",
                  traits: ["Established product", "Agency relationships", "Process-oriented"],
                  color: "var(--status-warning)",
                },
              ].map((persona, i) => (
                <div
                  key={i}
                  className="persona-card group p-8 bg-[var(--bg-canvas)] border border-[var(--border-1)] rounded-[var(--radius-lg)] hover:border-[var(--border-2)] transition-all"
                >
                  {/* Header */}
                  <div 
                    className="w-16 h-16 rounded-[var(--radius-md)] flex items-center justify-center mb-6 transition-transform group-hover:scale-110"
                    style={{ backgroundColor: `${persona.color}15` }}
                  >
                    <persona.icon size={32} style={{ color: persona.color }} />
                  </div>

                  {/* Content */}
                  <h3 className="rf-h4 mb-3">{persona.title}</h3>
                  <p className="rf-body text-[var(--ink-2)] mb-6">{persona.description}</p>

                  {/* Traits */}
                  <div className="space-y-2">
                    {persona.traits.map((trait, j) => (
                      <div key={j} className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: persona.color }} />
                        <span className="rf-mono-xs text-[var(--ink-2)]">{trait}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Early access note */}
            <div className="mt-16 text-center">
              <p className="rf-body text-[var(--ink-3)]">
                Sound like you? We&apos;re in public beta. 
                <Link href="/dashboard" className="text-[var(--ink-1)] font-medium ml-1 hover:underline">
                  Start building free →
                </Link>
              </p>
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════════════════
            CTA SECTION - Final conversion
        ═══════════════════════════════════════════════════════════════════════ */}
        <section className="py-32 px-6 relative overflow-hidden">
          {/* Background glow */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[var(--ink-1)] opacity-[0.03] rounded-full blur-3xl" />

          <div className="max-w-4xl mx-auto text-center relative">
            <div className="reveal-section">
              <h2 className="rf-h1 text-5xl md:text-7xl mb-6">
                Ready to build your
                <br />
                <span className="relative inline-block">
                  truth machine?
                  <svg className="absolute -bottom-2 left-0 w-full" height="8" viewBox="0 0 200 8" preserveAspectRatio="none">
                    <path d="M0,4 Q50,0 100,4 T200,4" fill="none" stroke="var(--ink-1)" strokeWidth="3" />
                  </svg>
                </span>
              </h2>
              <p className="rf-body text-[var(--ink-2)] text-xl mb-6 max-w-2xl mx-auto">
                No credit card. No enterprise sales call. Just you, your strategy, and a system that remembers.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
                <Link 
                  href="/dashboard" 
                  className="group rf-btn rf-btn-primary h-16 px-12 text-lg"
                >
                  Start Building Free
                  <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                </Link>
              </div>
              <div className="flex flex-wrap items-center justify-center gap-6 text-[var(--ink-3)]">
                <span className="flex items-center gap-2">
                  <Check size={16} className="text-[var(--status-success)]" />
                  No auth required
                </span>
                <span className="flex items-center gap-2">
                  <Check size={16} className="text-[var(--status-success)]" />
                  Your data stays in your workspace
                </span>
                <span className="flex items-center gap-2">
                  <Check size={16} className="text-[var(--status-success)]" />
                  Free forever for core features
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════════════════
            FOOTER - Comprehensive with All Links
        ═══════════════════════════════════════════════════════════════════════ */}
        <footer className="py-20 px-6 border-t border-[var(--border-1)] bg-[var(--bg-surface)]">
          <div className="max-w-7xl mx-auto">
            {/* Main Footer Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 lg:gap-12 mb-16">
              {/* Brand Column */}
              <div className="col-span-2 md:col-span-3 lg:col-span-2">
                <Link href="/" className="flex items-center gap-3 mb-6 group">
                  <Logo 
                    size={48} 
                    mode="light" 
                    className="transition-transform group-hover:scale-105" 
                  />
                  <span className="font-semibold text-2xl text-[#2A2529]">RaptorFlow</span>
                </Link>
                <p className="rf-body text-[var(--ink-2)] mb-6 max-w-xs">
                  The marketing OS for operators who demand precision. Build truth. Lock strategy. Execute with AI.
                </p>
                <div className="flex gap-3">
                  {[
                    { name: "Twitter", href: "https://twitter.com/raptorflow", icon: "T" },
                    { name: "LinkedIn", href: "https://linkedin.com/company/raptorflow", icon: "L" },
                    { name: "GitHub", href: "https://github.com/raptorflow", icon: "G" },
                    { name: "Discord", href: "https://discord.gg/raptorflow", icon: "D" },
                  ].map((social) => (
                    <a 
                      key={social.name} 
                      href={social.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-10 h-10 rounded-full bg-[var(--bg-canvas)] flex items-center justify-center hover:bg-[var(--ink-1)] hover:text-[var(--ink-inverse)] transition-all duration-300"
                      aria-label={social.name}
                    >
                      <span className="rf-mono-xs font-bold">{social.icon}</span>
                    </a>
                  ))}
                </div>
              </div>

              {/* Product Column */}
              <div>
                <h4 className="rf-label mb-4 text-[var(--ink-1)]">Product</h4>
                <ul className="space-y-3">
                  {[
                    { label: "Features", href: "#features" },
                    { label: "Foundation", href: "/foundation" },
                    { label: "Moves", href: "/moves" },
                    { label: "Muse AI", href: "/muse" },
                    { label: "Campaigns", href: "/campaigns" },
                    { label: "Pricing", href: "/pricing" },
                    { label: "Changelog", href: "/changelog" },
                  ].map((link) => (
                    <li key={link.label}>
                      <Link 
                        href={link.href}
                        className="rf-body-sm text-[var(--ink-2)] hover:text-[var(--ink-1)] transition-colors"
                      >
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Resources Column */}
              <div>
                <h4 className="rf-label mb-4 text-[var(--ink-1)]">Resources</h4>
                <ul className="space-y-3">
                  {[
                    { label: "Documentation", href: "/docs" },
                    { label: "API Reference", href: "/api" },
                    { label: "Support Center", href: "/support" },
                    { label: "Help & FAQ", href: "/support" },
                    { label: "Community", href: "/community" },
                    { label: "Status", href: "https://status.raptorflow.ai" },
                  ].map((link) => (
                    <li key={link.label}>
                      <Link 
                        href={link.href}
                        className="rf-body-sm text-[var(--ink-2)] hover:text-[var(--ink-1)] transition-colors"
                      >
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Company Column */}
              <div>
                <h4 className="rf-label mb-4 text-[var(--ink-1)]">Company</h4>
                <ul className="space-y-3">
                  {[
                    { label: "About", href: "/about" },
                    { label: "Blog", href: "/blog" },
                    { label: "Careers", href: "/careers" },
                    { label: "Press Kit", href: "/press" },
                    { label: "Contact", href: "/contact" },
                  ].map((link) => (
                    <li key={link.label}>
                      <Link 
                        href={link.href}
                        className="rf-body-sm text-[var(--ink-2)] hover:text-[var(--ink-1)] transition-colors"
                      >
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Legal Column */}
              <div>
                <h4 className="rf-label mb-4 text-[var(--ink-1)]">Legal</h4>
                <ul className="space-y-3">
                  {[
                    { label: "Privacy Policy", href: "/legal/privacy" },
                    { label: "Terms of Service", href: "/legal/terms" },
                    { label: "Cookie Policy", href: "/legal/cookies" },
                    { label: "Security", href: "/security" },
                    { label: "GDPR", href: "/legal/gdpr" },
                  ].map((link) => (
                    <li key={link.label}>
                      <Link 
                        href={link.href}
                        className="rf-body-sm text-[var(--ink-2)] hover:text-[var(--ink-1)] transition-colors"
                      >
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Newsletter Section */}
            <div className="py-8 border-y border-[var(--border-1)] mb-8">
              <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                <div>
                  <h4 className="rf-h4 mb-2">Stay in the loop</h4>
                  <p className="rf-body-sm text-[var(--ink-2)]">
                    Get updates on new features, moves, and marketing strategies.
                  </p>
                </div>
                <div className="flex w-full md:w-auto gap-2">
                  <input
                    type="email"
                    placeholder="you@company.com"
                    className="rf-input flex-1 md:w-64"
                  />
                  <button className="rf-btn rf-btn-primary whitespace-nowrap">
                    Subscribe
                  </button>
                </div>
              </div>
            </div>

            {/* Bottom Bar */}
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <p className="rf-mono-xs text-[var(--ink-3)]">
                © 2025 RaptorFlow, Inc. All rights reserved. Built for operators.
              </p>
              <div className="flex items-center gap-6">
                <Link href="/legal/privacy" className="rf-mono-xs text-[var(--ink-3)] hover:text-[var(--ink-1)] transition-colors">
                  Privacy
                </Link>
                <Link href="/legal/terms" className="rf-mono-xs text-[var(--ink-3)] hover:text-[var(--ink-1)] transition-colors">
                  Terms
                </Link>
                <Link href="/legal/cookies" className="rf-mono-xs text-[var(--ink-3)] hover:text-[var(--ink-1)] transition-colors">
                  Cookies
                </Link>
                <button 
                  onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                  className="rf-mono-xs text-[var(--ink-3)] hover:text-[var(--ink-1)] transition-colors"
                >
                  Back to top ↑
                </button>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
