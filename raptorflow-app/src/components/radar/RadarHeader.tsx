'use client';

import React from 'react';
import { RadarMode } from './types';
import { cn } from '@/lib/utils';
import { ChevronDownIcon, FilterIcon, ZapIcon } from '@/components/ui/icons';
import { Button } from '@/components/ui/button';

interface RadarHeaderProps {
    mode: RadarMode;
    setMode: (mode: RadarMode) => void;
    selectedIcpId: string;
    setSelectedIcpId: (id: string) => void;
    onScanClick: () => void;
}

export function RadarHeader({ mode, setMode, selectedIcpId, setSelectedIcpId, onScanClick }: RadarHeaderProps) {
    return (
        <div className="flex flex-col gap-8">
            {/* Title Row */}
            <div className="flex items-end justify-between">
                <div>
                    <h1 className="font-display text-4xl font-semibold text-primary tracking-tight">
                        Radar
                    </h1>
                    <p className="text-muted-foreground mt-2 text-base font-sans">
                        Signal for your ICPs. Turn it into posts or moves.
                    </p>
                </div>

                {/* Filters (Abstract placeholder for now) */}
                <div className="flex items-center gap-3">
                    <Button variant="outline" size="sm" className="h-9 gap-2 text-muted-foreground border-border hover:text-foreground">
                        <FilterIcon size={14} />
                        Filters
                    </Button>
                    <Button variant="outline" size="sm" className="h-9 gap-2 text-muted-foreground border-border hover:text-foreground">
                        Last 7d <ChevronDownIcon size={12} className="opacity-50" />
                    </Button>

                    {/* Primary Action */}
                    <Button onClick={onScanClick} size="sm" className="ml-2 h-9 px-4 gap-2 text-sm font-medium shadow-sm">
                        <ZapIcon size={14} />
                        New Scan
                    </Button>
                </div>
            </div>

            {/* Controls Row */}
            <div className="flex items-center justify-between border-b border-border/40 pb-0">

                {/* Mode Switch (Underline Tabs) */}
                <div className="flex items-center gap-8 relative top-[1px]">
                    <button
                        onClick={() => setMode('recon')}
                        className={cn(
                            "pb-3 text-sm font-medium transition-all duration-200 border-b-2",
                            mode === 'recon'
                                ? "text-foreground border-foreground"
                                : "text-muted-foreground border-transparent hover:text-foreground/80"
                        )}
                    >
                        Recon
                        <span className="ml-2 text-xs opacity-50 font-normal">Fast signals</span>
                    </button>

                    <button
                        onClick={() => setMode('dossier')}
                        className={cn(
                            "pb-3 text-sm font-medium transition-all duration-200 border-b-2",
                            mode === 'dossier'
                                ? "text-foreground border-foreground"
                                : "text-muted-foreground border-transparent hover:text-foreground/80"
                        )}
                    >
                        Dossier
                        <span className="ml-2 text-xs opacity-50 font-normal">Deep briefs</span>
                    </button>
                </div>

                {/* ICP Selector (Simplified) */}
                <div className="pb-2">
                    <button className="flex items-center gap-2 text-sm font-medium text-foreground bg-secondary/50 hover:bg-secondary px-3 py-1.5 rounded-md transition-colors">
                        <span className="text-muted-foreground">Target:</span>
                        Early-stage Founders
                        <ChevronDownIcon size={12} className="opacity-50" />
                    </button>
                </div>
            </div>
        </div>
    );
}
