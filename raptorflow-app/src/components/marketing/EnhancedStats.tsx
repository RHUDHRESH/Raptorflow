'use client';

import { motion, useInView } from 'framer-motion';
import { useRef, useEffect, useState } from 'react';
import { GlassmorphismCard } from '@/components/ui/GlassmorphismCard';
import { cn } from '@/lib/utils';

interface Stat {
  value: number;
  suffix: string;
  label: string;
  prefix?: string;
  color: string;
}

const stats: Stat[] = [
  {
    value: 10,
    suffix: 'min',
    label: 'to build your 90-day plan',
    color: 'from-blue-500 to-purple-500',
  },
  {
    value: 1,
    suffix: 'system',
    label: 'instead of 5+ tools',
    color: 'from-green-500 to-emerald-500',
  },
  {
    value: 7,
    suffix: 'moves',
    label: 'shipped every week',
    color: 'from-orange-500 to-red-500',
  },
  {
    value: 90,
    suffix: '%',
    label: 'more clarity in positioning',
    color: 'from-pink-500 to-rose-500',
  },
];

function AnimatedNumber({
  value,
  duration = 2,
}: {
  value: number;
  duration?: number;
}) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (!isInView) return;

    let start = 0;
    const end = value;
    const increment = end / (duration * 60); // 60 fps

    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, 1000 / 60);

    return () => clearInterval(timer);
  }, [isInView, value, duration]);

  return <span ref={ref}>{count}</span>;
}

export function EnhancedStats() {
  return (
    <section className="py-32 lg:py-40 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-muted/20 to-background -z-10" />

      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <motion.div
          className="text-center mb-20"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground mb-4">
            By The Numbers
          </p>
          <h2 className="font-display text-5xl lg:text-6xl font-medium tracking-tight">
            The RaptorFlow Effect
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
            >
              <GlassmorphismCard className="p-8 h-full" data-magnetic>
                {/* Progress circle */}
                <div className="relative w-32 h-32 mx-auto mb-6">
                  <svg
                    className="w-full h-full -rotate-90"
                    viewBox="0 0 100 100"
                  >
                    {/* Background circle */}
                    <circle
                      cx="50"
                      cy="50"
                      r="45"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="8"
                      className="text-muted/20"
                    />
                    {/* Animated progress circle */}
                    <motion.circle
                      cx="50"
                      cy="50"
                      r="45"
                      fill="none"
                      stroke="url(#gradient-${index})"
                      strokeWidth="8"
                      strokeLinecap="round"
                      initial={{ pathLength: 0 }}
                      whileInView={{ pathLength: 0.75 }}
                      viewport={{ once: true }}
                      transition={{ duration: 2, delay: index * 0.1 }}
                      style={{
                        strokeDasharray: '283',
                      }}
                    />
                    <defs>
                      <linearGradient
                        id={`gradient-${index}`}
                        x1="0%"
                        y1="0%"
                        x2="100%"
                        y2="100%"
                      >
                        <stop
                          offset="0%"
                          className={cn(
                            'text-opacity-100',
                            stat.color.split(' ')[0]
                          )}
                        />
                        <stop
                          offset="100%"
                          className={cn(
                            'text-opacity-100',
                            stat.color.split(' ')[2]
                          )}
                        />
                      </linearGradient>
                    </defs>
                  </svg>

                  {/* Number in center */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <div className="font-display text-4xl font-bold">
                        <AnimatedNumber value={stat.value} />
                      </div>
                      <div className="text-xs text-muted-foreground font-medium">
                        {stat.suffix}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Label */}
                <p className="text-center text-sm text-muted-foreground leading-relaxed">
                  {stat.label}
                </p>
              </GlassmorphismCard>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
