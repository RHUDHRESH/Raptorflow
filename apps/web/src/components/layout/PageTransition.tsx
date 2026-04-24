"use client";

import { motion } from "framer-motion";
import { type ReactNode } from "react";

const variants = {
  hidden: { opacity: 0, y: 8 },
  visible: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -4 },
};

export function PageTransition({ children }: { children: ReactNode }) {
  return (
    <motion.div
      variants={variants}
      initial="hidden"
      animate="visible"
      exit="exit"
      transition={{ duration: 0.18, ease: [0.19, 1, 0.22, 1] }}
      className="h-full"
    >
      {children}
    </motion.div>
  );
}
