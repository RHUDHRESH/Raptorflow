"use client";

import React, { useEffect, useState } from "react";
import { motion, useScroll, useSpring } from "framer-motion";

// ═══════════════════════════════════════════════════════════════
// Scroll Progress Indicator
// Shows reading progress at top of viewport
// ═══════════════════════════════════════════════════════════════

export function ScrollProgress() {
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001,
  });

  return (
    <motion.div
      className="fixed top-0 left-0 right-0 h-1 bg-[var(--ink)] origin-left z-[60]"
      style={{ scaleX }}
    />
  );
}

// ═══════════════════════════════════════════════════════════════
// Scroll to section utility
// ═══════════════════════════════════════════════════════════════

export function scrollToSection(sectionId: string) {
  const element = document.getElementById(sectionId);
  if (element) {
    element.scrollIntoView({ behavior: "smooth" });
  }
}
