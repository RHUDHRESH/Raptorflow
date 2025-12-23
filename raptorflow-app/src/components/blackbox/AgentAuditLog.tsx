'use client';

import React, { useState } from 'react';
import { Terminal, Search, ChevronRight, ChevronDown, Cpu, Clock, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export interface AuditEntry {
    id: string;
    agent_id: string;
    move_id: string;
    trace: {
        input?: any;
        output?: any;
        error?: string;
        status?: string;
    };
    tokens: number;
    latency: number;
    timestamp: string;
}

interface AgentAuditLogProps {
    entries: AuditEntry[];
    isLoading?: boolean;
}

export function AgentAuditLog({ entries, isLoading }: AgentAuditLogProps) {
    const [expandedId, setExpandedId] = useState<string | null>(null);
    const [filter, setFilter] = useState('');

    const filteredEntries = entries.filter(e =>
        e.agent_id.toLowerCase().includes(filter.toLowerCase()) ||
        e.id.toLowerCase().includes(filter.toLowerCase())
    );

    if (isLoading) {
        return (
            <div className="space-y-2">
                {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="h-12 bg-muted rounded-lg animate-pulse" />
                ))}
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                    placeholder="Filter by Agent ID..."
                    className="pl-9 bg-muted/50 border-border rounded-xl font-sans text-sm"
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                />
            </div>

            <div className="border border-border rounded-2xl overflow-hidden bg-card">
                <div className="grid grid-cols-12 gap-4 px-4 py-3 bg-muted/30 border-b border-border text-[10px] font-semibold uppercase tracking-widest text-muted-foreground font-sans">
                    <div className="col-span-1">Status</div>
                    <div className="col-span-4">Agent</div>
                    <div className="col-span-3">Timestamp</div>
                    <div className="col-span-2 text-right">Tokens</div>
                    <div className="col-span-2 text-right">Latency</div>
                </div>

                <div className="divide-y divide-border">
                    {filteredEntries.map((entry) => {
                        const isExpanded = expandedId === entry.id;
                        const isError = entry.trace.status === 'failed' || !!entry.trace.error;

                        return (
                            <div key={entry.id} className="group">
                                <button
                                    onClick={() => setExpandedId(isExpanded ? null : entry.id)}
                                    className="w-full grid grid-cols-12 gap-4 px-4 py-3 items-center hover:bg-muted/20 transition-colors text-left font-sans"
                                >
                                    <div className="col-span-1 flex justify-center">
                                        <div className={cn(
                                            "h-2 w-2 rounded-full",
                                            isError ? "bg-red-500 animate-pulse" : "bg-emerald-500"
                                        )} />
                                    </div>
                                    <div className="col-span-4 flex items-center gap-2">
                                        <Cpu size={14} className="text-muted-foreground" />
                                        <span className="text-sm font-medium truncate">{entry.agent_id}</span>
                                    </div>
                                    <div className="col-span-3 text-xs text-muted-foreground">
                                        {new Date(entry.timestamp).toLocaleTimeString()}
                                    </div>
                                    <div className="col-span-2 text-right text-xs font-mono text-muted-foreground">
                                        {entry.tokens}
                                    </div>
                                    <div className="col-span-2 text-right text-xs font-mono text-muted-foreground">
                                        {entry.latency.toFixed(2)}s
                                    </div>
                                </button>

                                {isExpanded && (
                                    <div className="px-4 pb-4 pt-1 bg-muted/10 space-y-4">
                                        <div className="p-4 rounded-xl bg-black/[0.02] dark:bg-white/[0.02] border border-border/50 space-y-3">
                                            <div>
                                                <h5 className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mb-1 flex items-center gap-1.5">
                                                    <Terminal size={10} /> Input
                                                </h5>
                                                <pre className="text-xs font-mono p-3 rounded-lg bg-black/5 dark:bg-white/5 overflow-x-auto whitespace-pre-wrap max-h-40">
                                                    {JSON.stringify(entry.trace.input, null, 2)}
                                                </pre>
                                            </div>
                                            <div>
                                                <h5 className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mb-1 flex items-center gap-1.5">
                                                    <Zap size={10} /> Output
                                                </h5>
                                                <pre className={cn(
                                                    "text-xs font-mono p-3 rounded-lg overflow-x-auto whitespace-pre-wrap max-h-60",
                                                    isError ? "bg-red-500/5 text-red-500/80" : "bg-black/5 dark:bg-white/5"
                                                )}>
                                                    {JSON.stringify(isError ? entry.trace.error : entry.trace.output, null, 2)}
                                                </pre>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-4 text-[10px] text-muted-foreground font-mono">
                                            <span className="flex items-center gap-1"><Clock size={10} /> ID: {entry.id}</span>
                                            <span className="flex items-center gap-1"><Terminal size={10} /> MOVE: {entry.move_id}</span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
