"use client";

import React from "react";
import { motion } from "framer-motion";

// ═══════════════════════════════════════════════════════════════
// Gradient Orb Background Effect
// Floating gradient orbs for visual depth
// ═══════════════════════════════════════════════════════════════

interface GradientOrbProps {
  className?: string;
  color?: "coral" | "ocean" | "sage" | "lavender" | "mixed";
  size?: "sm" | "md" | "lg" | "xl";
  animate?: boolean;
}

export function GradientOrb({
  className = "",
  color = "mixed",
  size = "lg",
  animate = true,
}: GradientOrbProps) {
  const sizeClasses = {
    sm: "w-64 h-64",
    md: "w-96 h-96",
    lg: "w-[500px] h-[500px]",
    xl: "w-[700px] h-[700px]",
  };

  const colorClasses = {
    coral: "bg-gradient-to-br from-[#E08D79]/30 via-[#EBB098]/20 to-transparent",
    ocean: "bg-gradient-to-br from-[#8CA9B3]/30 via-[#A6C4B9]/20 to-transparent",
    sage: "bg-gradient-to-br from-[#9CAF98]/30 via-[#A6C4B9]/20 to-transparent",
    lavender: "bg-gradient-to-br from-[#B3A5B8]/30 via-[#9D92B0]/20 to-transparent",
    mixed: "bg-gradient-to-br from-[#E08D79]/20 via-[#8CA9B3]/15 to-[#9CAF98]/10",
  };

  if (!animate) {
    return (
      <div
        className={`absolute rounded-full blur-3xl pointer-events-none ${sizeClasses[size]} ${colorClasses[color]} ${className}`}
      />
    );
  }

  return (
    <motion.div
      className={`absolute rounded-full blur-3xl pointer-events-none ${sizeClasses[size]} ${colorClasses[color]} ${className}`}
      animate={{
        scale: [1, 1.1, 1],
        x: [0, 20, -10, 0],
        y: [0, -20, 10, 0],
      }}
      transition={{
        duration: 15,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    />
  );
}

// ═══════════════════════════════════════════════════════════════
// Multiple Orbs Container
// ═══════════════════════════════════════════════════════════════

export function GradientOrbContainer() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <GradientOrb
        color="coral"
        size="xl"
        className="-top-48 -right-48"
      />
      <GradientOrb
        color="ocean"
        size="lg"
        className="top-1/3 -left-24"
      />
      <GradientOrb
        color="sage"
        size="md"
        className="bottom-1/4 right-1/4"
      />
      <GradientOrb
        color="lavender"
        size="sm"
        className="top-1/2 right-1/3"
      />
    </div>
  );
}
