'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface KineticTypographyProps {
  text: string;
  className?: string;
}

export function KineticTypography({ text, className }: KineticTypographyProps) {
  const letters = text.split('');

  const container = {
    hidden: { opacity: 0 },
    visible: (i = 1) => ({
      opacity: 1,
      transition: { staggerChildren: 0.03, delayChildren: 0.04 * i },
    }),
  };

  const child = {
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring' as const,
        damping: 12,
        stiffness: 200,
      },
    },
    hidden: {
      opacity: 0,
      y: 20,
      transition: {
        type: 'spring' as const,
        damping: 12,
        stiffness: 200,
      },
    },
  };

  return (
    <motion.div
      className={cn('flex flex-wrap overflow-hidden', className)}
      variants={container}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
    >
      {letters.map((letter, index) => (
        <motion.span
          key={index}
          variants={child}
          className="inline-block"
          whileHover={{
            y: -5,
            color: 'var(--muted-foreground)',
            transition: { duration: 0.2 },
          }}
        >
          {letter === ' ' ? '\u00A0' : letter}
        </motion.span>
      ))}
    </motion.div>
  );
}