'use client';

import { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { GlassmorphismCard } from '@/components/ui/GlassmorphismCard';
import { SplitText } from '@/components/ui/SplitText';

const features = [
  {
    title: 'Foundation',
    description: 'Define your market, positioning, and core messaging',
    icon: '🎯',
  },
  {
    title: 'Cohorts',
    description: 'Organize your ICPs into actionable segments',
    icon: '👥',
  },
  {
    title: 'Campaigns',
    description: 'Build 90-day strategic marketing war plans',
    icon: '📋',
  },
  {
    title: 'Moves',
    description: 'Execute weekly tasks that compound over time',
    icon: '🚀',
  },
  {
    title: 'Muse',
    description: 'AI-powered content and asset generation',
    icon: '✨',
  },
  {
    title: 'Radar',
    description: 'Track performance and optimize your strategy',
    icon: '📊',
  },
];

export function ParallaxShowcase() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start'],
  });

  const y = useTransform(scrollYProgress, [0, 1], ['0%', '20%']);
  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0]);

  return (
    <section ref={ref} className="py-32 lg:py-40 relative overflow-hidden">
      {/* Parallax Background */}
      <motion.div
        className="absolute inset-0 -z-10"
        style={{ y }}
      >
        <div className="absolute top-0 left-1/4 w-96 h-96 rounded-full bg-foreground/5 blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 rounded-full bg-muted-foreground/5 blur-3xl" />
      </motion.div>

      <motion.div
        className="mx-auto max-w-7xl px-6 lg:px-8"
        style={{ opacity }}
      >
        {/* Header */}
        <div className="text-center mb-20">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground mb-4">
            The Complete System
          </p>
          <h2 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
            <SplitText animation="blur">
              Six modules. One flow.
            </SplitText>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Every piece of RaptorFlow connects to create a marketing machine that compounds.
          </p>
        </div>

        {/* Feature Grid with Parallax */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const yOffset = useTransform(
              scrollYProgress,
              [0, 1],
              [0, (index % 2 === 0 ? -50 : 50)]
            );

            return (
              <motion.div
                key={feature.title}
                style={{ y: yOffset }}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-10%' }}
                transition={{ delay: index * 0.1, duration: 0.6 }}
              >
                <GlassmorphismCard
                  className="p-8 h-full hover:scale-105 transition-transform duration-300"
                  data-magnetic
                  data-cursor-text={feature.title}
                >
                  {/* Icon */}
                  <div className="text-6xl mb-6">{feature.icon}</div>

                  {/* Title */}
                  <h3 className="font-display text-2xl font-semibold mb-3">
                    {feature.title}
                  </h3>

                  {/* Description */}
                  <p className="text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>

                  {/* Decorative line */}
                  <div className="mt-6 h-1 w-12 bg-gradient-to-r from-foreground to-transparent rounded-full" />
                </GlassmorphismCard>
              </motion.div>
            );
          })}
        </div>
      </motion.div>
    </section>
  );
}
