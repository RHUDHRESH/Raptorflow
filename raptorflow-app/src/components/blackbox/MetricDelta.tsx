'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MetricDeltaProps {
    value: string | number;
    delta: number;
    label: string;
    unit?: string;
    inverse?: boolean; // If true, negative delta is good (e.g. cost)
}

export function MetricDelta({ value, delta, label, unit = '', inverse = false }: MetricDeltaProps) {
    const isPositive = delta > 0;
    const isZero = delta === 0;

    // Determine color based on delta and inverse property
    let deltaColor = "text-muted-foreground";
    if (!isZero) {
        if (inverse) {
            deltaColor = isPositive ? "text-red-500" : "text-emerald-500";
        } else {
            deltaColor = isPositive ? "text-emerald-500" : "text-red-500";
        }
    }

    return (
        <div className="p-6 rounded-2xl bg-card border border-border group hover:border-accent/20 transition-all duration-300">
            <div className="flex flex-col gap-1">
                <span className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground font-sans">
                    {label}
                </span>

                <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-display font-semibold tracking-tight">
                        {value}{unit}
                    </span>

                    <AnimatePresence mode="wait">
                        <motion.div
                            key={delta}
                            initial={{ opacity: 0, y: 5 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -5 }}
                            className={cn(
                                "flex items-center text-xs font-mono font-medium",
                                deltaColor
                            )}
                        >
                            {!isZero && (
                                isPositive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />
                            )}
                            {isZero ? <Minus size={14} /> : `${Math.abs(delta)}%`}
                        </motion.div>
                    </AnimatePresence>
                </div>
            </div>

            {/* Subtle progress background for "Industrial" feel */}
            <div className="mt-4 h-1 w-full bg-muted rounded-full overflow-hidden">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: '60%' }} // Mock progress
                    className="h-full bg-accent/20"
                />
            </div>
        </div>
    );
}
