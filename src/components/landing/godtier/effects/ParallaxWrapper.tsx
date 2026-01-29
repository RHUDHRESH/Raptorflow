"use client";

import React from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

// ═══════════════════════════════════════════════════════════════
// Parallax Wrapper
// Simple parallax effect for child elements
// ═══════════════════════════════════════════════════════════════

interface ParallaxWrapperProps {
  children: React.ReactNode;
  className?: string;
  speed?: number; // -1 to 1, negative moves slower, positive moves faster
}

export function ParallaxWrapper({
  children,
  className = "",
  speed = 0.5,
}: ParallaxWrapperProps) {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  const y = useTransform(scrollYProgress, [0, 1], [0, speed * 100]);

  return (
    <motion.div ref={ref} className={className} style={{ y }}>
      {children}
    </motion.div>
  );
}
