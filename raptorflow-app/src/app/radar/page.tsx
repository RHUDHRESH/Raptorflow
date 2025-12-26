'use client';

import React, { useState, useEffect } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import {
    RadarTab,
    Watchlist,
    Alert,
    MOCK_WATCHLISTS,
    MOCK_ALERTS,
    MOCK_RADAR_STATUS,
} from '@/components/radar/types';
import { AlertFeed } from '@/components/radar/alerts/AlertFeed';
import { WatchlistCard } from '@/components/radar/WatchlistCard';
import { RadarStatusWidget } from '@/components/radar/RadarStatusWidget';
import { WatchlistWizard } from '@/components/radar/WatchlistWizard';
import { RadarAnalytics } from '@/components/radar/RadarAnalytics';
import { RadarScheduler } from '@/components/radar/RadarScheduler';
import { RadarNotifications } from '@/components/radar/RadarNotifications';
import { ArrowRight, Plus } from 'lucide-react';
import { toast } from 'sonner';
import { scanRecon, generateDossier, getSignalTrends, startScheduler, stopScheduler } from '@/lib/radar';

export default function RadarPage() {
    const [activeTab, setActiveTab] = useState<RadarTab>('alerts');
    const [watchlists, setWatchlists] = useState<Watchlist[]>(MOCK_WATCHLISTS);
    const [alerts, setAlerts] = useState<Alert[]>(MOCK_ALERTS);
    const [showWizard, setShowWizard] = useState(false);
    const [isScanning, setIsScanning] = useState(false);
    const [schedulerActive, setSchedulerActive] = useState(false);

    // Load scheduler status on mount
    useEffect(() => {
        // Could check scheduler status here
        // For now, default to inactive
    }, []);

    const handleDismissAlert = (id: string) => {
        setAlerts(prev => prev.map(a =>
            a.id === id ? { ...a, status: 'dismissed' } : a
        ));
        toast.success('Alert dismissed');
    };

    const handleCreateMove = (alert: Alert) => {
        toast.success('Creating move...', {
            description: `Opening move wizard for: ${alert.title}`,
        });
    };

    const handleRunScan = async () => {
        if (isScanning) return;
        
        setIsScanning(true);
        try {
            toast.loading('Starting radar scan...', { id: 'scan' });
            
            // Get sources from active watchlists
            const sourceUrls = [
                'https://competitor-a.com/pricing',
                'https://competitor-b.com',
                'https://linkedin.com/company/competitor-c'
            ];
            
            const signals = await scanRecon('default-icp', sourceUrls);
            
            toast.success('Scan completed!', { 
                id: 'scan',
                description: `Found ${signals.length} new signals` 
            });
            
            // Could update alerts state with new signals
            console.log('New signals:', signals);
            
        } catch (error) {
            toast.error('Scan failed', { 
                id: 'scan',
                description: error instanceof Error ? error.message : 'Unknown error'
            });
        } finally {
            setIsScanning(false);
        }
    };

    const handleGenerateDossier = async () => {
        try {
            toast.loading('Generating dossier...', { id: 'dossier' });
            
            const dossier = await generateDossier('campaign-123');
            
            toast.success('Dossier generated!', { 
                id: 'dossier',
                description: `Created "${dossier[0]?.title}"` 
            });
            
            console.log('Generated dossier:', dossier);
            
        } catch (error) {
            toast.error('Dossier generation failed', { 
                id: 'dossier',
                description: error instanceof Error ? error.message : 'Unknown error'
            });
        }
    };

    const handleToggleScheduler = async () => {
        try {
            if (schedulerActive) {
                await stopScheduler();
                setSchedulerActive(false);
                toast.success('Scheduler stopped');
            } else {
                await startScheduler();
                setSchedulerActive(true);
                toast.success('Scheduler started');
            }
        } catch (error) {
            toast.error('Scheduler operation failed', {
                description: error instanceof Error ? error.message : 'Unknown error'
            });
        }
    };

    const handleWatchlistComplete = (watchlist: Omit<Watchlist, 'id' | 'createdAt' | 'updatedAt'>) => {
        const newWatchlist: Watchlist = {
            ...watchlist,
            id: `wl-${Date.now()}`,
            createdAt: new Date(),
            updatedAt: new Date(),
        };
        setWatchlists([...watchlists, newWatchlist]);
        setShowWizard(false);
        toast.success('Watchlist created!', {
            description: `"${newWatchlist.name}" is now active.`,
        });
    };

    const hasWatchlists = watchlists.length > 0;

    // Empty State — Masterclass Minimal
    if (!hasWatchlists && !showWizard) {
        return (
            <AppLayout>
                <div className="min-h-[80vh] flex items-center justify-center px-8">
                    <div className="text-center max-w-lg">
                        <div className="w-20 h-20 mx-auto mb-8 rounded-2xl bg-[#F8F9F7] border border-[#E5E6E3] flex items-center justify-center">
                            <div className="w-3 h-3 rounded-full bg-[#2D3538]" />
                        </div>
                        <h1 className="font-serif text-4xl text-[#2D3538] mb-4 tracking-tight">
                            Competitive Radar
                        </h1>
                        <p className="text-[16px] text-[#5B5F61] mb-10 leading-relaxed max-w-md mx-auto">
                            Monitor competitors. Track pricing changes. Catch messaging updates before they matter. Create your first watchlist to begin.
                        </p>
                        <button
                            onClick={() => setShowWizard(true)}
                            className="inline-flex items-center gap-3 h-14 px-8 bg-[#1A1D1E] text-white rounded-2xl font-medium text-[15px] transition-all hover:bg-black hover:shadow-[0_12px_32px_rgba(0,0,0,0.15)]"
                        >
                            Create First Watchlist
                            <ArrowRight className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </AppLayout>
        );
    }

    // Wizard — Full Screen
    if (showWizard) {
        return (
            <WatchlistWizard
                onComplete={handleWatchlistComplete}
                onCancel={() => setShowWizard(false)}
                existingCompetitors={['Competitor X', 'Competitor Y', 'Competitor Z']}
            />
        );
    }

    // Main View
    return (
        <AppLayout fullBleed>
            <div className="min-h-screen bg-[#F8F9F7] px-12 lg:px-24 py-16">
                <div className="w-full">
                    {/* Header */}
                    <header className="flex items-end justify-between mb-20">
                        <div>
                            <h1 className="font-serif text-[44px] text-[#2D3538] tracking-tight leading-none">
                                Radar
                            </h1>
                            <p className="text-[16px] text-[#5B5F61] mt-3">
                                Competitive intelligence. Automated.
                            </p>
                        </div>
                        <div className="flex items-center gap-4">
                            <button
                                onClick={handleRunScan}
                                disabled={isScanning}
                                className={`h-11 px-5 rounded-xl text-[14px] font-medium transition-all ${
                                    isScanning 
                                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                                        : 'border border-[#C0C1BE] text-[#2D3538] hover:bg-white'
                                }`}
                            >
                                {isScanning ? 'Scanning...' : 'Run Scan'}
                            </button>
                            <button
                                onClick={handleGenerateDossier}
                                className="h-11 px-5 border border-[#C0C1BE] rounded-xl text-[14px] font-medium text-[#2D3538] hover:bg-white transition-colors"
                            >
                                Generate Dossier
                            </button>
                            <button
                                onClick={handleToggleScheduler}
                                className={`h-11 px-5 rounded-xl text-[14px] font-medium transition-all ${
                                    schedulerActive
                                        ? 'bg-red-50 text-red-600 border-red-200 hover:bg-red-100'
                                        : 'border border-[#C0C1BE] text-[#2D3538] hover:bg-white'
                                }`}
                            >
                                {schedulerActive ? 'Stop Scheduler' : 'Start Scheduler'}
                            </button>
                            <button
                                onClick={() => setShowWizard(true)}
                                className="inline-flex items-center gap-2 h-11 px-5 bg-[#1A1D1E] text-white rounded-xl text-[14px] font-medium transition-all hover:bg-black"
                            >
                                <Plus className="w-4 h-4" />
                                New Watchlist
                            </button>
                        </div>
                    </header>

                    {/* Navigation Tabs */}
                    <nav className="flex items-center gap-12 mb-12 border-b border-[#E5E6E3]">
                        {(['alerts', 'watchlists', 'sources', 'analytics', 'scheduler', 'notifications'] as RadarTab[]).map((tab) => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                className={`pb-5 text-[15px] font-medium transition-colors border-b-2 -mb-[1px] capitalize ${activeTab === tab
                                    ? 'text-[#2D3538] border-[#2D3538]'
                                    : 'text-[#9D9F9F] border-transparent hover:text-[#5B5F61]'
                                    }`}
                            >
                                {tab}
                                {tab === 'alerts' && alerts.filter(a => a.status === 'new').length > 0 && (
                                    <span className="ml-3 text-[12px] text-[#9D9F9F]">
                                        {alerts.filter(a => a.status === 'new').length}
                                    </span>
                                )}
                            </button>
                        ))}
                    </nav>

                    {/* Content Grid */}
                    <div className="grid grid-cols-12 gap-16 px-4">
                        {/* Main Content */}
                        <main className="col-span-8">
                            {activeTab === 'alerts' && (
                                <AlertFeed
                                    alerts={alerts}
                                    onDismiss={handleDismissAlert}
                                    onCreateMove={handleCreateMove}
                                />
                            )}

                            {activeTab === 'watchlists' && (
                                <div className="space-y-5">
                                    {watchlists.map((wl) => (
                                        <WatchlistCard
                                            key={wl.id}
                                            watchlist={wl}
                                            onView={(id) => {
                                                setActiveTab('alerts');
                                                toast.info(`Viewing alerts for ${wl.name}`);
                                            }}
                                            onEdit={(id) => toast.info(`Editing ${wl.name}`)}
                                            onRunRecon={(id) => toast.info(`Running recon on ${wl.name}`)}
                                        />
                                    ))}
                                </div>
                            )}

                            {activeTab === 'sources' && (
                                <div className="flex flex-col items-center justify-center py-24 text-center">
                                    <div className="w-16 h-16 rounded-2xl bg-white border border-[#E5E6E3] flex items-center justify-center mb-6">
                                        <div className="w-3 h-3 rounded-full bg-[#9D9F9F]" />
                                    </div>
                                    <h3 className="font-serif text-2xl text-[#2D3538] mb-2">Sources Hub</h3>
                                    <p className="text-[15px] text-[#5B5F61] max-w-sm">
                                        Manage all intelligence sources in one place. Coming soon.
                                    </p>
                                </div>
                            )}

                            {activeTab === 'analytics' && (
                                <RadarAnalytics />
                            )}

                            {activeTab === 'scheduler' && (
                                <RadarScheduler />
                            )}

                            {activeTab === 'notifications' && (
                                <RadarNotifications />
                            )}
                        </main>

                        {/* Sidebar */}
                        <aside className="col-span-4">
                            <div className="sticky top-12">
                                <RadarStatusWidget
                                    status={MOCK_RADAR_STATUS}
                                    onAddWatchlist={() => setShowWizard(true)}
                                    onAddCompetitor={() => toast.info('Add competitor coming soon')}
                                    onAddSource={() => toast.info('Add source coming soon')}
                                />
                            </div>
                        </aside>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
