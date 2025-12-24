'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Cpu, Brain, Loader2, PlayCircle, Layers, Zap } from 'lucide-react';

export interface AgentThread {
    id: string;
    agentName: string;
    task: string;
    status: 'thinking' | 'executing' | 'queued' | 'validating';
    startTime: string;
}

interface ActiveThreadsProps {
    threads: AgentThread[];
    className?: string;
}

export function ActiveThreads({ threads, className }: ActiveThreadsProps) {
    const getStatusIcon = (status: AgentThread['status']) => {
        switch (status) {
            case 'thinking': return <Brain className="h-3 w-3 animate-pulse text-blue-500" />;
            case 'executing': return <Cpu className="h-3 w-3 animate-spin duration-[3000ms] text-accent" />;
            case 'validating': return <Layers className="h-3 w-3 text-green-500" />;
            default: return <Loader2 className="h-3 w-3 text-muted-foreground" />;
        }
    };

    const getStatusColor = (status: AgentThread['status']) => {
        switch (status) {
            case 'thinking': return "bg-blue-50 text-blue-700";
            case 'executing': return "bg-accent/10 text-accent";
            case 'validating': return "bg-green-50 text-green-700";
            default: return "bg-muted text-muted-foreground";
        }
    };

    return (
        <div className={cn(
            "rounded-[24px] bg-card border border-border flex flex-col h-full overflow-hidden transition-all duration-300 shadow-sm",
            className
        )}>
            {/* Header */}
            <div className="p-6 border-b border-border/50 flex items-center justify-between bg-muted/5">
                <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-primary/5 flex items-center justify-center">
                        <Zap className="h-4 w-4 text-primary/60" />
                    </div>
                    <div>
                        <h3 className="text-[11px] font-bold uppercase tracking-[0.2em] text-foreground font-sans">
                            Active Agent Pool
                        </h3>
                        <span className="text-[10px] text-muted-foreground uppercase tracking-wider">
                            Distributed Intelligence
                        </span>
                    </div>
                </div>
                <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-primary/5 border border-primary/10">
                    <div className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse" />
                    <span className="text-[10px] font-mono font-bold text-primary">
                        {threads.length} ACTIVE
                    </span>
                </div>
            </div>

            {/* Thread List */}
            <div className="flex-1 overflow-y-auto p-6 space-y-3 custom-scrollbar">
                <AnimatePresence initial={false}>
                    {threads.map((thread, idx) => (
                        <motion.div
                            key={thread.id}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            transition={{ duration: 0.4, delay: idx * 0.05 }}
                            className="p-4 rounded-xl border border-border/50 bg-background/50 hover:bg-muted/5 transition-all group"
                        >
                            <div className="flex items-start justify-between mb-3">
                                <div className="flex flex-col gap-1">
                                    <span className="text-[10px] font-mono font-bold text-muted-foreground uppercase tracking-tighter opacity-60">
                                        ID: {thread.id}
                                    </span>
                                    <h4 className="text-sm font-sans font-bold text-foreground group-hover:text-accent transition-colors">
                                        {thread.agentName}
                                    </h4>
                                </div>
                                <div className={cn(
                                    "px-2 py-0.5 rounded-full flex items-center gap-1.5 border border-current/10",
                                    getStatusColor(thread.status)
                                )}>
                                    {getStatusIcon(thread.status)}
                                    <span className="text-[9px] font-bold uppercase tracking-wider">
                                        {thread.status}
                                    </span>
                                </div>
                            </div>

                            <div className="flex flex-col gap-3">
                                <div className="flex items-center gap-2">
                                    <div className="h-4 w-4 rounded bg-muted flex items-center justify-center">
                                        <PlayCircle className="h-2.5 w-2.5 text-muted-foreground" />
                                    </div>
                                    <p className="text-xs font-sans text-muted-foreground line-clamp-1">
                                        {thread.task}
                                    </p>
                                </div>

                                {/* Progress Bar Mini */}
                                <div className="h-1 w-full bg-muted rounded-full overflow-hidden">
                                    <motion.div
                                        className="h-full bg-accent"
                                        initial={{ width: "0%" }}
                                        animate={{ width: thread.status === 'executing' ? "65%" : "100%" }}
                                        transition={{ duration: 2, repeat: thread.status === 'executing' ? Infinity : 0 }}
                                    />
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {threads.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center py-12 text-center opacity-40">
                        <div className="h-12 w-12 rounded-full border border-dashed border-border flex items-center justify-center mb-4">
                            <Layers className="h-6 w-6 text-muted-foreground" />
                        </div>
                        <p className="text-xs text-muted-foreground font-sans">
                            Agent pool idle.<br/>
                            Awaiting strategic directives.
                        </p>
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="p-4 bg-muted/5 border-t border-border/50 flex items-center justify-between">
                <span className="text-[9px] font-mono text-muted-foreground uppercase">
                    Cluster: EU-WEST-1
                </span>
                <span className="text-[9px] font-mono text-muted-foreground uppercase">
                    Latency: 42ms
                </span>
            </div>
        </div>
    );
}
