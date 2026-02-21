/**
 * ENHANCED WITH:
 * - context7: GSAP force3D optimization, will-change best practices
 * - frontend-animations: Elastic number counting, staggered reveals
 * - magicui: NumberTicker-inspired effects
 * - performance-optimization: once: true triggers, GPU acceleration
 */

"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLandingStore } from "./LandingClient";

const STATS = [
  { value: 21, suffix: "", label: "Onboarding steps to build your BCM" },
  { value: 5, suffix: "", label: "Move categories for every situation" },
  { value: 90, suffix: "-day", label: "Campaign sieges for market ownership" },
  { value: 100, suffix: "%", label: "Reversible — every decision, always" },
];

// Animated counter with elastic effect
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
          duration: 2.2,
          ease: "power2.out",
          onUpdate: () => {
            if (ref.current) {
              ref.current.textContent = Math.round(obj.val) + suffix;
            }
          },
        });

        // Elastic scale effect when done
        gsap.fromTo(ref.current, 
          { scale: 1 },
          { 
            scale: 1.1, 
            duration: 0.3, 
            delay: 2.2,
            ease: "back.out(2)",
            yoyo: true,
            repeat: 1,
          }
        );
      },
    });

    return () => trigger.kill();
  }, [value, suffix, isReducedMotion]);

  return <span ref={ref} className="inline-block will-change-transform">0{suffix}</span>;
}

export function StatsSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      // Stats grid entrance with stagger
      gsap.from(".stat-item", {
        scrollTrigger: {
          trigger: ".stats-grid",
          start: "top 80%",
          toggleActions: "play none none none",
        },
        y: 50,
        opacity: 0,
        scale: 0.9,
        duration: 0.8,
        stagger: 0.12,
        ease: "power3.out",
      });

      // Hover effects with matchMedia
      const mm = gsap.matchMedia();
      
      mm.add("(min-width: 768px)", () => {
        const items = sectionRef.current?.querySelectorAll(".stat-item");
        items?.forEach((item) => {
          const valueEl = item.querySelector(".stat-value");
          
          item.addEventListener("mouseenter", () => {
            gsap.to(item, { 
              y: -8, 
              scale: 1.03, 
              duration: 0.3, 
              ease: "power2.out" 
            });
            gsap.to(valueEl, { 
              scale: 1.1, 
              color: "var(--rf-charcoal)",
              duration: 0.3 
            });
          });
          
          item.addEventListener("mouseleave", () => {
            gsap.to(item, { 
              y: 0, 
              scale: 1, 
              duration: 0.3, 
              ease: "power2.out" 
            });
            gsap.to(valueEl, { 
              scale: 1, 
              color: "var(--ink-1)",
              duration: 0.3 
            });
          });
        });
        
        return;
      });

      return () => mm.revert();
    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <section ref={sectionRef} className="py-28 px-6 bg-[var(--bg-canvas)] relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[var(--rf-charcoal)]/[0.02] rounded-full blur-[100px]" />
      </div>

      <div className="max-w-[var(--shell-max-w)] mx-auto relative z-10">
        <div className="stats-grid grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
          {STATS.map((stat, index) => (
            <div 
              key={stat.label} 
              className="stat-item text-center p-6 rounded-[var(--radius-md)] hover:bg-[var(--bg-surface)] transition-colors duration-300 cursor-pointer will-change-transform"
            >
              <div className="flex items-baseline justify-center gap-0.5 mb-3">
                <span className="stat-value text-[52px] font-bold text-[var(--ink-1)] leading-none font-mono tracking-tighter">
                  <StatCounter value={stat.value} suffix={stat.suffix} />
                </span>
              </div>
              <p className="text-[13px] text-[var(--ink-2)] leading-snug font-medium">
                {stat.label}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
