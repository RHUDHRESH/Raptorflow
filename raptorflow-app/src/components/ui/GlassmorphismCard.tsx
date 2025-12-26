'use client';

import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface GlassmorphismCardProps {
  children: ReactNode;
  className?: string;
  blur?: 'sm' | 'md' | 'lg' | 'xl';
  border?: boolean;
}

export function GlassmorphismCard({
  children,
  className,
  blur = 'md',
  border = true,
}: GlassmorphismCardProps) {
  const blurClass = {
    sm: 'backdrop-blur-sm',
    md: 'backdrop-blur-md',
    lg: 'backdrop-blur-lg',
    xl: 'backdrop-blur-xl',
  };

  return (
    <motion.div
      className={cn(
        'relative overflow-hidden rounded-2xl',
        'bg-background/40',
        blurClass[blur],
        border && 'border border-border/50',
        'shadow-xl',
        className
      )}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-foreground/5 via-transparent to-transparent pointer-events-none" />
      
      {/* Shine effect */}
      <div className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity duration-500">
        <div
          className="absolute inset-0"
          style={{
            background:
              'linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%)',
            backgroundSize: '200% 200%',
            animation: 'shine 3s infinite',
          }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10">{children}</div>

      <style jsx>{`
        @keyframes shine {
          0% {
            background-position: -200% 0;
          }
          100% {
            background-position: 200% 0;
          }
        }
      `}</style>
    </motion.div>
  );
}