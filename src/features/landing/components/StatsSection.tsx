"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLandingStore } from "./LandingClient";

const STATS = [
  { value: 21, suffix: "", label: "Steps to your full BCM" },
  { value: 6, suffix: "", label: "Integrated modules" },
  { value: 90, suffix: "", label: "Day campaign sieges" },
  { value: 100, suffix: "%", label: "Operator-controlled" },
];

function StatCounter({ value, suffix }: { value: number; suffix: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const hasAnimated = useRef(false);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!ref.current || hasAnimated.current) return;

    if (isReducedMotion) {
      ref.current.textContent = value + suffix;
      return;
    }

    const trigger = ScrollTrigger.create({
      trigger: ref.current,
      start: "top 85%",
      once: true,
      onEnter: () => {
        hasAnimated.current = true;
        const obj = { val: 0 };
        gsap.to(obj, {
          val: value,
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
  }, [value, suffix, isReducedMotion]);

  return <span ref={ref}>0{suffix}</span>;
}

export function StatsSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      gsap.from(".stat-item", {
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 80%",
          toggleActions: "play none none none",
        },
        y: 30,
        opacity: 0,
        duration: 0.7,
        stagger: 0.12,
        ease: "power3.out",
      });
    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <section id="stats" ref={sectionRef} className="py-24 px-6 bg-[var(--rf-charcoal)]">
      <div className="max-w-[var(--shell-max-w)] mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4">
          {STATS.map((stat, i) => (
            <div
              key={stat.label}
              className={`stat-item py-10 px-8 will-change-transform ${
                i < STATS.length - 1 ? "border-r border-white/10" : ""
              }`}
            >
              <div className="text-[clamp(52px,7vw,72px)] font-bold text-[var(--rf-ivory)] leading-none rf-mono tracking-tight">
                <StatCounter value={stat.value} suffix={stat.suffix} />
              </div>
              <p className="mt-4 text-[11px] font-semibold tracking-[0.1em] text-white/40 uppercase">
                {stat.label}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
