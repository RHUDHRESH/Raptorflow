'use client';

import React from 'react';

/**
 * High-End 'Cinematic' Motion Primitives
 * Philosophy: "It's already there, it just appeared."
 * No bounce. No spring. Just sleek ease-out.
 */

// Simple CSS-based implementations to avoid heavyweight deps if Framer Motion isn't available
// Using Tailwind Animate classes we defined in tailwind.config.js

interface FadeInProps {
  children: React.ReactNode;
  delay?: number; // index to multiply delay by
  className?: string;
}

export function FadeIn({ children, delay = 0, className = '' }: FadeInProps) {
  const style = {
    animationDelay: `${delay * 100}ms`,
    opacity: 0, // Start invisible, let animation handle it
  } as React.CSSProperties;

  return (
    <div className={`animate-slide-up-fade ${className}`} style={style}>
      {children}
    </div>
  );
}

export function Stagger({
  children,
  className = '',
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={className}>
      {React.Children.map(children, (child, index) => (
        <FadeIn delay={index + 1}>{child}</FadeIn>
      ))}
    </div>
  );
}
