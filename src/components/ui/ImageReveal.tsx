'use client';

import { motion, useInView } from 'framer-motion';
import { useRef, ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface ImageRevealProps {
  children: ReactNode;
  className?: string;
  direction?: 'up' | 'down' | 'left' | 'right';
  delay?: number;
}

export function ImageReveal({
  children,
  className,
  direction = 'up',
  delay = 0,
}: ImageRevealProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-10%' });

  const directionOffset = {
    up: { y: 100 },
    down: { y: -100 },
    left: { x: 100 },
    right: { x: -100 },
  };

  return (
    <div ref={ref} className={cn('relative overflow-hidden', className)}>
      {/* Reveal overlay */}
      <motion.div
        className="absolute inset-0 bg-foreground z-10"
        initial={{ scaleX: 1 }}
        animate={isInView ? { scaleX: 0 } : {}}
        transition={{
          duration: 1,
          delay: delay,
          ease: [0.76, 0, 0.24, 1],
        }}
        style={{
          originX: direction === 'left' ? 0 : 1,
          originY: direction === 'up' ? 1 : 0,
        }}
      />

      {/* Image content */}
      <motion.div
        initial={{ ...directionOffset[direction], scale: 1.2 }}
        animate={isInView ? { x: 0, y: 0, scale: 1 } : {}}
        transition={{
          duration: 1,
          delay: delay + 0.1,
          ease: [0.76, 0, 0.24, 1],
        }}
      >
        {children}
      </motion.div>
    </div>
  );
}
