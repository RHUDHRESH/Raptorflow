"use client";

import React from "react";
import { motion } from "framer-motion";
import { useScroll, useSpring } from "framer-motion";

/**
 * A thin progress bar at the very top of the page showing scroll progress.
 */
export function ScrollProgress() {
    const { scrollYProgress } = useScroll();
    const scaleX = useSpring(scrollYProgress, {
        stiffness: 100,
        damping: 30,
        restDelta: 0.001
    });

    return (
        <motion.div
            style={{ scaleX }}
            className="fixed top-0 left-0 right-0 h-1 bg-gradient-to-r from-[var(--accent)] to-[var(--ink)] origin-left z-[100]"
        />
    );
}
