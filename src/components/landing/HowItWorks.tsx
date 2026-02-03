"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { CompassLogo } from "@/components/compass/CompassLogo";

gsap.registerPlugin(ScrollTrigger);

const STEPS = [
  {
    number: "01",
    title: "Onboard",
    description:
      "Share your business context. Our AI absorbs your positioning, ICP, and competitive landscape to understand your unique situation.",
    details: ["Business context capture", "ICP definition", "Competitive analysis"],
  },
  {
    number: "02",
    title: "Generate BCM",
    description:
      "The Cognitive Engine creates your Business Context Manifest—a living document that captures your strategy and guides all marketing decisions.",
    details: ["AI-powered analysis", "Strategic framework", "Continuous refinement"],
  },
  {
    number: "03",
    title: "Execute Moves",
    description:
      "Deploy weekly marketing moves and campaigns. Muse generates content, tracks performance, and learns from results to improve over time.",
    details: ["Weekly execution", "AI content generation", "Performance tracking"],
  },
];

export function HowItWorks() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const timelineRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!timelineRef.current) return;

    const steps = timelineRef.current.querySelectorAll(".timeline-step");
    const line = timelineRef.current.querySelector(".timeline-line");

    const ctx = gsap.context(() => {
      // Animate the connecting line
      if (line) {
        gsap.fromTo(
          line,
          { scaleY: 0, transformOrigin: "top" },
          {
            scaleY: 1,
            duration: 1.5,
            ease: "power2.out",
            scrollTrigger: {
              trigger: timelineRef.current,
              start: "top 70%",
              toggleActions: "play none none reverse",
            },
          }
        );
      }

      // Animate each step
      steps.forEach((step, index) => {
        const isEven = index % 2 === 0;

        gsap.fromTo(
          step,
          {
            x: isEven ? -40 : 40,
            opacity: 0,
          },
          {
            x: 0,
            opacity: 1,
            duration: 0.8,
            ease: "power3.out",
            scrollTrigger: {
              trigger: step,
              start: "top 80%",
              toggleActions: "play none none reverse",
            },
          }
        );

        // Animate the compass marker
        const marker = step.querySelector(".step-marker");
        if (marker) {
          gsap.fromTo(
            marker,
            { scale: 0, rotation: -180 },
            {
              scale: 1,
              rotation: 0,
              duration: 0.6,
              ease: "back.out(1.7)",
              scrollTrigger: {
                trigger: step,
                start: "top 80%",
                toggleActions: "play none none reverse",
              },
              delay: 0.2,
            }
          );
        }
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      id="how-it-works"
      ref={sectionRef}
      className="relative py-32 bg-[var(--bg-secondary)]"
    >
      <div className="max-w-6xl mx-auto px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-20">
          <span className="inline-block px-4 py-1.5 bg-[var(--bg-primary)] border border-[var(--border)] rounded-full text-xs font-semibold tracking-widest uppercase text-[var(--accent)] mb-6">
            The Journey
          </span>
          <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-semibold text-[var(--text-primary)] mb-6">
            How It <span className="text-[var(--accent)]">Works</span>
          </h2>
          <p className="text-lg text-[var(--text-secondary)] max-w-2xl mx-auto">
            From onboarding to execution in three simple steps. Let the compass
            guide your marketing journey.
          </p>
        </div>

        {/* Timeline */}
        <div ref={timelineRef} className="relative">
          {/* Connecting Line */}
          <div className="timeline-line absolute left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-[var(--accent)] via-[var(--border-strong)] to-[var(--border)] hidden md:block" />

          {/* Mobile Line */}
          <div className="absolute left-8 top-0 bottom-0 w-px bg-gradient-to-b from-[var(--accent)] via-[var(--border-strong)] to-[var(--border)] md:hidden" />

          {/* Steps */}
          <div className="space-y-16 md:space-y-24">
            {STEPS.map((step, index) => {
              const isEven = index % 2 === 0;

              return (
                <div
                  key={index}
                  className={`timeline-step relative flex items-center gap-8 md:gap-0 ${
                    isEven ? "md:flex-row" : "md:flex-row-reverse"
                  }`}
                >
                  {/* Content */}
                  <div
                    className={`flex-1 md:px-16 ${
                      isEven ? "md:text-right" : "md:text-left"
                    }`}
                  >
                    <div
                      className={`bg-[var(--bg-primary)] border border-[var(--border)] rounded-2xl p-8 hover:border-[var(--accent)] transition-colors ${
                        isEven ? "md:ml-auto" : "md:mr-auto"
                      } max-w-md`}
                    >
                      <span className="font-display text-5xl font-semibold text-[var(--accent)]/20">
                        {step.number}
                      </span>
                      <h3 className="font-display text-2xl font-semibold text-[var(--text-primary)] mt-2 mb-4">
                        {step.title}
                      </h3>
                      <p className="text-[var(--text-secondary)] mb-6 leading-relaxed">
                        {step.description}
                      </p>
                      <ul
                        className={`space-y-2 ${
                          isEven ? "md:ml-auto" : ""
                        } inline-block`}
                      >
                        {step.details.map((detail, i) => (
                          <li
                            key={i}
                            className={`flex items-center gap-2 text-sm text-[var(--text-muted)] ${
                              isEven ? "md:flex-row-reverse" : ""
                            }`}
                          >
                            <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)]" />
                            {detail}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Center Marker */}
                  <div className="step-marker absolute left-8 md:left-1/2 -translate-x-1/2 z-10">
                    <div className="w-16 h-16 bg-[var(--bg-primary)] border-2 border-[var(--accent)] rounded-full flex items-center justify-center shadow-lg">
                      <CompassLogo size={32} variant="mark" animate={false} />
                    </div>
                  </div>

                  {/* Empty space for alternating layout */}
                  <div className="flex-1 hidden md:block" />
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}

export default HowItWorks;
