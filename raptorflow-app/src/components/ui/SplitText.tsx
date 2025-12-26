'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { ReactNode } from 'react';

interface SplitTextProps {
  children: string;
  className?: string;
  delay?: number;
  staggerDelay?: number;
  animation?: 'fade-up' | 'blur' | 'rotate' | 'scale';
}

export function SplitText({
  children,
  className,
  delay = 0,
  staggerDelay = 0.02,
  animation = 'fade-up',
}: SplitTextProps) {
  const words = children.split(' ');

  const getVariants = () => {
    switch (animation) {
      case 'blur':
        return {
          hidden: { opacity: 0, filter: 'blur(10px)' },
          visible: { opacity: 1, filter: 'blur(0px)' },
        };
      case 'rotate':
        return {
          hidden: { opacity: 0, rotateX: -90 },
          visible: { opacity: 1, rotateX: 0 },
        };
      case 'scale':
        return {
          hidden: { opacity: 0, scale: 0 },
          visible: { opacity: 1, scale: 1 },
        };
      default: // fade-up
        return {
          hidden: { opacity: 0, y: 20 },
          visible: { opacity: 1, y: 0 },
        };
    }
  };

  return (
    <span className={cn('inline-block', className)}>
      {words.map((word, i) => (
        <span key={i} className="inline-block overflow-hidden">
          <motion.span
            className="inline-block"
            variants={getVariants()}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-10%' }}
            transition={{
              duration: 0.6,
              delay: delay + i * staggerDelay,
              ease: [0.25, 0.46, 0.45, 0.94],
            }}
          >
            {word}
            {i < words.length - 1 && '\u00A0'}
          </motion.span>
        </span>
      ))}
    </span>
  );
}