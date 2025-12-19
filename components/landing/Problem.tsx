"use client";

import { useEffect, useRef } from "react";
import { AlertCircle, Clock, Shuffle, TrendingDown } from "lucide-react";

/**
 * Problem Section - Editorial Layout
 *
 * Articulates the pain points founders face with:
 * - Clean magazine-style grid layout
 * - Monochrome iconography
 * - Strong typographic hierarchy
 */

const problems = [
  {
    icon: Shuffle,
    title: "Strategy Chaos",
    description: "Jumping between tactics without a cohesive plan. Every day feels like starting over.",
  },
  {
    icon: Clock,
    title: "Time Drain",
    description: "Hours lost researching, planning, and second-guessing. Marketing becomes a full-time distraction.",
  },
  {
    icon: TrendingDown,
    title: "Invisible Results",
    description: "Effort without outcomes. No clear connection between activities and growth.",
  },
  {
    icon: AlertCircle,
    title: "Expert Gap",
    description: "Can't afford a CMO. Free advice is generic. Paid consultants cost more than results deliver.",
  },
];

export function Problem() {
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("revealed");
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -10% 0px" }
    );

    const revealElements = sectionRef.current?.querySelectorAll(".reveal");
    revealElements?.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={sectionRef}
      id="problem"
      className="section-lg bg-subtle relative"
    >
      <div className="container-editorial">
        {/* Section header */}
        <div className="max-w-2xl mx-auto text-center mb-20">
          <span className="reveal text-label text-muted mb-4 block">
            The Problem
          </span>
          <h2 className="reveal stagger-1 text-display-xl text-primary mb-6">
            Marketing shouldn&apos;t feel like gambling
          </h2>
          <p className="reveal stagger-2 text-body-lg text-secondary">
            Most founders treat marketing as an afterthought or an endless experiment.
            Neither approach scales.
          </p>
        </div>

        {/* Problem grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-12">
          {problems.map((problem, index) => (
            <div
              key={problem.title}
              className={`reveal stagger-${index + 1} group p-8 lg:p-10 rounded-2xl bg-base border border-hairline hover-lift`}
            >
              {/* Icon */}
              <div className="w-12 h-12 rounded-xl bg-subtle flex items-center justify-center mb-6 transition-colors duration-200 group-hover:bg-muted-custom">
                <problem.icon className="w-6 h-6 text-tertiary" strokeWidth={1.5} />
              </div>

              {/* Content */}
              <h3 className="text-display-sm text-primary mb-3">
                {problem.title}
              </h3>
              <p className="text-body-md text-tertiary leading-relaxed">
                {problem.description}
              </p>
            </div>
          ))}
        </div>

        {/* Transition statement */}
        <div className="reveal mt-20 text-center">
          <p className="text-body-xl text-secondary italic font-display max-w-xl mx-auto">
            &ldquo;What if marketing felt less like chaos and more like chess?&rdquo;
          </p>
        </div>
      </div>
    </section>
  );
}
