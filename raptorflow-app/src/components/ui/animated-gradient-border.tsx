'use client';

import React from 'react';
import { motion } from 'motion/react';
import { cn } from '@/lib/utils';

interface AnimatedGradientBorderProps {
  children: React.ReactNode;
  className?: string;
  active?: boolean;
  variant?: 'default' | 'success' | 'error';
}

export function AnimatedGradientBorder({
  children,
  className = '',
  active = false,
  variant = 'default',
}: AnimatedGradientBorderProps) {
  const gradientColors = {
    default: 'from-foreground/20 via-foreground/40 to-foreground/20',
    success: 'from-green-500/20 via-green-500/40 to-green-500/20',
    error: 'from-red-500/20 via-red-500/40 to-red-500/20',
  };

  if (!active) {
    return <div className={className}>{children}</div>;
  }

  return (
    <div className={cn('relative', className)}>
      <motion.div
        className="absolute inset-0 rounded-xl bg-gradient-to-r opacity-50"
        animate={{
          background: [
            `linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)`,
            `linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)`,
            `linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)`,
          ],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'linear',
        }}
      />
      <motion.div
        className="absolute inset-0 rounded-xl bg-gradient-to-r opacity-60"
        animate={{
          x: ['-100%', '100%'],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'linear',
        }}
      />
      <div className="relative rounded-xl overflow-hidden">{children}</div>
    </div>
  );
}
