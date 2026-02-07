'use client';

import { useEffect, useRef, useState } from 'react';
import { motion, useSpring, useMotionValue } from 'framer-motion';
import { cn } from '@/lib/utils';

interface CustomCursorProps {
  className?: string;
}

export function CustomCursor({ className }: CustomCursorProps) {
  const cursorRef = useRef<HTMLDivElement>(null);
  const [isHovering, setIsHovering] = useState(false);
  const [cursorText, setCursorText] = useState('');
  const [isVisible, setIsVisible] = useState(false);

  const cursorX = useMotionValue(-100);
  const cursorY = useMotionValue(-100);

  const springConfig = { damping: 25, stiffness: 300, mass: 0.5 };
  const cursorXSpring = useSpring(cursorX, springConfig);
  const cursorYSpring = useSpring(cursorY, springConfig);

  useEffect(() => {
    const moveCursor = (e: MouseEvent) => {
      cursorX.set(e.clientX);
      cursorY.set(e.clientY);
      if (!isVisible) setIsVisible(true);
    };

    const handleMouseEnter = () => setIsVisible(true);
    const handleMouseLeave = () => setIsVisible(false);

    // Handle magnetic elements
    const handleMagnetic = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const magneticEl = target.closest('[data-magnetic]');

      if (magneticEl) {
        setIsHovering(true);
        const text = magneticEl.getAttribute('data-cursor-text');
        if (text) setCursorText(text);
      } else {
        setIsHovering(false);
        setCursorText('');
      }
    };

    window.addEventListener('mousemove', moveCursor);
    window.addEventListener('mousemove', handleMagnetic);
    window.addEventListener('mouseenter', handleMouseEnter);
    window.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      window.removeEventListener('mousemove', moveCursor);
      window.removeEventListener('mousemove', handleMagnetic);
      window.removeEventListener('mouseenter', handleMouseEnter);
      window.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [cursorX, cursorY, isVisible]);

  return (
    <>
      <motion.div
        ref={cursorRef}
        className={cn(
          'pointer-events-none fixed z-[9999] mix-blend-difference hidden lg:block',
          className
        )}
        style={{
          x: cursorXSpring,
          y: cursorYSpring,
          translateX: '-50%',
          translateY: '-50%',
        }}
      >
        <motion.div
          className="relative"
          animate={{
            scale: isHovering ? 1.5 : 1,
          }}
          transition={{ duration: 0.2 }}
        >
          <motion.div
            className={cn(
              'rounded-full border-2 transition-colors',
              isHovering ? 'border-background' : 'border-foreground'
            )}
            animate={{
              width: isHovering ? 48 : 24,
              height: isHovering ? 48 : 24,
            }}
            transition={{ duration: 0.2 }}
          />
          {cursorText && (
            <motion.div
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-xs font-medium text-background whitespace-nowrap"
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0 }}
            >
              {cursorText}
            </motion.div>
          )}
        </motion.div>
      </motion.div>
      <style jsx global>{`
        * {
          cursor: none !important;
        }
        @media (max-width: 1024px) {
          * {
            cursor: auto !important;
          }
        }
      `}</style>
    </>
  );
}
