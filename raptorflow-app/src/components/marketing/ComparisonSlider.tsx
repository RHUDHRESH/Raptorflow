'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface Comparison {
  before: {
    title: string;
    items: string[];
  };
  after: {
    title: string;
    items: string[];
  };
}

const comparison: Comparison = {
  before: {
    title: 'Without RaptorFlow',
    items: [
      '5+ disconnected tools',
      'Random tactics, no strategy',
      'Unclear messaging',
      'Marketing resets every Monday',
      'Guessing what works',
      'Scattered efforts',
    ],
  },
  after: {
    title: 'With RaptorFlow',
    items: [
      'One unified system',
      'Strategic 90-day plans',
      'Crystal-clear positioning',
      'Compounding weekly progress',
      'Data-driven decisions',
      'Focused execution',
    ],
  },
};

export function ComparisonSlider() {
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isDragging, setIsDragging] = useState(false);

  const handleMove = (e: React.MouseEvent<HTMLDivElement> | React.TouchEvent<HTMLDivElement>) => {
    if (!isDragging && e.type !== 'click') return;

    const rect = e.currentTarget.getBoundingClientRect();
    const x = 'touches' in e ? e.touches[0].clientX : e.clientX;
    const position = ((x - rect.left) / rect.width) * 100;
    setSliderPosition(Math.max(0, Math.min(100, position)));
  };

  return (
    <section className="py-32 lg:py-40 border-y border-border bg-muted/20">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground mb-4">
            The Difference
          </p>
          <h2 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
            Before & After
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Drag the slider to see the transformation
          </p>
        </motion.div>

        <motion.div
          className="relative max-w-5xl mx-auto"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
        >
          <div
            className="relative select-none overflow-hidden rounded-3xl border-2 border-border bg-background"
            onMouseDown={() => setIsDragging(true)}
            onMouseUp={() => setIsDragging(false)}
            onMouseLeave={() => setIsDragging(false)}
            onMouseMove={handleMove}
            onTouchStart={() => setIsDragging(true)}
            onTouchEnd={() => setIsDragging(false)}
            onTouchMove={handleMove}
            onClick={handleMove}
          >
            {/* Before Side */}
            <div className="grid md:grid-cols-2 gap-0">
              <div className="p-12 border-r border-border bg-destructive/5">
                <h3 className="font-display text-3xl font-medium mb-8 text-destructive">
                  {comparison.before.title}
                </h3>
                <ul className="space-y-4">
                  {comparison.before.items.map((item, i) => (
                    <motion.li
                      key={i}
                      className="flex items-start gap-3"
                      initial={{ opacity: 0, x: -20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: i * 0.1 }}
                    >
                      <span className="text-destructive mt-1">✗</span>
                      <span className="text-muted-foreground">{item}</span>
                    </motion.li>
                  ))}
                </ul>
              </div>

              {/* After Side */}
              <div
                className="p-12 bg-green-500/5"
                style={{
                  clipPath: `inset(0 ${100 - sliderPosition}% 0 0)`,
                }}
              >
                <h3 className="font-display text-3xl font-medium mb-8 text-green-600">
                  {comparison.after.title}
                </h3>
                <ul className="space-y-4">
                  {comparison.after.items.map((item, i) => (
                    <motion.li
                      key={i}
                      className="flex items-start gap-3"
                      initial={{ opacity: 0, x: 20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: i * 0.1 }}
                    >
                      <span className="text-green-600 mt-1">✓</span>
                      <span className="font-medium">{item}</span>
                    </motion.li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Slider */}
            <div
              className="absolute inset-y-0 w-1 bg-foreground cursor-ew-resize z-10"
              style={{ left: `${sliderPosition}%` }}
            >
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-foreground shadow-lg flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-background"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 9l4-4 4 4m0 6l-4 4-4-4"
                  />
                </svg>
              </div>
            </div>
          </div>

          <p className="text-center mt-6 text-sm text-muted-foreground">
            ← Drag the slider to compare →
          </p>
        </motion.div>
      </div>
    </section>
  );
}
