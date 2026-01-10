"use client";

import { motion } from "motion/react";
import { cn } from "@/lib/utils";

interface Tab {
    id: string;
    label: string;
}

interface SegmentedTabsProps {
    tabs: Tab[];
    activeTab: string;
    onTabChange: (tab: string) => void;
    className?: string;
}

export function SegmentedTabs({
    tabs,
    activeTab,
    onTabChange,
    className,
}: SegmentedTabsProps) {
    return (
        <div
            className={cn(
                "inline-flex h-10 items-center rounded-xl border border-border bg-card p-1",
                className
            )}
        >
            {tabs.map((tab) => {
                const isActive = activeTab === tab.id;
                return (
                    <button
                        key={tab.id}
                        onClick={() => onTabChange(tab.id)}
                        className={cn(
                            "relative h-8 rounded-lg px-4 text-[14px] font-medium transition-colors",
                            !isActive && "text-muted-foreground hover:text-foreground"
                        )}
                    >
                        {isActive && (
                            <motion.div
                                layoutId="activeTab"
                                className="absolute inset-0 rounded-lg bg-foreground"
                                transition={{
                                    type: "spring",
                                    stiffness: 500,
                                    damping: 35,
                                }}
                            />
                        )}
                        <span
                            className={cn(
                                "relative z-10",
                                isActive && "text-background"
                            )}
                        >
                            {tab.label}
                        </span>
                    </button>
                );
            })}
        </div>
    );
}
