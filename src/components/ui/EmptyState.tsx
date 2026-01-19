"use client";

import React from "react";
import { motion } from "framer-motion";
import { FileSearch, Rocket, BarChart3, FolderOpen } from "lucide-react";
import Link from "next/link";

interface EmptyStateProps {
    /** Icon to display - defaults to FileSearch01Icon */
    icon?: React.ComponentType<any>;
    /** Main title */
    title: string;
    /** Description text */
    description: string;
    /** Optional action button */
    action?: {
        label: string;
        href?: string;
        onClick?: () => void;
    };
    /** Visual variant */
    variant?: "default" | "minimal" | "illustrated";
    /** Additional className */
    className?: string;
}

/**
 * Premium empty state component for when there's no data to display.
 * Use this instead of showing blank space or raw "No data" text.
 */
export function EmptyState({
    icon: Icon = FileSearch,
    title,
    description,
    action,
    variant = "default",
    className = ""
}: EmptyStateProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className={`flex flex-col items-center justify-center text-center py-16 px-6 ${className}`}
        >
            {/* Icon Container */}
            <motion.div
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.1, type: "spring" }}
                className={`mb-6 ${variant === "minimal"
                    ? "w-12 h-12"
                    : "w-16 h-16 p-4 rounded-2xl bg-[var(--surface)] border border-[var(--border)]"
                    }`}
            >
                {React.createElement(Icon as any, {
                    className: `w-full h-full text-[var(--muted)]`
                })}
            </motion.div>

            {/* Title */}
            <h3 className="text-lg font-semibold text-[var(--ink)] mb-2">
                {title}
            </h3>

            {/* Description */}
            <p className="text-sm text-[var(--secondary)] max-w-sm leading-relaxed mb-6">
                {description}
            </p>

            {/* Action Button */}
            {action && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                >
                    {action.href ? (
                        <Link
                            href={action.href}
                            className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--ink)] text-[var(--canvas)] text-sm font-medium rounded-lg hover:bg-[var(--ink)]/90 transition-colors"
                        >
                            {action.label}
                        </Link>
                    ) : (
                        <button
                            onClick={action.onClick}
                            className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--ink)] text-[var(--canvas)] text-sm font-medium rounded-lg hover:bg-[var(--ink)]/90 transition-colors"
                        >
                            {action.label}
                        </button>
                    )}
                </motion.div>
            )}
        </motion.div>
    );
}

/**
 * Preset empty states for common scenarios.
 */
export const EmptyStatePresets = {
    NoMoves: () => (
        <EmptyState
            icon={Rocket}
            title="No moves yet"
            description="Your weekly execution packets will appear here. Complete your Foundation setup to generate your first moves."
            action={{ label: "Go to Foundation", href: "/foundation" }}
        />
    ),
    NoData: () => (
        <EmptyState
            icon={BarChart3}
            title="Waiting for data"
            description="Once you start executing moves, your performance metrics will appear here."
        />
    ),
    NoCampaigns: () => (
        <EmptyState
            icon={FolderOpen}
            title="No campaigns"
            description="Create your first campaign to organize your marketing efforts into focused 90-day sprints."
            action={{ label: "Create Campaign", href: "/campaigns/new" }}
        />
    ),
    NoResults: () => (
        <EmptyState
            icon={FileSearch}
            title="No results found"
            description="Try adjusting your search or filters to find what you're looking for."
        />
    ),
};
