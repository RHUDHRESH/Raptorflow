"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";
import { cn } from "@/lib/utils";

/**
 * A reusable container for the ICP grid layout.
 * Refactored from BentoGrid to be black/white only.
 */
interface ICPGridProps {
  children: ReactNode;
}

export function ICPGrid({ children }: ICPGridProps) {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 },
    },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="grid grid-cols-1 md:grid-cols-6 gap-6 auto-rows-[280px] p-6"
    >
      {children}
    </motion.div>
  );
}

/**
 * A single item within the ICP Grid with hover and animation.
 * Premium black/white aesthetic with subtle shine effect.
 */
interface ICPGridItemProps {
  className?: string;
  children: ReactNode;
  colSpan?: 1 | 2 | 3 | 4 | 5 | 6;
}

export function ICPGridItem({
  className = "",
  children,
  colSpan = 1,
}: ICPGridItemProps) {
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 },
    },
  };

  const colSpanClasses = {
    1: "md:col-span-1",
    2: "md:col-span-2",
    3: "md:col-span-3",
    4: "md:col-span-4",
    5: "md:col-span-5",
    6: "md:col-span-6",
  };

  return (
    <motion.div
      variants={itemVariants}
      whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
      className={cn(
        "relative overflow-hidden group",
        "bg-gradient-to-br from-slate-950 via-slate-900 to-zinc-900",
        "border border-slate-700/60",
        "rounded-3xl shadow-lg",
        "p-6 flex flex-col justify-between",
        colSpanClasses[colSpan],
        className
      )}
    >
      {/* Subtle white/grey shine effect on hover */}
      <div
        className="
          absolute top-0 left-[-150%] h-full w-[50%]
          bg-[linear-gradient(to_right,transparent_0%,rgba(255,255,255,0.08)_50%,transparent_100%)]
          skew-x-[-25deg]
          transition-all duration-700 ease-in-out
          group-hover:left-[125%]
        "
      />
      <div className="relative z-10 h-full flex flex-col">{children}</div>
    </motion.div>
  );
}

