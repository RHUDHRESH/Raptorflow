'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { FadeIn } from '@/components/ui/motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useRouter } from 'next/navigation';
import {
  Search,
  LayoutGrid,
  List,
  Filter,
  Inbox,
  ArrowUpRight,
} from 'lucide-react';
import { useCampaigns } from '@/hooks/useCampaigns';
import { CampaignCard } from '@/components/campaigns/CampaignCard';
import { MoveCard } from '@/components/moves/MoveCard';
import { EditCampaignDialog } from '@/components/campaigns/EditCampaignDialog';
import { MoveCampaignWizard } from '@/components/moves/MoveCampaignWizard';
import { getUncategorizedMoves, getMovesByCampaign, getCampaignProgress } from '@/lib/campaigns';
import { Campaign, Move } from '@/lib/campaigns-types';
import { toast } from 'sonner';
import { AnimatePresence, motion } from 'framer-motion';

// Filter Types
type ViewMode = 'grid' | 'list';
type StatusFilter = 'all' | 'active' | 'planned' | 'completed';
type TimeFilter = 'all' | 'week' | 'month';

export default function Dashboard() {
  const router = useRouter();
  const { campaigns, refresh: refreshCampaigns } = useCampaigns(10000); // Poll every 10s
  const [uncategorizedMoves, setUncategorizedMoves] = useState<Move[]>([]);
  const [campaignMeta, setCampaignMeta] = useState<Record<string, { progress: number; moves: Move[] }>>({});

  // UI State
  const [isWizardOpen, setIsWizardOpen] = useState(false);
  const [editingCampaign, setEditingCampaign] = useState<Campaign | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');

  // Filters
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('active');
  const [timeFilter, setTimeFilter] = useState<TimeFilter>('all');

  // Fetch initial data
  const fetchData = useCallback(async () => {
    // 1. Uncategorized Moves
    const inbox = await getUncategorizedMoves();
    setUncategorizedMoves(inbox);

    // 2. Campaign Metadata (Moves + Progress)
    const meta: Record<string, any> = {};
    for (const c of campaigns) {
      const [moves, stats] = await Promise.all([
        getMovesByCampaign(c.id),
        getCampaignProgress(c.id)
      ]);
      const progress = stats.totalMoves > 0
        ? Math.round((stats.completedMoves / stats.totalMoves) * 100)
        : 0;

      meta[c.id] = { moves, progress };
    }
    setCampaignMeta(meta);
  }, [campaigns]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    const handleNewMove = () => setIsWizardOpen(true);
    const handleNewCampaign = () => setIsWizardOpen(true);

    window.addEventListener('rf:new-move', handleNewMove);
    window.addEventListener('rf:new-campaign', handleNewCampaign);

    return () => {
      window.removeEventListener('rf:new-move', handleNewMove);
      window.removeEventListener('rf:new-campaign', handleNewCampaign);
    };
  }, []);

  const handleRefresh = async () => {
    await refreshCampaigns();
    await fetchData();
  };

  // ------------------------------------------
  // Interactions
  // ------------------------------------------
  const handleEditCampaign = (c: Campaign) => setEditingCampaign(c);

  const handleDeleteCampaign = async (c: Campaign) => {
    if (!confirm(`Delete campaign "${c.name}"? This cannot be undone.`)) return;
    // Call API to delete (assuming deleteCampaign exists in lib/campaigns)
    // await deleteCampaign(c.id);
    toast.error("Delete not implemented yet (safety check)");
  };

  const handleArchiveCampaign = async (c: Campaign) => {
    toast.success(`Archived ${c.name}`);
  };

  const handleMoveClick = (m: Move) => {
    router.push(`/moves/${m.id}`);
  };

  // ------------------------------------------
  // Filtering Logic
  // ------------------------------------------
  const filteredCampaigns = campaigns.filter(c => {
    const matchesSearch = c.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all'
      ? c.status !== 'archived'
      : c.status === statusFilter;

    // Time filter logic (placeholder)
    const matchesTime = true;

    return matchesSearch && matchesStatus && matchesTime;
  });

  const filteredInbox = uncategorizedMoves.filter(m =>
    m.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <AppLayout>
      <div className="max-w-[1600px] mx-auto p-6 space-y-8 pb-32">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <h1 className="font-display text-4xl text-ink font-medium tracking-tight">
              Mission Control
            </h1>
            <p className="text-secondary-text mt-2 font-light">
              Overview of all active campaigns and tactical moves.
            </p>
          </div>
        <div className="flex items-center gap-3">
          <div className="relative group">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-secondary-text group-focus-within:text-ink transition-colors" />
            <Input
              placeholder="Search..."
              className="pl-9 w-64 bg-surface border-border focus:border-ink transition-all"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </div>

        {/* Filter Strip */}
        <div className="flex flex-wrap items-center justify-between gap-4 py-4 border-b border-border/40">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-secondary-text mr-2" />
            <FilterPill
              label="Active"
              active={statusFilter === 'active'}
              onClick={() => setStatusFilter('active')}
            />
            <FilterPill
              label="Planned"
              active={statusFilter === 'planned'}
              onClick={() => setStatusFilter('planned')}
            />
            <FilterPill
              label="Completed"
              active={statusFilter === 'completed'}
              onClick={() => setStatusFilter('completed')}
            />
            <div className="w-px h-4 bg-border mx-2" />
            <FilterPill
              label="All Campaigns"
              active={statusFilter === 'all'}
              onClick={() => setStatusFilter('all')}
            />
          </div>

          <div className="flex items-center gap-1 bg-surface p-1 rounded-lg border border-border">
            <Button
              variant="ghost"
              size="sm"
              className={`h-7 px-2 ${viewMode === 'grid' ? 'bg-white shadow-sm text-ink' : 'text-secondary-text'}`}
              onClick={() => setViewMode('grid')}
            >
              <LayoutGrid className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className={`h-7 px-2 ${viewMode === 'list' ? 'bg-white shadow-sm text-ink' : 'text-secondary-text'}`}
              onClick={() => setViewMode('list')}
            >
              <List className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* INBOX SECTION */}
        {filteredInbox.length > 0 && (
          <section className="space-y-4">
            <div className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-secondary-text">
              <Inbox className="w-4 h-4" />
              <span>Inbox ({filteredInbox.length})</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filteredInbox.map(move => (
                <MoveCard
                  key={move.id}
                  move={move}
                  onClick={() => handleMoveClick(move)}
                  className="bg-surface hover:bg-canvas-card border-border/60"
                />
              ))}
            </div>
          </section>
        )}

        {/* CAMPAIGNS SECTION */}
        <section className="space-y-6">
          {filteredCampaigns.length === 0 ? (
            <div className="py-20 text-center rounded-3xl border border-dashed border-border bg-surface/30">
              <p className="text-secondary-text mb-4">No campaigns found matching your filters.</p>
              <Button variant="outline" onClick={() => setStatusFilter('all')}>Clear Filters</Button>
            </div>
          ) : (
            <div className={`grid gap-6 ${viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 xl:grid-cols-2' : 'grid-cols-1'}`}>
              <AnimatePresence>
                {filteredCampaigns.map((campaign, i) => (
                  <FadeIn key={campaign.id} delay={i * 0.1}>
                    <CampaignCard
                      campaign={campaign}
                      moves={campaignMeta[campaign.id]?.moves || []}
                      progress={campaignMeta[campaign.id]?.progress || 0}
                      activeMove={campaignMeta[campaign.id]?.moves?.find(m => m.status === 'active')}
                      onEdit={handleEditCampaign}
                      onDelete={handleDeleteCampaign}
                      onArchive={handleArchiveCampaign}
                      onMoveClick={handleMoveClick}
                    />
                  </FadeIn>
                ))}
              </AnimatePresence>
            </div>
          )}
        </section>

      </div>

      {/* Modals */}
      <MoveCampaignWizard
        open={isWizardOpen}
        onClose={() => setIsWizardOpen(false)}
        onSuccess={handleRefresh}
      />

      <EditCampaignDialog
        open={!!editingCampaign}
        onOpenChange={(open) => !open && setEditingCampaign(null)}
        campaign={editingCampaign}
        moves={editingCampaign ? (campaignMeta[editingCampaign.id]?.moves || []) : []}
        onSuccess={handleRefresh}
      />
    </AppLayout>
  );
}

function FilterPill({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`
        px-3 py-1.5 rounded-full text-xs font-medium transition-all
        ${active
          ? 'bg-ink text-canvas shadow-sm'
          : 'bg-surface text-secondary-text hover:bg-surface/80 hover:text-ink'
        }
      `}
    >
      {label}
    </button>
  );
}
