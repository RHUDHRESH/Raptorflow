"use client";

import React from "react";
import Link from "next/link";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { ArrowRight } from "lucide-react";
import { MagneticButton } from "../effects/MagneticButton";
import { GradientOrb } from "../effects/GradientOrb";

// ═══════════════════════════════════════════════════════════════
// Final CTA - Powerful call to action at bottom of page
// ═══════════════════════════════════════════════════════════════

export function FinalCTA() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} className="py-32 md:py-40 relative overflow-hidden">
      {/* Background Effects */}
      <GradientOrb color="coral" size="xl" className="-bottom-48 -left-48" />
      <GradientOrb color="ocean" size="lg" className="top-0 right-0" />

      <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
        >
          {/* Headline */}
          <h2 className="text-4xl md:text-6xl lg:text-7xl font-editorial leading-[1.1] mb-6">
            Ready to stop posting
            <br />
            <span className="text-[var(--muted)]">and start building?</span>
          </h2>

          {/* Subtext */}
          <p className="text-xl text-[var(--secondary)] mb-10 max-w-2xl mx-auto">
            Join 500+ founders who have transformed their marketing from a time drain into a growth engine.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <MagneticButton className="group inline-flex items-center justify-center gap-2 px-8 py-4 bg-[var(--ink)] text-[var(--canvas)] text-lg font-medium rounded-xl hover:opacity-90 transition-all">
              <Link href="/signup" className="flex items-center gap-2">
                Start your free trial
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
            </MagneticButton>

            <Link
              href="/signin"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 border border-[var(--border)] text-[var(--ink)] text-lg font-medium rounded-xl hover:border-[var(--ink)] transition-colors"
            >
              Already a member? Log in
            </Link>
          </div>

          {/* Trust Note */}
          <p className="mt-8 text-sm text-[var(--muted)]">
            14-day free trial. No credit card required. Cancel anytime.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
