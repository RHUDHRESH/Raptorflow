'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface Testimonial {
  quote: string;
  author: string;
  role: string;
  company: string;
  avatar?: string;
}

const testimonials: Testimonial[] = [
  {
    quote: "RaptorFlow transformed how we think about marketing. We went from scattered tactics to a real system in weeks.",
    author: "Sarah Chen",
    role: "Founder",
    company: "TechStart Inc",
  },
  {
    quote: "Finally, a marketing tool that actually helps founders ship. The AI positioning is scary good.",
    author: "Marcus Rodriguez",
    role: "CEO",
    company: "GrowthLab",
  },
  {
    quote: "We've tried every marketing tool. This is the first one that gave us clarity instead of more chaos.",
    author: "Emily Watson",
    role: "Head of Marketing",
    company: "Innovate Co",
  },
];

export function TestimonialCarousel() {
  const [current, setCurrent] = useState(0);

  const next = () => setCurrent((prev) => (prev + 1) % testimonials.length);
  const prev = () =>
    setCurrent((prev) => (prev - 1 + testimonials.length) % testimonials.length);

  return (
    <section className="py-32 lg:py-40 relative overflow-hidden border-y border-border">
      {/* Background */}
      <div className="absolute inset-0 bg-muted/20" />
      
      <div className="mx-auto max-w-5xl px-6 lg:px-8 relative z-10">
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground mb-4">
            Testimonials
          </p>
          <h2 className="font-display text-4xl lg:text-5xl font-medium tracking-tight">
            Loved by founders
          </h2>
        </motion.div>

        <div className="relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={current}
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -100 }}
              transition={{ duration: 0.5, ease: 'easeInOut' }}
              className="text-center"
            >
              <blockquote className="mb-8">
                <p className="font-display text-2xl lg:text-4xl font-medium leading-relaxed mb-8">
                  "{testimonials[current].quote}"
                </p>
              </blockquote>

              <div className="flex flex-col items-center gap-2">
                {testimonials[current].avatar && (
                  <div className="w-16 h-16 rounded-full bg-muted mb-2 overflow-hidden">
                    <img
                      src={testimonials[current].avatar}
                      alt={testimonials[current].author}
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
                <div>
                  <p className="font-semibold text-lg">
                    {testimonials[current].author}
                  </p>
                  <p className="text-muted-foreground text-sm">
                    {testimonials[current].role} at {testimonials[current].company}
                  </p>
                </div>
              </div>
            </motion.div>
          </AnimatePresence>

          {/* Navigation */}
          <div className="flex items-center justify-center gap-4 mt-12">
            <Button
              variant="outline"
              size="icon"
              onClick={prev}
              className="rounded-full"
              data-magnetic
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>

            {/* Dots */}
            <div className="flex gap-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrent(index)}
                  className={cn(
                    'w-2 h-2 rounded-full transition-all duration-300',
                    current === index
                      ? 'bg-foreground w-8'
                      : 'bg-muted-foreground/30'
                  )}
                />
              ))}
            </div>

            <Button
              variant="outline"
              size="icon"
              onClick={next}
              className="rounded-full"
              data-magnetic
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}