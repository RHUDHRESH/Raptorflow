"use client";

import React from "react";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";

// ═══════════════════════════════════════════════════════════════
// Text Reveal Animation
// Staggered character or word reveal
// ═══════════════════════════════════════════════════════════════

interface TextRevealProps {
  children: string;
  className?: string;
  delay?: number;
  stagger?: number;
  type?: "chars" | "words" | "lines";
  once?: boolean;
}

export function TextReveal({
  children,
  className = "",
  delay = 0,
  stagger = 0.02,
  type = "words",
  once = true,
}: TextRevealProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once, margin: "-100px" });

  const splitText = () => {
    switch (type) {
      case "chars":
        return children.split("");
      case "words":
        return children.split(" ");
      case "lines":
        return children.split("\n");
      default:
        return children.split(" ");
    }
  };

  const items = splitText();

  const container = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        delayChildren: delay,
        staggerChildren: stagger,
      },
    },
  };

  const child = {
    hidden: {
      opacity: 0,
      y: 20,
      rotateX: -90,
    },
    visible: {
      opacity: 1,
      y: 0,
      rotateX: 0,
      transition: {
        duration: 0.5,
        ease: [0.16, 1, 0.3, 1],
      },
    },
  };

  return (
    <motion.span
      ref={ref}
      className={`inline-flex flex-wrap ${className}`}
      variants={container}
      initial="hidden"
      animate={isInView ? "visible" : "hidden"}
      style={{ perspective: "1000px" }}
    >
      {items.map((item, i) => (
        <motion.span
          key={i}
          variants={child}
          className="inline-block"
          style={{ transformStyle: "preserve-3d" }}
        >
          {item}
          {type === "words" && i < items.length - 1 && "\u00A0"}
        </motion.span>
      ))}
    </motion.span>
  );
}

// ═══════════════════════════════════════════════════════════════
// Simple Fade Up Text
// ═══════════════════════════════════════════════════════════════

interface FadeUpTextProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  duration?: number;
}

export function FadeUpText({
  children,
  className = "",
  delay = 0,
  duration = 0.6,
}: FadeUpTextProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-50px" });

  return (
    <motion.div
      ref={ref}
      className={className}
      initial={{ opacity: 0, y: 30 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
      transition={{
        duration,
        delay,
        ease: [0.16, 1, 0.3, 1],
      }}
    >
      {children}
    </motion.div>
  );
}
