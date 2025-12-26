'use client';

import React from 'react';
import { RadarMode } from './types';
import { cn } from '@/lib/utils';
import { ChevronDownIcon, FilterIcon, ZapIcon } from '@/components/ui/Icons';
import { Button } from '@/components/ui/button';
import { scanRecon, generateDossier } from '@/lib/radar';
import { toast } from 'sonner';

interface RadarHeaderProps {
    mode: RadarMode;
    setMode: (mode: RadarMode) => void;
    selectedIcpId: string;
    setSelectedIcpId: (id: string) => void;
    onScanClick: () => void;
}

export function RadarHeader({ mode, setMode, selectedIcpId, setSelectedIcpId, onScanClick }: RadarHeaderProps) {
    const [isScanning, setIsScanning] = React.useState(false);

    const handleScanClick = async () => {
        if (isScanning) return;
        
        setIsScanning(true);
        try {
            toast.loading('Starting radar scan...', { id: 'header-scan' });
            
            const signals = await scanRecon(selectedIcpId);
            
            toast.success('Scan completed!', { 
                id: 'header-scan',
                description: `Found ${signals.length} new signals` 
            });
            
            onScanClick();
            
        } catch (error) {
            toast.error('Scan failed', { 
                id: 'header-scan',
                description: error instanceof Error ? error.message : 'Unknown error'
            });
        } finally {
            setIsScanning(false);
        }
    };

    const handleGenerateDossier = async () => {
        try {
            toast.loading('Generating dossier...', { id: 'header-dossier' });
            
            const dossier = await generateDossier('campaign-123');
            
            toast.success('Dossier generated!', { 
                id: 'header-dossier',
                description: `Created "${dossier[0]?.title}"` 
            });
            
        } catch (error) {
            toast.error('Dossier generation failed', { 
                id: 'header-dossier',
                description: error instanceof Error ? error.message : 'Unknown error'
            });
        }
    };
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

                    {/* Primary Actions */}
                    <Button onClick={handleScanClick} disabled={isScanning} size="sm" className="ml-2 h-9 px-4 gap-2 text-sm font-medium shadow-sm">
                        <ZapIcon size={14} />
                        {isScanning ? 'Scanning...' : 'New Scan'}
                    </Button>
                    <Button onClick={handleGenerateDossier} variant="outline" size="sm" className="ml-2 h-9 px-4 gap-2 text-sm font-medium">
                        Generate Dossier
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
