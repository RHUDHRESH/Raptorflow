'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import {
  RadarTab,
  Watchlist,
  Alert,
  Competitor,
  MOCK_RADAR_STATUS,
} from '@/components/radar/types';
import { AlertFeed } from '@/components/radar/alerts/AlertFeed';
import { WatchlistCard } from '@/components/radar/WatchlistCard';
import { RadarStatusWidget } from '@/components/radar/RadarStatusWidget';
import { WatchlistWizard } from '@/components/radar/WatchlistWizard';
import { ArrowRight, Plus, Sparkles, Search } from 'lucide-react';
import { toast } from 'sonner';
import {
  scanRecon,
  generateDossier,
} from '@/lib/radar';
import { useFoundation } from '@/context/FoundationProvider';

// Helper to generate watchlists from Foundation data
function generateWatchlistsFromFoundation(competition: any): Watchlist[] {
  if (!competition?.direct?.length) return [];

  const competitors: Competitor[] = competition.direct.map(
    (c: any, idx: number) => ({
      id: `comp-foundation-${idx}`,
      name: c.name,
      website: `https://${c.name.toLowerCase().replace(/\s+/g, '')}.com`,
      sources: [
        {
          id: `src-${idx}-1`,
          type: 'url' as const,
          name: 'Website',
          value: `https://${c.name.toLowerCase().replace(/\s+/g, '')}.com`,
          health: 90,
        },
      ],
      lastRecon: new Date(Date.now() - 1000 * 60 * 60 * 24),
      notes: `${c.strength} | Weakness: ${c.weakness}`,
    })
  );

  return [
    {
      id: 'wl-foundation-1',
      name: 'Direct Competitors',
      description: 'Competitors from your Foundation data',
      type: 'competitors',
      competitors,
      signalTypes: ['pricing', 'messaging', 'content'],
      scanFrequency: 'daily',
      lastScan: new Date(Date.now() - 1000 * 60 * 60 * 2),
      nextScan: new Date(Date.now() + 1000 * 60 * 60 * 4.5),
      status: 'active',
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7),
      updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 2),
    },
  ];
}

// Helper to generate alerts from Foundation battlecards
function generateAlertsFromFoundation(competition: any): Alert[] {
  if (!competition?.battlecards?.landmines?.length) return [];

  return competition.battlecards.landmines
    .slice(0, 3)
    .map((landmine: string, idx: number) => ({
      id: `alert-foundation-${idx}`,
      watchlistId: 'wl-foundation-1',
      watchlistName: 'Direct Competitors',
      competitorId: 'comp-foundation-0',
      competitorName: competition.direct?.[0]?.name || 'Competitor',
      type: 'messaging' as const,
      title: `Objection Pattern: "${landmine}"`,
      summary: `Common objection detected: "${landmine}". Prepare talk track response.`,
      impact: 'medium' as const,
      confidence: 'high' as const,
      evidence: [],
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * (idx + 1)),
      status: 'new' as const,
    }));
}

import { ReconScanner } from '@/components/radar/recon/ReconScanner';
import { SignalTable } from '@/components/radar/recon/SignalTable';
import { DossierDetail } from '@/components/radar/dossier/DossierDetail';
import { Signal, Dossier } from '@/components/radar/types';

export default function RadarPage() {
  const { getCompetition, isLoading: foundationLoading } = useFoundation();
  const competition = getCompetition();

  // Generate watchlists from Foundation
  const foundationWatchlists = useMemo(
    () => generateWatchlistsFromFoundation(competition),
    [competition]
  );

  // Generate alerts from Foundation
  const foundationAlerts = useMemo(
    () => generateAlertsFromFoundation(competition),
    [competition]
  );

  const [activeTab, setActiveTab] = useState<RadarTab | 'recon'>('recon');
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [reconSignals, setReconSignals] = useState<Signal[]>([]);
  const [showWizard, setShowWizard] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [currentDossier, setCurrentDossier] = useState<Dossier | null>(null);
  const [isDossierOpen, setIsDossierOpen] = useState(false);

  // Initialize with Foundation data
  useEffect(() => {
    if (foundationWatchlists.length > 0) {
      setWatchlists(foundationWatchlists);
    }
    if (foundationAlerts.length > 0) {
      setAlerts(foundationAlerts);
    }
  }, [foundationWatchlists, foundationAlerts]);

  // Get existing competitors for wizard
  const existingCompetitors = useMemo(
    () => competition?.direct?.map((c: any) => c.name) || [],
    [competition]
  );

  const handleDismissAlert = (id: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: 'dismissed' } : a))
    );
    toast.success('Alert dismissed');
  };

  const handleCreateMove = (alert: Alert) => {
    toast.success('Creating move...', {
      description: `Opening move wizard for: ${alert.title}`,
    });
  };

  const handleRunRecon = async (icpId: string, urls: string[]) => {
    if (isScanning) return;

    setIsScanning(true);
    try {
      toast.loading('Scanning market intelligence...', { id: 'recon' });
      const signals = await scanRecon(icpId, urls);
      setReconSignals(signals);
      toast.success('Recon completed!', {
        id: 'recon',
        description: `Identified ${signals.length} strategic signals.`,
      });
    } catch (error) {
      toast.error('Recon scan failed', {
        id: 'recon',
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    } finally {
      setIsScanning(false);
    }
  };

  const handleGenerateDossier = async (signalIds: string[]) => {
    try {
      toast.loading('Compiling intelligence dossier...', { id: 'dossier' });
      const dossier = await generateDossier('default-campaign', signalIds);
      setCurrentDossier(dossier[0]);
      setIsDossierOpen(true);
      toast.success('Dossier generated!', {
        id: 'dossier',
        description: `Created "${dossier[0]?.title}"`,
      });
    } catch (error) {
      toast.error('Dossier compilation failed', {
        id: 'dossier',
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  };

  const handleWatchlistComplete = (
    watchlist: Omit<Watchlist, 'id' | 'createdAt' | 'updatedAt'>
  ) => {
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
  if (!hasWatchlists && !showWizard && activeTab !== 'recon') {
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
              Monitor competitors. Track pricing changes. Catch messaging
              updates before they matter. Create your first watchlist to begin.
            </p>
            <div className="flex gap-4 justify-center">
              <button
                onClick={() => setActiveTab('recon')}
                className="inline-flex items-center gap-3 h-14 px-8 border border-[#C0C1BE] text-[#2D3538] rounded-2xl font-medium text-[15px] transition-all hover:bg-white"
              >
                Start Recon
              </button>
              <button
                onClick={() => setShowWizard(true)}
                className="inline-flex items-center gap-3 h-14 px-8 bg-[#1A1D1E] text-white rounded-2xl font-medium text-[15px] transition-all hover:bg-black hover:shadow-[0_12px_32px_rgba(0,0,0,0.15)]"
              >
                Create First Watchlist
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
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
        existingCompetitors={existingCompetitors}
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
            {(['recon', 'alerts', 'watchlists'] as (RadarTab | 'recon')[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`pb-5 text-[15px] font-medium transition-colors border-b-2 -mb-[1px] capitalize ${activeTab === tab
                  ? 'text-[#2D3538] border-[#2D3538]'
                  : 'text-[#9D9F9F] border-transparent hover:text-[#5B5F61]'
                  }`}
              >
                {tab === 'recon' ? 'Recon' : tab}
                {tab === 'alerts' &&
                  alerts.filter((a) => a.status === 'new').length > 0 && (
                    <span className="ml-3 text-[12px] text-[#9D9F9F]">
                      {alerts.filter((a) => a.status === 'new').length}
                    </span>
                  )}
              </button>
            ))}
          </nav>

          {/* Content Grid */}
          <div className="grid grid-cols-12 gap-16 px-4">
            {/* Main Content */}
            <main className="col-span-8">
              {activeTab === 'recon' && (
                <div className="space-y-12">
                  <ReconScanner onScan={handleRunRecon} isLoading={isScanning} />

                  {reconSignals.length > 0 && (
                    <div className="space-y-6">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-xl bg-white border border-[#C0C1BE] flex items-center justify-center">
                          <Sparkles className="w-5 h-5 text-[#D7C9AE]" />
                        </div>
                        <h2 className="font-serif text-2xl text-[#2D3538]">
                          Strategic Signals
                        </h2>
                      </div>
                      <SignalTable
                        signals={reconSignals}
                        onPin={(id) => setReconSignals(prev => prev.map(s => s.id === id ? { ...s, isSaved: true } : s))}
                        onUnpin={(id) => setReconSignals(prev => prev.map(s => s.id === id ? { ...s, isSaved: false } : s))}
                        onAddNote={(id) => toast.info('Adding note coming soon')}
                        onGenerateDossier={handleGenerateDossier}
                      />
                    </div>
                  )}

                  {reconSignals.length === 0 && !isScanning && (
                    <div className="flex flex-col items-center justify-center py-20 bg-white/50 border border-dashed border-[#C0C1BE] rounded-3xl">
                      <div className="w-12 h-12 rounded-full bg-[#F3F4EE] flex items-center justify-center mb-4">
                        <Search className="w-5 h-5 text-[#9D9F9F]" />
                      </div>
                      <h3 className="text-[#2D3538] font-medium">No active recon signals.</h3>
                      <p className="text-[14px] text-[#5B5F61] mt-1">Initiate a scan to populate intelligence.</p>
                    </div>
                  )}
                </div>
              )}

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
                      onRunRecon={(id) =>
                        toast.info(`Running recon on ${wl.name}`)
                      }
                    />
                  ))}
                </div>
              )}

            </main>

            {/* Sidebar */}
            <aside className="col-span-4">
              <div className="sticky top-12">
                <RadarStatusWidget
                  status={MOCK_RADAR_STATUS}
                  onAddWatchlist={() => setShowWizard(true)}
                  onAddCompetitor={() =>
                    toast.info('Add competitor coming soon')
                  }
                  onAddSource={() => toast.info('Add source coming soon')}
                />
              </div>
            </aside>
          </div>
        </div>
      </div>
      <DossierDetail
        open={isDossierOpen}
        onClose={() => setIsDossierOpen(false)}
        dossier={currentDossier}
        onConvertToMove={(d) => toast.success('Converting to move...')}
      />
    </AppLayout>
  );
}
