"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ArrowRight } from "lucide-react";
import { CompassLogo } from "@/components/compass/CompassLogo";

gsap.registerPlugin(ScrollTrigger);

export function FinalCTA() {
  const router = useRouter();
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sectionRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".cta-content",
        { y: 40, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.8,
          ease: "power3.out",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 70%",
            toggleActions: "play none none reverse",
          },
        }
      );
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative py-32 bg-[var(--bg-primary)] overflow-hidden"
    >
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23967553' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}
        />
      </div>

      {/* Gradient overlays */}
      <div className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-[var(--bg-primary)] to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[var(--bg-primary)] to-transparent" />

      <div className="cta-content relative z-10 max-w-4xl mx-auto px-6 text-center">
        {/* Compass Icon */}
        <div className="flex justify-center mb-8">
          <CompassLogo size={80} variant="minimal" animate={false} />
        </div>

        <h2 className="font-display text-4xl md:text-5xl lg:text-6xl font-semibold text-[var(--text-primary)] mb-6">
          Ready to Find Your
          <br />
          <span className="text-[var(--accent)]">True North?</span>
        </h2>

        <p className="text-lg text-[var(--text-secondary)] max-w-2xl mx-auto mb-10">
          Join founders who are navigating their marketing with precision.
          Start your free trial today—no credit card required.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={() => router.push("/signup")}
            className="group magnetic-button px-8 py-4 bg-[var(--accent)] text-white font-medium rounded-full hover:bg-[var(--accent-dark)] transition-all flex items-center gap-2"
          >
            Start Free Trial
            <ArrowRight
              size={18}
              className="group-hover:translate-x-1 transition-transform"
            />
          </button>
          <button
            onClick={() => router.push("/pricing")}
            className="px-8 py-4 border border-[var(--border-strong)] text-[var(--text-primary)] font-medium rounded-full hover:bg-[var(--bg-secondary)] transition-all"
          >
            View Pricing
          </button>
        </div>

        <p className="mt-8 text-sm text-[var(--text-muted)]">
          Trusted by founders building the future.
        </p>
      </div>
    </section>
  );
}

export default FinalCTA;
