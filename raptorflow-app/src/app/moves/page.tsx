'use client';

import React, { useState, useMemo, useEffect } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { InferenceErrorBoundary } from '@/components/layout/InferenceErrorBoundary';
import { Move, Campaign } from '@/lib/campaigns-types';
import { MoveCampaignWizard } from '@/components/moves/MoveCampaignWizard';
import { CampaignCard } from '@/components/campaigns/CampaignCard';
import { CampaignEditModal } from '@/components/campaigns/CampaignEditModal';
import { MoveCard } from '@/components/moves/MoveCard';
import { MoveDetail } from '@/components/moves/MoveDetail';
import { RationaleDrawer } from '@/components/moves/RationaleDrawer';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@/components/ui/dropdown-menu';
import {
  Plus,
  Search,
  Filter,
  Inbox,
  Target,
  SlidersHorizontal,
  Calendar,
  Tag,
  ChevronDown,
} from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import {
  deleteCampaign,
  getCampaigns,
  getMoves,
  getMove,
  toggleChecklistItem,
  updateCampaign,
  updateMove,
} from '@/lib/campaigns';
import { getMoveRationale } from '@/lib/api';

export default function UnifiedMovesPage() {
  // Data State
  const [moves, setMoves] = useState<Move[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [isLoadingData, setIsLoadingData] = useState(true);

  // Filter State
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [channelFilter, setChannelFilter] = useState<string>('all');

  // UI State
  const [isWizardOpen, setIsWizardOpen] = useState(false);
  const [wizardMode, setWizardMode] = useState<'move' | 'campaign'>('campaign');
  const [editingCampaign, setEditingCampaign] = useState<Campaign | null>(null);
  const [selectedMove, setSelectedMove] = useState<Move | null>(null);
  const [rationaleMove, setRationaleMove] = useState<Move | null>(null);
  const [moveRationale, setMoveRationale] = useState<any>(null);

  // Fetch Data
  const fetchData = async () => {
    setIsLoadingData(true);
    try {
      const [cData, mData] = await Promise.all([getCampaigns(), getMoves()]);
      setCampaigns(cData);
      setMoves(mData);
    } catch (error) {
      toast.error('Failed to load data');
      console.error(error);
    } finally {
      setIsLoadingData(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    const handleNewMove = () => {
      setWizardMode('move');
      setIsWizardOpen(true);
    };
    const handleNewCampaign = () => {
      setWizardMode('campaign');
      setIsWizardOpen(true);
    };

    window.addEventListener('rf:new-move', handleNewMove);
    window.addEventListener('rf:new-campaign', handleNewCampaign);

    return () => {
      window.removeEventListener('rf:new-move', handleNewMove);
      window.removeEventListener('rf:new-campaign', handleNewCampaign);
    };
  }, []);

  // Derived Logic
  const filteredMoves = useMemo(() => {
    return moves.filter((move) => {
      if (statusFilter !== 'all' && move.status !== statusFilter) return false;
      if (channelFilter !== 'all' && move.channel !== channelFilter)
        return false;
      return true;
    });
  }, [moves, statusFilter, channelFilter]);

  const { groupedMoves, inboxMoves } = useMemo(() => {
    const groups: Record<string, Move[]> = {};
    const inbox: Move[] = [];

    filteredMoves.forEach((move) => {
      if (move.campaignId) {
        if (!groups[move.campaignId]) groups[move.campaignId] = [];
        groups[move.campaignId].push(move);
      } else {
        inbox.push(move);
      }
    });

    return { groupedMoves: groups, inboxMoves: inbox };
  }, [filteredMoves]);

  // Handlers
  const handleCampaignUpdate = async (_updated: any) => {
    fetchData();
  };

  const handleDeleteCampaign = async (campaign: Campaign) => {
    try {
      await deleteCampaign(campaign.id);
      toast.success('Campaign archived.');
      fetchData();
    } catch (error) {
      toast.error('Failed to archive campaign.');
    }
  };

  const handleArchiveCampaign = async (campaign: Campaign) => {
    try {
      await updateCampaign({ ...campaign, status: 'archived' });
      toast.success('Campaign archived.');
      fetchData();
    } catch (error) {
      toast.error('Failed to archive campaign.');
    }
  };

  return (
    <AppLayout>
      <InferenceErrorBoundary>
        <div className="min-h-screen px-6 lg:px-12 py-8 pb-32">
          <div className="max-w-[1200px] mx-auto">
            {/* Header & Controls */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
              <div>
                <h1 className="font-serif text-[32px] text-[#2D3538] mb-1">
                  Mission Control
                </h1>
                <p className="text-[#9D9F9F] text-sm">
                  Orchestrate your campaigns and tactical moves.
                </p>
              </div>

              <div className="flex items-center gap-3">
                {/* Filters */}
                <div className="flex items-center gap-2 mr-2">
                  <select
                    className="h-10 pl-3 pr-8 rounded-xl border border-[#E5E6E3] bg-white text-sm text-[#5B5F61] focus:ring-1 focus:ring-[#2D3538]"
                    value={channelFilter}
                    onChange={(e) => setChannelFilter(e.target.value)}
                  >
                    <option value="all">All Channels</option>
                    <option value="linkedin">LinkedIn</option>
                    <option value="email">Email</option>
                    <option value="twitter">Twitter</option>
                  </select>
                  <select
                    className="h-10 pl-3 pr-8 rounded-xl border border-[#E5E6E3] bg-white text-sm text-[#5B5F61] focus:ring-1 focus:ring-[#2D3538]"
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                  >
                    <option value="all">All Status</option>
                    <option value="active">Active</option>
                    <option value="draft">Draft</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>

                {/* Main Action */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button className="bg-[#2D3538] text-white hover:bg-black rounded-xl h-11 px-6 shadow-md transition-all hover:scale-105 active:scale-95">
                      <Plus className="w-4 h-4 mr-2" />
                      New
                      <ChevronDown className="w-4 h-4 ml-2 opacity-50" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-48">
                    <DropdownMenuItem
                      onClick={() => {
                        setWizardMode('campaign');
                        setIsWizardOpen(true);
                      }}
                    >
                      <Target className="w-4 h-4 mr-2" />
                      New Campaign
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onClick={() => {
                        setWizardMode('move');
                        setIsWizardOpen(true);
                      }}
                    >
                      <Inbox className="w-4 h-4 mr-2" />
                      New Move
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>

            {isLoadingData ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              </div>
            ) : (
              <div className="space-y-12">
                {/* Section: Campaigns */}
                <section className="space-y-6">
                  <div className="flex items-center gap-2 mb-4 border-b border-[#E5E6E3] pb-2">
                    <Target className="w-4 h-4 text-[#9D9F9F]" />
                    <h2 className="text-[12px] font-semibold uppercase tracking-wider text-[#9D9F9F]">
                      Active Campaigns
                    </h2>
                  </div>

                  <div className="grid gap-6">
                    {campaigns
                      .filter((c) => c.status !== 'archived')
                      .map((campaign) => (
                        <CampaignCard
                          key={campaign.id}
                          campaign={campaign}
                          moves={groupedMoves[campaign.id] || []}
                          onEdit={setEditingCampaign}
                          onDelete={handleDeleteCampaign}
                          onArchive={handleArchiveCampaign}
                          onMoveClick={setSelectedMove}
                        />
                      ))}
                    {campaigns.length === 0 && (
                      <div className="text-center py-12 border border-dashed border-[#C0C1BE] rounded-2xl bg-[#FCFDFB]">
                        <p className="text-sm text-[#9D9F9F]">
                          No active campaigns. Start by creating a strategy.
                        </p>
                      </div>
                    )}
                  </div>
                </section>

                {/* Section: Inbox */}
                <section className="space-y-6">
                  <div className="flex items-center gap-2 mb-4 border-b border-[#E5E6E3] pb-2">
                    <Inbox className="w-4 h-4 text-[#9D9F9F]" />
                    <h2 className="text-[12px] font-semibold uppercase tracking-wider text-[#9D9F9F]">
                      Inbox / Unassigned ({inboxMoves.length})
                    </h2>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {inboxMoves.length > 0 ? (
                      inboxMoves.map((move) => (
                        <MoveCard
                          key={move.id}
                          move={move}
                          onClick={async () => {
                            const fullMove = await getMove(move.id);
                            setSelectedMove(fullMove || move);
                          }}
                          onLogProgress={() =>
                            toast.info('Progress logging coming soon')
                          }
                          onViewRationale={async () => {
                            try {
                              const rationale = await getMoveRationale(move.id);
                              setMoveRationale(rationale);
                              setRationaleMove(move);
                            } catch (error) {
                              toast.error('Unable to load rationale.');
                            }
                          }}
                          className="bg-white border-[#E5E6E3] hover:border-[#2D3538]/30"
                        />
                      ))
                    ) : (
                      <div className="col-span-full text-center py-12 border border-dashed border-[#C0C1BE] rounded-2xl bg-[#FCFDFB]">
                        <p className="text-sm text-[#9D9F9F]">
                          Inbox zero. All moves are assigned to campaigns.
                        </p>
                      </div>
                    )}
                  </div>
                </section>
              </div>
            )}

            {/* Modals & Overlays */}
            <MoveCampaignWizard
              open={isWizardOpen}
              onClose={() => setIsWizardOpen(false)}
              onSuccess={() => {
                setIsWizardOpen(false);
                toast.success('Strategy created successfully');
                fetchData();
              }}
            />

            <CampaignEditModal
              isOpen={!!editingCampaign}
              campaign={editingCampaign}
              moves={
                editingCampaign ? groupedMoves[editingCampaign.id] || [] : []
              }
              onClose={() => setEditingCampaign(null)}
              onSave={fetchData}
            />

            {selectedMove && (
              <MoveDetail
                move={selectedMove}
                rationale={moveRationale}
                open={!!selectedMove}
                onClose={() => setSelectedMove(null)}
                onUpdate={async (updates) => {
                  try {
                    const updatedMove = { ...selectedMove, ...updates };
                    await updateMove(updatedMove);
                    setSelectedMove(updatedMove);
                    fetchData();
                  } catch (error) {
                    toast.error('Failed to update move.');
                  }
                }}
                onToggleTask={async (taskId) => {
                  try {
                    await toggleChecklistItem(selectedMove.id, taskId);
                    const refreshed = await getMove(selectedMove.id);
                    setSelectedMove(refreshed || selectedMove);
                  } catch (error) {
                    toast.error('Failed to update task.');
                  }
                }}
              />
            )}

            {rationaleMove && (
              <RationaleDrawer
                isOpen={!!rationaleMove}
                onClose={() => setRationaleMove(null)}
                move={rationaleMove}
              />
            )}
          </div>
        </div>
      </InferenceErrorBoundary>
    </AppLayout>
  );
}
