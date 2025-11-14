"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

/**
 * A subtle dark gradient background for premium, minimal aesthetic.
 * Replaces the colorful aurora with black/white/grey only.
 * Respects prefers-reduced-motion for accessibility.
 */
export function DarkBackground() {
  const [shouldAnimate, setShouldAnimate] = useState(true);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setShouldAnimate(!mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setShouldAnimate(!e.matches);
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  return (
    <div className="absolute inset-0 z-0 overflow-hidden bg-gradient-to-br from-slate-950 via-zinc-950 to-neutral-950">
      {/* Subtle radial highlights using greys only */}
      {shouldAnimate ? (
        <>
          <motion.div
            className="absolute top-0 left-0 w-[40rem] h-[40rem] rounded-full blur-3xl"
            style={{
              background: "radial-gradient(circle, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 50%, transparent 100%)",
            }}
            animate={{
              opacity: [0.3, 0.5, 0.3],
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 20,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
          <motion.div
            className="absolute bottom-0 right-0 w-[35rem] h-[35rem] rounded-full blur-3xl"
            style={{
              background: "radial-gradient(circle, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 50%, transparent 100%)",
            }}
            animate={{
              opacity: [0.2, 0.4, 0.2],
              scale: [1, 1.05, 1],
            }}
            transition={{
              duration: 25,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        </>
      ) : (
        <>
          <div
            className="absolute top-0 left-0 w-[40rem] h-[40rem] rounded-full blur-3xl opacity-40"
            style={{
              background: "radial-gradient(circle, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 50%, transparent 100%)",
            }}
          />
          <div
            className="absolute bottom-0 right-0 w-[35rem] h-[35rem] rounded-full blur-3xl opacity-30"
            style={{
              background: "radial-gradient(circle, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 50%, transparent 100%)",
            }}
          />
        </>
      )}
    </div>
  );
}

