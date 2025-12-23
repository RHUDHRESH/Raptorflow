'use client';

import React, { useState } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { RadarHeader } from '@/components/radar/RadarHeader';
import { RadarScanner } from '@/components/radar/RadarScanner';
import { ScanConfigurationDialog, ScanConfig } from '@/components/radar/ScanConfigurationDialog';
import { ReconFeed } from '@/components/radar/recon/ReconFeed';
import { DossierFeed } from '@/components/radar/dossier/DossierFeed';
import { CompetitorRadar } from '@/components/foundation/CompetitorRadar';
import { RadarMode, Signal, Dossier } from '@/components/radar/types';
import { scanRecon, generateDossier } from '@/lib/radar';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

const MOCK_RADAR_DATA = [
    { subject: 'Speed', A: 85, B: 60, fullMark: 100 },
    { subject: 'Clarity', A: 90, B: 40, fullMark: 100 },
    { subject: 'Proof', A: 65, B: 80, fullMark: 100 },
    { subject: 'Control', A: 75, B: 55, fullMark: 100 },
    { subject: 'Momentum', A: 80, B: 70, fullMark: 100 },
];

export default function RadarPage() {
    const [mode, setMode] = useState<RadarMode>('recon');
    const [selectedIcpId, setSelectedIcpId] = useState<string>('default');
    const [scanStatus, setScanStatus] = useState<'idle' | 'scanning' | 'results'>('results');
    const [isScanDialogOpen, setIsScanDialogOpen] = useState(false);

    const [signals, setSignals] = useState<Signal[]>([]);
    const [dossiers, setDossiers] = useState<Dossier[]>([]);

    const handleOpenScanDialog = () => {
        setIsScanDialogOpen(true);
    };

    const handleStartScan = async (config: ScanConfig) => {
        setMode(config.mode);
        setScanStatus('scanning');

        try {
            if (config.mode === 'recon') {
                const results = await scanRecon(selectedIcpId);
                setSignals(results);
            } else {
                const results = await generateDossier(selectedIcpId);
                setDossiers(results);
            }
        } catch (error) {
            console.error("Scan failed:", error);
            toast.error("Radar scan failed. Ensure backend is running.");
            setScanStatus('idle');
        }
    };

    const handleScanComplete = () => {
        setScanStatus('results');
    };

    return (
        <AppLayout>
            <div className="min-h-screen bg-background text-foreground animate-in fade-in duration-500">
                <div className="max-w-[1200px] mx-auto px-12 py-12">

                    <RadarHeader
                        mode={mode}
                        setMode={setMode}
                        selectedIcpId={selectedIcpId}
                        setSelectedIcpId={setSelectedIcpId}
                        onScanClick={handleOpenScanDialog}
                    />

                    <div className="mt-8 min-h-[400px]">
                        {scanStatus === 'scanning' ? (
                            <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center">
                                <div className="w-full max-w-3xl">
                                    <RadarScanner status="scanning" onScanComplete={handleScanComplete} />
                                </div>
                            </div>
                        ) : (
                            <div className="animate-in slide-in-from-bottom-4 duration-700 fade-in grid grid-cols-1 lg:grid-cols-12 gap-12">
                                <div className="lg:col-span-7">
                                    {mode === 'recon' ? (
                                        <ReconFeed signals={signals} />
                                    ) : (
                                        <DossierFeed dossiers={dossiers} />
                                    )}
                                </div>

                                <div className="lg:col-span-5 space-y-8">
                                    <CompetitorRadar data={MOCK_RADAR_DATA} brandName="RaptorFlow" />

                                    <div className="p-6 rounded-2xl bg-muted/20 border border-border/40">
                                        <h4 className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground mb-4">
                                            Scanning Intelligence
                                        </h4>
                                        <p className="text-xs text-muted-foreground leading-relaxed">
                                            Our agents are currently monitoring 15+ competitor channels and 3 industry news aggregates.
                                            Signals are ranked by strategic impact score.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                <ScanConfigurationDialog
                    open={isScanDialogOpen}
                    onOpenChange={setIsScanDialogOpen}
                    initialMode={mode}
                    onStartScan={handleStartScan}
                />
            </div>
        </AppLayout>
    );
}
