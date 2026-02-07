'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { ImageIcon } from 'lucide-react';

interface ImagePlaceholderProps {
  prompt: string;
  aspectRatio?: 'square' | 'video' | 'portrait' | 'wide';
  className?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export function ImagePlaceholder({
  prompt,
  aspectRatio = 'video',
  className,
  size = 'md',
}: ImagePlaceholderProps) {
  const aspectClasses = {
    square: 'aspect-square',
    video: 'aspect-video',
    portrait: 'aspect-[3/4]',
    wide: 'aspect-[21/9]',
  };

  const sizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
    xl: 'text-lg',
  };

  return (
    <motion.div
      className={cn(
        'relative overflow-hidden rounded-2xl border-2 border-dashed border-border bg-muted/30',
        'flex items-center justify-center',
        aspectClasses[aspectRatio],
        className
      )}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-foreground/5 to-transparent" />

      {/* Grid pattern */}
      <div className="absolute inset-0 opacity-10">
        <svg className="w-full h-full">
          <defs>
            <pattern
              id={`grid-${prompt.replace(/\s/g, '-')}`}
              width="32"
              height="32"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 32 0 L 0 0 0 32"
                fill="none"
                stroke="currentColor"
                strokeWidth="1"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill={`url(#grid-${prompt.replace(/\s/g, '-')})`} />
        </svg>
      </div>

      {/* Content */}
      <div className="relative z-10 p-6 text-center max-w-md">
        <ImageIcon className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-50" />
        <p className={cn('text-muted-foreground font-medium leading-relaxed', sizeClasses[size])}>
          📸 <span className="italic">{prompt}</span>
        </p>
      </div>

      {/* Shimmer effect */}
      <div className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity duration-500">
        <div
          className="absolute inset-0 -translate-x-full animate-shimmer"
          style={{
            background:
              'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
          }}
        />
      </div>
    </motion.div>
  );
}

export function ImagePlaceholderGrid({
  prompts,
  className,
}: {
  prompts: { prompt: string; aspectRatio?: 'square' | 'video' | 'portrait' | 'wide' }[];
  className?: string;
}) {
  return (
    <div className={cn('grid gap-6', className)}>
      {prompts.map((item, index) => (
        <ImagePlaceholder
          key={index}
          prompt={item.prompt}
          aspectRatio={item.aspectRatio}
        />
      ))}
    </div>
  );
}
