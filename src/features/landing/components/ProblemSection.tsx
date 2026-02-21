/**
 * ENHANCED WITH:
 * - context7: GSAP matchMedia for responsive animations
 * - frontend-animations: 3D card transforms, staggered reveals
 * - performance-optimization: will-change, passive scroll triggers
 * - raptorflow-design-vibe: Strict Charcoal/Ivory enforcement
 */

"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLandingStore } from "./LandingClient";

const PROBLEMS = [
  {
    number: "01",
    stat: "12+",
    statLabel: "tools juggled",
    title: "Tool Sprawl",
    description:
      "Your marketing stack is a dozen disconnected apps. Data lives in silos. Nothing talks to anything else. You are the integration layer.",
  },
  {
    number: "02",
    stat: "73%",
    statLabel: "time wasted",
    title: "The Content Treadmill",
    description:
      "You wake up, stare at a blank page, and somehow need to feed LinkedIn, email, Twitter, and a blog — all before lunch. Every single day.",
  },
  {
    number: "03",
    stat: "100%",
    statLabel: "generic",
    title: "Generic AI Slop",
    description:
      "ChatGPT doesn't know your ICPs. Doesn't understand your positioning. It generates content that sounds exactly like your competitors.",
  },
];

// Counter Animation Component
function AnimatedCounter({ target }: { target: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const hasAnimated = useRef(false);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!ref.current || hasAnimated.current) return;
    
    if (isReducedMotion) {
      ref.current.textContent = target;
      return;
    }

    const isPercent = target.includes("%");
    const hasPlus = target.includes("+");
    const numValue = parseInt(target.replace(/[^0-9]/g, ""), 10);

    const trigger = ScrollTrigger.create({
      trigger: ref.current,
      start: "top 85%",
      once: true,
      onEnter: () => {
        hasAnimated.current = true;
        const obj = { val: 0 };
        
        gsap.to(obj, {
          val: numValue,
          duration: 2,
          ease: "power2.out",
          onUpdate: () => {
            if (ref.current) {
              const suffix = hasPlus ? "+" : isPercent ? "%" : "";
              ref.current.textContent = Math.round(obj.val) + suffix;
            }
          },
        });
      },
    });

    return () => trigger.kill();
  }, [target, isReducedMotion]);

  return <span ref={ref}>0</span>;
}

export function ProblemSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      // Header animation with blur
      gsap.from(".problem-header", {
        scrollTrigger: {
          trigger: ".problem-header",
          start: "top 85%",
          toggleActions: "play none none none",
        },
        y: 50,
        opacity: 0,
        filter: "blur(10px)",
        duration: 1,
        ease: "power3.out",
        clearProps: "filter",
      });

      // Label fade
      gsap.from(".problem-label", {
        scrollTrigger: {
          trigger: ".problem-header",
          start: "top 85%",
          toggleActions: "play none none none",
        },
        y: 20,
        opacity: 0,
        duration: 0.6,
        delay: 0.2,
        ease: "power3.out",
      });

      // Cards 3D staggered reveal
      gsap.from(".problem-card", {
        scrollTrigger: {
          trigger: cardsRef.current,
          start: "top 80%",
          toggleActions: "play none none none",
        },
        y: 80,
        opacity: 0,
        rotateX: 15,
        duration: 0.9,
        stagger: 0.15,
        ease: "power3.out",
      });

      // Responsive animations with matchMedia (context7 best practice)
      const mm = gsap.matchMedia();
      
      mm.add("(min-width: 768px)", () => {
        // Desktop: enhanced hover effects
        const cards = sectionRef.current?.querySelectorAll(".problem-card");
        cards?.forEach((card) => {
          card.addEventListener("mouseenter", () => {
            gsap.to(card, {
              y: -10,
              scale: 1.02,
              rotateY: 5,
              duration: 0.35,
              ease: "power2.out",
            });
            gsap.to(card.querySelector(".problem-number"), {
              scale: 1.2,
              color: "rgba(255,255,255,0.5)",
              duration: 0.3,
            });
          });
          
          card.addEventListener("mouseleave", () => {
            gsap.to(card, {
              y: 0,
              scale: 1,
              rotateY: 0,
              duration: 0.35,
              ease: "power2.out",
            });
            gsap.to(card.querySelector(".problem-number"), {
              scale: 1,
              color: "rgba(255,255,255,0.2)",
              duration: 0.3,
            });
          });
        });
        
        return () => {
          // Cleanup
        };
      });

      mm.add("(max-width: 767px)", () => {
        // Mobile: simplified hover
        const cards = sectionRef.current?.querySelectorAll(".problem-card");
        cards?.forEach((card) => {
          card.addEventListener("mouseenter", () => {
            gsap.to(card, { y: -5, duration: 0.2 });
          });
          card.addEventListener("mouseleave", () => {
            gsap.to(card, { y: 0, duration: 0.2 });
          });
        });
        
        return () => {
          // Cleanup
        };
      });

      return () => mm.revert();
    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <section
      ref={sectionRef}
      className="relative py-32 px-6 bg-[var(--rf-charcoal)] overflow-hidden"
    >
      {/* Background texture */}
      <div className="absolute inset-0 pointer-events-none">
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `linear-gradient(var(--rf-ivory) 1px, transparent 1px), linear-gradient(90deg, var(--rf-ivory) 1px, transparent 1px)`,
            backgroundSize: "64px 64px",
          }}
        />
        {/* Subtle gradient orbs */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-white/[0.02] rounded-full blur-[120px]" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-white/[0.02] rounded-full blur-[100px]" />
      </div>

      <div className="max-w-[var(--shell-max-w)] mx-auto relative z-10">
        {/* Header */}
        <div className="problem-header text-center mb-20">
          <span className="problem-label rf-label text-white/40 tracking-[0.15em] mb-4 block">
            THE PROBLEM
          </span>
          <h2 className="text-[clamp(32px,5.5vw,52px)] font-bold text-[var(--rf-ivory)] leading-tight tracking-[-0.02em]">
            Marketing is broken
            <br />
            <span className="text-white/60">at the foundation.</span>
          </h2>
          <p className="mt-6 text-[17px] text-white/50 max-w-lg mx-auto leading-relaxed">
            You&rsquo;re not failing at marketing. You&rsquo;re drowning in a system designed to waste your time.
          </p>
        </div>

        {/* Cards grid with 3D perspective */}
        <div 
          ref={cardsRef}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto" 
          style={{ perspective: "1200px" }}
        >
          {PROBLEMS.map((problem, index) => (
            <div
              key={problem.number}
              className="problem-card group rounded-[var(--radius-lg)] border border-white/[0.08] bg-white/[0.03] p-8 hover:bg-white/[0.05] transition-colors duration-300 will-change-transform"
              style={{ transformStyle: "preserve-3d" }}
            >
              {/* Number tag with glow on hover */}
              <span className="problem-number text-[12px] font-mono text-white/20 tracking-wider transition-all duration-300 inline-block">
                {problem.number}
              </span>

              {/* Stat with animated counter */}
              <div className="mt-8 mb-6">
                <span className="text-[56px] font-bold text-[var(--rf-ivory)] leading-none font-mono tracking-tight">
                  <AnimatedCounter target={problem.stat} />
                </span>
                <span className="block text-[12px] text-white/40 font-mono tracking-wider mt-2 uppercase">
                  {problem.statLabel}
                </span>
              </div>

              {/* Content */}
              <h3 className="text-[22px] font-bold text-[var(--rf-ivory)] mb-4">
                {problem.title}
              </h3>
              <p className="text-[15px] text-white/50 leading-relaxed">
                {problem.description}
              </p>

              {/* Decorative line that animates on hover */}
              <div className="mt-6 h-px bg-white/[0.1] relative overflow-hidden">
                <div className="absolute inset-y-0 left-0 w-0 bg-white/30 group-hover:w-full transition-all duration-500" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
