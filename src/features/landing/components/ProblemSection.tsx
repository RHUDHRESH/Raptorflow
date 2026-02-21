"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLandingStore } from "./LandingClient";

const PAIN_POINTS = [
  "12+ disconnected tools",
  "Context lost every meeting",
  "Brand voice drift",
  "Generic AI output",
  "Campaign silos",
  "Manual reporting",
  "Strategy in Notion, execution in Slack",
  "No single source of truth",
];

const PROBLEMS = [
  {
    number: "01",
    stat: "12",
    suffix: "+",
    statLabel: "tools juggled daily",
    title: "Tool Sprawl",
    description:
      "Your marketing stack is a dozen disconnected apps. Data lives in silos. Nothing talks to anything else. You are the integration layer.",
  },
  {
    number: "02",
    stat: "73",
    suffix: "%",
    statLabel: "of time wasted",
    title: "The Context Treadmill",
    description:
      "Every campaign brief starts from zero. Your positioning, your ICPs, your voice — repeated endlessly across tools that never remember.",
  },
  {
    number: "03",
    stat: "100",
    suffix: "%",
    statLabel: "sounds generic",
    title: "AI Without Context",
    description:
      "ChatGPT doesn't know your ICPs. Doesn't understand your positioning. It generates content that sounds exactly like your competitors.",
  },
];

function AnimatedCounter({ target, suffix }: { target: string; suffix: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const hasAnimated = useRef(false);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!ref.current || hasAnimated.current) return;

    if (isReducedMotion) {
      ref.current.textContent = target + suffix;
      return;
    }

    const numValue = parseInt(target, 10);

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
              ref.current.textContent = Math.round(obj.val) + suffix;
            }
          },
        });
      },
    });

    return () => trigger.kill();
  }, [target, suffix, isReducedMotion]);

  return <span ref={ref}>0{suffix}</span>;
}

export function ProblemSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const marqueeRowARef = useRef<HTMLDivElement>(null);
  const marqueeRowBRef = useRef<HTMLDivElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (isReducedMotion) return;

    const rowA = marqueeRowARef.current;
    const rowB = marqueeRowBRef.current;
    if (!rowA || !rowB) return;

    const widthA = rowA.scrollWidth / 2;
    const widthB = rowB.scrollWidth / 2;

    const tweenA = gsap.to(rowA, {
      x: `-=${widthA}`,
      duration: 28,
      ease: "none",
      repeat: -1,
      modifiers: {
        x: gsap.utils.unitize((x) => parseFloat(x) % widthA),
      },
    });

    const tweenB = gsap.to(rowB, {
      x: `+=${widthB}`,
      duration: 32,
      ease: "none",
      repeat: -1,
      modifiers: {
        x: gsap.utils.unitize((x) => parseFloat(x) % widthB),
      },
    });

    return () => {
      tweenA.kill();
      tweenB.kill();
    };
  }, [isReducedMotion]);

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      gsap.from(".problem-card", {
        scrollTrigger: {
          trigger: ".problem-cards-row",
          start: "top 78%",
          toggleActions: "play none none none",
        },
        y: 80,
        opacity: 0,
        rotateX: 8,
        duration: 0.9,
        stagger: 0.15,
        ease: "power3.out",
      });

      const mm = gsap.matchMedia();
      mm.add("(min-width: 768px)", () => {
        const cards = sectionRef.current?.querySelectorAll(".problem-card");
        cards?.forEach((card) => {
          card.addEventListener("mouseenter", () => {
            gsap.to(card, { y: -8, scale: 1.02, duration: 0.3, ease: "power2.out" });
          });
          card.addEventListener("mouseleave", () => {
            gsap.to(card, { y: 0, scale: 1, duration: 0.3, ease: "power2.out" });
          });
        });
        return () => {};
      });

      return () => mm.revert();
    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  const allPains = [...PAIN_POINTS, ...PAIN_POINTS];

  return (
    <section ref={sectionRef} className="bg-[var(--bg-canvas)]">
      <div className="py-10 overflow-hidden border-y border-[var(--border-1)]">
        <div className="relative">
          <div className="flex gap-3 mb-3 whitespace-nowrap">
            <div ref={marqueeRowARef} className="flex gap-3 flex-shrink-0">
              {allPains.map((pain, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--bg-surface)] border border-[var(--border-2)] rounded-[10px] text-[13px] font-medium text-[var(--ink-2)] whitespace-nowrap"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--border-2)]" />
                  {pain}
                </span>
              ))}
            </div>
          </div>
          <div className="flex gap-3 whitespace-nowrap">
            <div ref={marqueeRowBRef} className="flex gap-3 flex-shrink-0" style={{ transform: "translateX(-25%)" }}>
              {[...allPains].reverse().map((pain, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--bg-surface)] border border-[var(--border-2)] rounded-[10px] text-[13px] font-medium text-[var(--ink-2)] whitespace-nowrap"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--border-2)]" />
                  {pain}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="relative py-32 px-6 bg-[var(--rf-charcoal)] overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div
            className="absolute inset-0 opacity-[0.03]"
            style={{
              backgroundImage: `linear-gradient(var(--rf-ivory) 1px, transparent 1px), linear-gradient(90deg, var(--rf-ivory) 1px, transparent 1px)`,
              backgroundSize: "64px 64px",
            }}
          />
        </div>

        <div className="max-w-[var(--shell-max-w)] mx-auto relative z-10">
          <div className="text-center mb-20">
            <span className="rf-label text-white/40 tracking-[0.15em] mb-5 block">
              THE PROBLEM
            </span>
            <h2 className="text-[clamp(32px,5.5vw,52px)] font-bold text-[var(--rf-ivory)] leading-tight tracking-[-0.03em]">
              Marketing is broken
              <br />
              <span className="text-white/50">at the foundation.</span>
            </h2>
            <p className="mt-6 text-[17px] text-white/50 max-w-lg mx-auto leading-relaxed">
              You&rsquo;re not failing at marketing. You&rsquo;re drowning in a system designed to waste your time.
            </p>
          </div>

          <div
            className="problem-cards-row grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto"
            style={{ perspective: "1200px" }}
          >
            {PROBLEMS.map((problem) => (
              <div
                key={problem.number}
                className="problem-card group rounded-[var(--radius-md)] border border-white/[0.08] bg-white/[0.03] p-10 will-change-transform"
              >
                <span className="text-[11px] font-mono text-white/25 tracking-wider">
                  {problem.number}
                </span>

                <div className="mt-8 mb-6">
                  <span className="text-[56px] font-bold text-[var(--rf-ivory)] leading-none rf-mono tracking-tight">
                    <AnimatedCounter target={problem.stat} suffix={problem.suffix} />
                  </span>
                  <span className="block text-[11px] text-white/40 font-mono tracking-wider mt-2 uppercase">
                    {problem.statLabel}
                  </span>
                </div>

                <h3 className="text-[22px] font-bold text-[var(--rf-ivory)] mb-4">
                  {problem.title}
                </h3>
                <p className="text-[15px] text-white/50 leading-relaxed">
                  {problem.description}
                </p>

                <div className="mt-8 h-px bg-white/[0.1] relative overflow-hidden">
                  <div className="absolute inset-y-0 left-0 w-0 bg-white/25 group-hover:w-full transition-all duration-700" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
