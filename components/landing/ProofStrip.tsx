"use client";

import { useEffect, useRef } from "react";

/**
 * ProofStrip Section - Social Proof
 *
 * Minimal, elegant display of credibility signals:
 * - Logo parade (company logos or badges)
 * - Key metrics
 * - Trust indicators
 */

const stats = [
  { value: "500+", label: "Founders" },
  { value: "2.5K", label: "Strategies Generated" },
  { value: "89%", label: "Time Saved" },
  { value: "4.9", label: "Rating" },
];

const testimonialSnippet = {
  quote: "RaptorFlow turned my random marketing efforts into a systematic growth engine. I went from posting sporadically to having a clear, executable strategy.",
  author: "Sarah Chen",
  role: "Founder, TechStartup",
};

export function ProofStrip() {
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
      className="section-md bg-subtle relative"
    >
      <div className="container-editorial">
        {/* Stats row */}
        <div className="reveal grid grid-cols-2 md:grid-cols-4 gap-8 lg:gap-16 mb-20">
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-display-lg text-primary mb-2 font-mono">
                {stat.value}
              </div>
              <div className="text-label text-muted">
                {stat.label}
              </div>
            </div>
          ))}
        </div>

        {/* Divider */}
        <div className="divider-hairline mb-20" />

        {/* Featured testimonial */}
        <div className="reveal max-w-3xl mx-auto text-center">
          <blockquote className="text-display-md text-secondary italic mb-8 leading-relaxed">
            &ldquo;{testimonialSnippet.quote}&rdquo;
          </blockquote>
          <div className="flex items-center justify-center gap-4">
            {/* Avatar placeholder */}
            <div className="w-12 h-12 rounded-full bg-muted-custom flex items-center justify-center text-label text-tertiary">
              {testimonialSnippet.author.split(" ").map((n) => n[0]).join("")}
            </div>
            <div className="text-left">
              <div className="text-body-md text-primary font-medium">
                {testimonialSnippet.author}
              </div>
              <div className="text-body-sm text-muted">
                {testimonialSnippet.role}
              </div>
            </div>
          </div>
        </div>

        {/* Trust badges / logos placeholder */}
        <div className="reveal mt-20 pt-16 border-t border-hairline">
          <p className="text-center text-label text-muted mb-8">
            Built with tools you already use
          </p>
          <div className="flex flex-wrap items-center justify-center gap-8 lg:gap-12 opacity-40">
            {/* Logo placeholders - would be actual brand logos */}
            {["OpenAI", "Notion", "Slack", "Linear", "Figma", "Stripe"].map((brand) => (
              <div
                key={brand}
                className="h-8 flex items-center justify-center text-body-md font-medium text-tertiary"
              >
                {brand}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
