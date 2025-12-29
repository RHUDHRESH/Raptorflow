'use client';

import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface RadarScannerProps {
  status: 'idle' | 'scanning' | 'found' | 'results';
  onScanComplete?: () => void;
}

export function RadarScanner({ status, onScanComplete }: RadarScannerProps) {
  const [scanMessage, setScanMessage] = useState('Initializing scan...');

  useEffect(() => {
    if (status === 'scanning') {
      const messages = [
        'Scanning sources...',
        'Filtering noise...',
        'Ranking relevance...',
        'Analyzing angles...',
      ];
      let i = 0;
      const interval = setInterval(() => {
        setScanMessage(messages[i % messages.length]);
        i++;
      }, 1200);

      const timer = setTimeout(() => {
        clearInterval(interval);
        onScanComplete?.();
      }, 5000); // 5s scan duration

      return () => {
        clearInterval(interval);
        clearTimeout(timer);
      };
    }
  }, [status, onScanComplete]);

  return (
    <div
      className={cn(
        'relative flex flex-col items-center justify-center transition-all duration-700 ease-in-out',
        status === 'results'
          ? 'h-32 w-32 scale-75 opacity-0 hidden'
          : 'h-[60vh] w-full'
      )}
    >
      {/* The Sonar Field */}
      <div className="relative flex items-center justify-center">
        {/* Rings */}
        {[1, 2, 3].map((ring) => (
          <div
            key={ring}
            className={cn(
              'absolute rounded-full border border-primary/20',
              status === 'scanning' && 'animate-pulse'
            )}
            style={{
              width: `${ring * 200}px`,
              height: `${ring * 200}px`,
              opacity: 0.1 + ring * 0.1,
              animationDelay: `${ring * 0.5}s`,
            }}
          />
        ))}

        {/* The Sweep */}
        <motion.div
          className="absolute w-[300px] h-[300px] rounded-full bg-gradient-to-tr from-transparent via-transparent to-primary/10"
          animate={status === 'scanning' ? { rotate: 360 } : { rotate: 0 }}
          transition={
            status === 'scanning'
              ? { duration: 4, repeat: Infinity, ease: 'linear' }
              : { duration: 0 }
          }
          style={{ originX: 0.5, originY: 0.5 }}
        />

        {/* Center Dot */}
        <div className="h-3 w-3 rounded-full bg-primary/80 shadow-[0_0_15px_rgba(var(--primary),0.5)] z-10" />

        {/* Status Text (Floating) */}
        <AnimatePresence mode="wait">
          {status === 'scanning' && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              key={scanMessage}
              className="absolute top-[180px] text-sm font-mono text-muted-foreground uppercase tracking-widest"
            >
              {scanMessage}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
