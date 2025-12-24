'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { Plus, LucideIcon } from 'lucide-react';
import { motion } from 'framer-motion';

interface EmptyStateProps {
    title: string;
    description: string;
    actionLabel?: string;
    onAction?: () => void;
    icon?: LucideIcon;
}

export function EmptyState({
    title,
    description,
    actionLabel,
    onAction,
    icon: Icon
}: EmptyStateProps) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center justify-center py-20 px-6 text-center border border-dashed rounded-3xl bg-muted/10"
        >
            <div className="h-16 w-16 rounded-2xl bg-muted/20 flex items-center justify-center mb-6">
                {Icon ? <Icon className="h-8 w-8 text-muted-foreground/40" /> : <Plus className="h-8 w-8 text-muted-foreground/40" />}
            </div>

            <h3 className="text-xl font-display font-semibold tracking-tight text-foreground mb-2">
                {title}
            </h3>

            <p className="text-sm text-muted-foreground font-sans max-w-[280px] mb-8 leading-relaxed">
                {description}
            </p>

            {actionLabel && onAction && (
                <Button
                    onClick={onAction}
                    className="rounded-xl bg-foreground text-background hover:bg-foreground/90 h-11 px-8 font-sans font-medium tracking-tight"
                >
                    <Plus className="w-4 h-4 mr-2" /> {actionLabel}
                </Button>
            )}
        </motion.div>
    );
}
