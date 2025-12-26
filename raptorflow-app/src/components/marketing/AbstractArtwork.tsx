'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface AbstractArtworkProps {
  variant?: 'geometric' | 'organic' | 'grid' | 'waves';
  className?: string;
  animate?: boolean;
}

export function AbstractArtwork({
  variant = 'geometric',
  className,
  animate = true,
}: AbstractArtworkProps) {
  if (variant === 'geometric') {
    return (
      <svg
        className={cn('w-full h-full', className)}
        viewBox="0 0 800 800"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <motion.g
          initial={animate ? { opacity: 0, scale: 0.8 } : undefined}
          animate={animate ? { opacity: 1, scale: 1 } : undefined}
          transition={{ duration: 1.5, ease: 'easeOut' }}
        >
          {/* Circles */}
          <motion.circle
            cx="400"
            cy="400"
            r="150"
            stroke="currentColor"
            strokeWidth="2"
            fill="none"
            initial={animate ? { pathLength: 0, rotate: 0 } : undefined}
            animate={
              animate
                ? { pathLength: 1, rotate: 360 }
                : undefined
            }
            transition={{ duration: 2, ease: 'easeInOut' }}
          />
          <motion.circle
            cx="400"
            cy="400"
            r="200"
            stroke="currentColor"
            strokeWidth="1"
            fill="none"
            opacity="0.5"
            initial={animate ? { pathLength: 0, rotate: 0 } : undefined}
            animate={
              animate
                ? { pathLength: 1, rotate: -360 }
                : undefined
            }
            transition={{ duration: 2.5, ease: 'easeInOut', delay: 0.2 }}
          />

          {/* Geometric shapes */}
          <motion.polygon
            points="400,200 500,400 400,600 300,400"
            stroke="currentColor"
            strokeWidth="2"
            fill="none"
            initial={animate ? { opacity: 0, scale: 0 } : undefined}
            animate={animate ? { opacity: 0.3, scale: 1 } : undefined}
            transition={{ duration: 1, delay: 0.5 }}
          />

          <motion.rect
            x="250"
            y="250"
            width="300"
            height="300"
            stroke="currentColor"
            strokeWidth="1"
            fill="none"
            opacity="0.2"
            initial={animate ? { rotate: 0 } : undefined}
            animate={animate ? { rotate: 45 } : undefined}
            transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
            style={{ transformOrigin: '400px 400px' }}
          />
        </motion.g>
      </svg>
    );
  }

  if (variant === 'organic') {
    return (
      <svg
        className={cn('w-full h-full', className)}
        viewBox="0 0 800 800"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <motion.g opacity="0.6">
          <motion.path
            d="M400,100 Q500,200 400,300 T400,500 T400,700"
            stroke="currentColor"
            strokeWidth="2"
            fill="none"
            initial={animate ? { pathLength: 0 } : undefined}
            animate={animate ? { pathLength: 1 } : undefined}
            transition={{ duration: 3, ease: 'easeInOut' }}
          />
          <motion.path
            d="M100,400 Q200,300 300,400 T500,400 T700,400"
            stroke="currentColor"
            strokeWidth="2"
            fill="none"
            initial={animate ? { pathLength: 0 } : undefined}
            animate={animate ? { pathLength: 1 } : undefined}
            transition={{ duration: 3, ease: 'easeInOut', delay: 0.3 }}
          />

          {/* Organic blobs */}
          <motion.ellipse
            cx="300"
            cy="300"
            rx="80"
            ry="120"
            fill="currentColor"
            opacity="0.1"
            animate={
              animate
                ? {
                    rx: [80, 100, 80],
                    ry: [120, 100, 120],
                  }
                : undefined
            }
            transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
          />
          <motion.ellipse
            cx="500"
            cy="500"
            rx="100"
            ry="80"
            fill="currentColor"
            opacity="0.1"
            animate={
              animate
                ? {
                    rx: [100, 80, 100],
                    ry: [80, 100, 80],
                  }
                : undefined
            }
            transition={{
              duration: 5,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 1,
            }}
          />
        </motion.g>
      </svg>
    );
  }

  if (variant === 'grid') {
    return (
      <svg
        className={cn('w-full h-full', className)}
        viewBox="0 0 800 800"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern
            id="small-grid"
            width="40"
            height="40"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 40 0 L 0 0 0 40"
              fill="none"
              stroke="currentColor"
              strokeWidth="0.5"
              opacity="0.2"
            />
          </pattern>
          <pattern
            id="large-grid"
            width="120"
            height="120"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 120 0 L 0 0 0 120"
              fill="none"
              stroke="currentColor"
              strokeWidth="1"
              opacity="0.3"
            />
          </pattern>
        </defs>
        <motion.g
          initial={animate ? { opacity: 0 } : undefined}
          animate={animate ? { opacity: 1 } : undefined}
          transition={{ duration: 1 }}
        >
          <rect width="800" height="800" fill="url(#small-grid)" />
          <rect width="800" height="800" fill="url(#large-grid)" />
        </motion.g>
      </svg>
    );
  }

  // waves variant
  return (
    <svg
      className={cn('w-full h-full', className)}
      viewBox="0 0 800 400"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <motion.g>
        <motion.path
          d="M0,200 Q200,150 400,200 T800,200"
          stroke="currentColor"
          strokeWidth="2"
          fill="none"
          opacity="0.4"
          initial={animate ? { pathLength: 0 } : undefined}
          animate={
            animate
              ? {
                  pathLength: 1,
                  d: [
                    'M0,200 Q200,150 400,200 T800,200',
                    'M0,200 Q200,250 400,200 T800,200',
                    'M0,200 Q200,150 400,200 T800,200',
                  ],
                }
              : undefined
          }
          transition={{
            pathLength: { duration: 2, ease: 'easeInOut' },
            d: { duration: 6, repeat: Infinity, ease: 'easeInOut' },
          }}
        />
        <motion.path
          d="M0,220 Q200,170 400,220 T800,220"
          stroke="currentColor"
          strokeWidth="2"
          fill="none"
          opacity="0.3"
          initial={animate ? { pathLength: 0 } : undefined}
          animate={
            animate
              ? {
                  pathLength: 1,
                  d: [
                    'M0,220 Q200,170 400,220 T800,220',
                    'M0,220 Q200,270 400,220 T800,220',
                    'M0,220 Q200,170 400,220 T800,220',
                  ],
                }
              : undefined
          }
          transition={{
            pathLength: { duration: 2, ease: 'easeInOut', delay: 0.2 },
            d: {
              duration: 5,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 0.5,
            },
          }}
        />
        <motion.path
          d="M0,240 Q200,190 400,240 T800,240"
          stroke="currentColor"
          strokeWidth="2"
          fill="none"
          opacity="0.2"
          initial={animate ? { pathLength: 0 } : undefined}
          animate={
            animate
              ? {
                  pathLength: 1,
                  d: [
                    'M0,240 Q200,190 400,240 T800,240',
                    'M0,240 Q200,290 400,240 T800,240',
                    'M0,240 Q200,190 400,240 T800,240',
                  ],
                }
              : undefined
          }
          transition={{
            pathLength: { duration: 2, ease: 'easeInOut', delay: 0.4 },
            d: {
              duration: 7,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 1,
            },
          }}
        />
      </motion.g>
    </svg>
  );
}

// Decorative Elements
export function FloatingDots({ className }: { className?: string }) {
  return (
    <div className={cn('absolute inset-0 overflow-hidden', className)}>
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 rounded-full bg-current opacity-20"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.2, 0.5, 0.2],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 2,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
}

export function NoisTexture({ className }: { className?: string }) {
  return (
    <svg className={cn('absolute inset-0 w-full h-full', className)}>
      <filter id="noise">
        <feTurbulence
          type="fractalNoise"
          baseFrequency="0.8"
          numOctaves="4"
          stitchTiles="stitch"
        />
        <feColorMatrix type="saturate" values="0" />
      </filter>
      <rect width="100%" height="100%" filter="url(#noise)" opacity="0.03" />
    </svg>
  );
}
