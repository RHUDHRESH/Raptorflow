'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface AnimatedGradientProps {
  className?: string;
  colors?: string[];
}

export function AnimatedGradient({
  className,
  colors = ['#2D3538', '#5B5F61', '#C0C1BE'],
}: AnimatedGradientProps) {
  return (
    <div className={cn('absolute inset-0 overflow-hidden', className)}>
      <motion.div
        className="absolute inset-0"
        style={{
          background: `linear-gradient(45deg, ${colors.join(', ')})`,
          backgroundSize: '400% 400%',
        }}
        animate={{
          backgroundPosition: [
            '0% 50%',
            '100% 50%',
            '100% 100%',
            '0% 100%',
            '0% 50%',
          ],
        }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: 'linear',
        }}
      />
    </div>
  );
}

export function GradientMesh({ className }: { className?: string }) {
  return (
    <div
      className={cn('absolute inset-0 overflow-hidden opacity-30', className)}
    >
      <svg className="w-full h-full" viewBox="0 0 1000 1000">
        <defs>
          <radialGradient id="grad1" cx="30%" cy="30%">
            <stop offset="0%" stopColor="currentColor" stopOpacity="0.3" />
            <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="grad2" cx="70%" cy="70%">
            <stop offset="0%" stopColor="currentColor" stopOpacity="0.3" />
            <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="grad3" cx="50%" cy="50%">
            <stop offset="0%" stopColor="currentColor" stopOpacity="0.2" />
            <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
          </radialGradient>
        </defs>

        <motion.circle
          cx="300"
          cy="300"
          r="200"
          fill="url(#grad1)"
          animate={{
            cx: [300, 400, 300],
            cy: [300, 400, 300],
            r: [200, 250, 200],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />

        <motion.circle
          cx="700"
          cy="700"
          r="250"
          fill="url(#grad2)"
          animate={{
            cx: [700, 600, 700],
            cy: [700, 600, 700],
            r: [250, 200, 250],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />

        <motion.circle
          cx="500"
          cy="500"
          r="180"
          fill="url(#grad3)"
          animate={{
            cx: [500, 550, 500],
            cy: [500, 450, 500],
            r: [180, 220, 180],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      </svg>
    </div>
  );
}
