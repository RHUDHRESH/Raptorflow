'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

interface PreloaderProps {
  onComplete?: () => void;
  className?: string;
}

export function Preloader({ onComplete, className }: PreloaderProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Simulate loading progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            setIsLoading(false);
            onComplete?.();
          }, 500);
          return 100;
        }
        return prev + Math.random() * 15;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <AnimatePresence>
      {isLoading && (
        <motion.div
          className={cn(
            'fixed inset-0 z-[9999] flex items-center justify-center bg-background',
            className
          )}
          initial={{ opacity: 1 }}
          exit={{
            opacity: 0,
            transition: { duration: 0.8, ease: 'easeInOut' },
          }}
        >
          <div className="relative">
            {/* Logo/Brand */}
            <motion.div
              className="mb-12 text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <h1 className="font-display text-6xl font-medium tracking-tight">
                RaptorFlow
              </h1>
              <p className="text-sm text-muted-foreground mt-2 tracking-wide uppercase">
                Loading your experience
              </p>
            </motion.div>

            {/* Progress Bar */}
            <div className="w-80 h-1 bg-muted rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-foreground"
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(progress, 100)}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>

            {/* Percentage */}
            <motion.div
              className="text-center mt-4 font-mono text-sm text-muted-foreground"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              {Math.floor(progress)}%
            </motion.div>
          </div>

          {/* Animated Grid Background */}
          <div className="absolute inset-0 overflow-hidden opacity-5 -z-10">
            <svg className="w-full h-full">
              <defs>
                <pattern
                  id="grid"
                  width="40"
                  height="40"
                  patternUnits="userSpaceOnUse"
                >
                  <path
                    d="M 40 0 L 0 0 0 40"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1"
                  />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
            </svg>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
