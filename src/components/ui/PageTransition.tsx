"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { usePathname } from "next/navigation";

interface PageTransitionProps {
    children: React.ReactNode;
}

/**
 * Wraps page content with smooth fade transitions between routes.
 * Use at the layout level to animate page changes.
 */
export function PageTransition({ children }: PageTransitionProps) {
    const pathname = usePathname();

    return (
        <AnimatePresence mode="wait">
            <motion.div
                key={pathname}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{
                    duration: 0.25,
                    ease: [0.25, 0.1, 0.25, 1.0]
                }}
                className="w-full"
            >
                {children}
            </motion.div>
        </AnimatePresence>
    );
}

/**
 * Simpler fade-only transition for less jarring effect.
 */
export function FadeTransition({ children }: PageTransitionProps) {
    const pathname = usePathname();

    return (
        <AnimatePresence mode="wait">
            <motion.div
                key={pathname}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="w-full"
            >
                {children}
            </motion.div>
        </AnimatePresence>
    );
}

/**
 * Staggered container for animating multiple children on page load.
 */
export function StaggerContainer({
    children,
    className = "",
    staggerDelay = 0.05
}: {
    children: React.ReactNode;
    className?: string;
    staggerDelay?: number;
}) {
    return (
        <motion.div
            initial="hidden"
            animate="visible"
            variants={{
                hidden: { opacity: 0 },
                visible: {
                    opacity: 1,
                    transition: {
                        staggerChildren: staggerDelay,
                        delayChildren: 0.1
                    }
                }
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

/**
 * Individual stagger item - use inside StaggerContainer.
 */
export function StaggerItem({
    children,
    className = ""
}: {
    children: React.ReactNode;
    className?: string
}) {
    return (
        <motion.div
            variants={{
                hidden: { opacity: 0, y: 20 },
                visible: {
                    opacity: 1,
                    y: 0,
                    transition: { duration: 0.4, ease: "easeOut" }
                }
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}
