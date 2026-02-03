"use client";

import { useState } from "react";
import { MagneticButton } from "./MagneticButton";
import { TextReveal, WordReveal } from "./TextReveal";
import { LottieCompass, LottieSpinner } from "./LottieCompass";
import { FloatingElement, RotatingElement } from "./FloatingElements";
import { AnimatedCounter } from "./AnimatedCounter";
import { RevealOnScroll } from "./RevealOnScroll";

// Showcase component to display all animation effects
export function AnimationShowcase() {
  const [activeDemo, setActiveDemo] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] p-8">
      <h1 className="font-display text-4xl text-[var(--text-primary)] mb-12 text-center">
        Animation Showcase
      </h1>

      <div className="max-w-4xl mx-auto space-y-16">
        {/* Magnetic Buttons */}
        <section className="border border-[var(--border)] rounded-2xl p-8">
          <h2 className="font-display text-2xl text-[var(--text-primary)] mb-6">
            Magnetic Buttons
          </h2>
          <div className="flex gap-4 flex-wrap">
            <MagneticButton
              strength={0.3}
              className="px-6 py-3 bg-[var(--accent)] text-white rounded-full"
            >
              Hover Me (Strong)
            </MagneticButton>
            <MagneticButton
              strength={0.1}
              className="px-6 py-3 border border-[var(--accent)] text-[var(--accent)] rounded-full"
            >
              Hover Me (Gentle)
            </MagneticButton>
          </div>
        </section>

        {/* Text Reveal */}
        <section className="border border-[var(--border)] rounded-2xl p-8">
          <h2 className="font-display text-2xl text-[var(--text-primary)] mb-6">
            Text Reveal
          </h2>
          <div className="space-y-4">
            <TextReveal className="font-display text-3xl text-[var(--text-primary)]">
              Character by character
            </TextReveal>
            <WordReveal className="font-display text-3xl text-[var(--accent)]">
              Word by word animation
            </WordReveal>
          </div>
        </section>

        {/* Lottie Compass */}
        <section className="border border-[var(--border)] rounded-2xl p-8">
          <h2 className="font-display text-2xl text-[var(--text-primary)] mb-6">
            Animated Compass
          </h2>
          <div className="flex gap-8 items-center justify-center">
            <LottieCompass size={150} autoplay loop />
            <LottieSpinner size={60} />
          </div>
        </section>

        {/* Floating Elements */}
        <section className="border border-[var(--border)] rounded-2xl p-8">
          <h2 className="font-display text-2xl text-[var(--text-primary)] mb-6">
            Floating & Rotating
          </h2>
          <div className="flex gap-12 items-center justify-center h-32">
            <FloatingElement amplitude={20} duration={2}>
              <div className="w-16 h-16 bg-[var(--accent)] rounded-xl" />
            </FloatingElement>
            <RotatingElement duration={10}>
              <div className="w-16 h-16 border-2 border-[var(--accent)] rounded-full flex items-center justify-center">
                <div className="w-2 h-2 bg-[var(--accent)] rounded-full" />
              </div>
            </RotatingElement>
          </div>
        </section>

        {/* Animated Counter */}
        <section className="border border-[var(--border)] rounded-2xl p-8">
          <h2 className="font-display text-2xl text-[var(--text-primary)] mb-6">
            Animated Counter (Scroll to trigger)
          </h2>
          <div className="flex gap-8 justify-center">
            <div className="text-center">
              <AnimatedCounter
                end={5000}
                prefix="₹"
                className="font-display text-4xl text-[var(--text-primary)]"
              />
              <p className="text-sm text-[var(--text-muted)]">Price</p>
            </div>
            <div className="text-center">
              <AnimatedCounter
                end={100}
                suffix="+"
                className="font-display text-4xl text-[var(--accent)]"
              />
              <p className="text-sm text-[var(--text-muted)]">Features</p>
            </div>
          </div>
        </section>

        {/* Reveal Animations */}
        <section className="border border-[var(--border)] rounded-2xl p-8">
          <h2 className="font-display text-2xl text-[var(--text-primary)] mb-6">
            Scroll Reveals (Scroll to see)
          </h2>
          <div className="space-y-4">
            <RevealOnScroll animation="fadeUp">
              <div className="p-6 bg-[var(--bg-secondary)] rounded-xl text-center">
                Fade Up
              </div>
            </RevealOnScroll>
            <RevealOnScroll animation="fadeLeft">
              <div className="p-6 bg-[var(--bg-secondary)] rounded-xl text-center">
                Fade Left
              </div>
            </RevealOnScroll>
            <RevealOnScroll animation="scale">
              <div className="p-6 bg-[var(--bg-secondary)] rounded-xl text-center">
                Scale
              </div>
            </RevealOnScroll>
          </div>
        </section>
      </div>
    </div>
  );
}

export default AnimationShowcase;
