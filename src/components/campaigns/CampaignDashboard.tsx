"use client";

import { useState, useEffect } from 'react';
import {
  Plus,
  Play,
  Pause,
  BarChart3,
  TrendingUp,
  Users,
  DollarSign,
  Calendar,
  Filter,
  Search,
  MoreVertical,
  Edit,
  Copy,
  Trash2,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle
} from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { useEnhancedCampaignStore } from '@/stores/enhancedCampaignStore';
import { Campaign, CampaignStatus } from '@/types/campaign';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

interface CampaignDashboardProps {
  onCreateCampaign?: () => void;
  onEditCampaign?: (id: string) => void;
  onViewCampaign?: (id: string) => void;
}

export function CampaignDashboard({
  onCreateCampaign,
  onEditCampaign,
  onViewCampaign
}: CampaignDashboardProps) {
  const campaigns = useEnhancedCampaignStore(state => Object.values(state.campaigns));
  const bulkUpdateStatus = useEnhancedCampaignStore(state => state.bulkUpdateStatus);
  const deleteCampaign = useEnhancedCampaignStore(state => state.deleteCampaign);
  const duplicateCampaign = useEnhancedCampaignStore(state => state.duplicateCampaign);

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<CampaignStatus | 'all'>('all');
  const [selectedCampaigns, setSelectedCampaigns] = useState<string[]>([]);
  const [showBulkActions, setShowBulkActions] = useState(false);

  // Filter campaigns
  const filteredCampaigns = campaigns.filter(campaign => {
    const matchesSearch = campaign.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      campaign.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || campaign.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // Calculate metrics
  const totalCampaigns = campaigns.length;
  const activeCampaigns = campaigns.filter(c => c.status === CampaignStatus.ACTIVE).length;
  const totalBudget = campaigns.reduce((sum, c) => sum + c.budget.total, 0);
  const totalSpent = campaigns.reduce((sum, c) => sum + c.budget.spent, 0);
  const totalConversions = campaigns.reduce((sum, c) => sum + c.analytics.overview.totalConversions, 0);
  const totalRevenue = campaigns.reduce((sum, c) => sum + c.analytics.overview.totalRevenue, 0);

  // Status configuration
  const statusConfig = {
    [CampaignStatus.DRAFT]: {
      label: 'Draft',
      color: 'bg-[var(--surface)] text-[var(--secondary)] border-[var(--border)]',
      icon: Edit
    },
    [CampaignStatus.PLANNING]: {
      label: 'Planning',
      color: 'bg-[var(--blueprint-light)] text-[var(--blueprint)] border-[var(--blueprint)]/20',
      icon: Clock
    },
    [CampaignStatus.ACTIVE]: {
      label: 'Active',
      color: 'bg-[var(--success-light)] text-[var(--success)] border-[var(--success)]/20',
      icon: Play
    },
    [CampaignStatus.PAUSED]: {
      label: 'Paused',
      color: 'bg-[var(--warning-light)] text-[var(--warning)] border-[var(--warning)]/20',
      icon: Pause
    },
    [CampaignStatus.COMPLETED]: {
      label: 'Completed',
      color: 'bg-[var(--accent-light)] text-[var(--accent)] border-[var(--accent)]/20',
      icon: CheckCircle
    },
    [CampaignStatus.CANCELLED]: {
      label: 'Cancelled',
      color: 'bg-[var(--error-light)] text-[var(--error)] border-[var(--error)]/20',
      icon: XCircle
    }
  };

  // Handle selection
  const handleSelectCampaign = (campaignId: string) => {
    setSelectedCampaigns(prev =>
      prev.includes(campaignId)
        ? prev.filter(id => id !== campaignId)
        : [...prev, campaignId]
    );
  };

  const handleSelectAll = () => {
    if (selectedCampaigns.length === filteredCampaigns.length) {
      setSelectedCampaigns([]);
    } else {
      setSelectedCampaigns(filteredCampaigns.map(c => c.id));
    }
  };

  // Quick actions
  const handleQuickAction = async (action: string, campaignId?: string) => {
    switch (action) {
      case 'activate':
        if (campaignId) {
          await bulkUpdateStatus([campaignId], CampaignStatus.ACTIVE);
        } else if (selectedCampaigns.length > 0) {
          await bulkUpdateStatus(selectedCampaigns, CampaignStatus.ACTIVE);
          setSelectedCampaigns([]);
        }
        break;
      case 'pause':
        if (campaignId) {
          await bulkUpdateStatus([campaignId], CampaignStatus.PAUSED);
        } else if (selectedCampaigns.length > 0) {
          await bulkUpdateStatus(selectedCampaigns, CampaignStatus.PAUSED);
          setSelectedCampaigns([]);
        }
        break;
      case 'duplicate':
        if (campaignId) {
          await duplicateCampaign(campaignId);
        }
        break;
      case 'delete':
        if (campaignId) {
          await deleteCampaign(campaignId);
        } else if (selectedCampaigns.length > 0) {
          await Promise.all(selectedCampaigns.map(id => deleteCampaign(id)));
          setSelectedCampaigns([]);
        }
        break;
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-[var(--structure-subtle)]">
        <div>
          <h1 className="text-2xl font-bold text-[var(--ink)]">Campaigns</h1>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Manage your marketing campaigns and track performance
          </p>
        </div>
        <BlueprintButton
          onClick={onCreateCampaign}
          className="flex items-center gap-2"
        >
          <Plus size={16} />
          New Campaign
        </BlueprintButton>
      </div>

      {/* Metrics Overview */}
      <div className="p-6 grid grid-cols-5 gap-4">
        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-[var(--ink-muted)] uppercase tracking-wide">Total Campaigns</p>
              <p className="text-2xl font-bold text-[var(--ink)] mt-1">{totalCampaigns}</p>
              <p className="text-xs text-[var(--success)] mt-1">+{activeCampaigns} active</p>
            </div>
            <div className="p-2 bg-[var(--blueprint-light)]/10 rounded">
              <BarChart3 size={20} className="text-[var(--blueprint)]" />
            </div>
          </div>
        </BlueprintCard>

        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-[var(--ink-muted)] uppercase tracking-wide">Total Budget</p>
              <p className="text-2xl font-bold text-[var(--ink)] mt-1">${totalBudget.toLocaleString()}</p>
              <p className="text-xs text-[var(--ink-muted)] mt-1">${totalSpent.toLocaleString()} spent</p>
            </div>
            <div className="p-2 bg-[var(--success-light)]/10 rounded">
              <DollarSign size={20} className="text-[var(--success)]" />
            </div>
          </div>
        </BlueprintCard>

        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-[var(--ink-muted)] uppercase tracking-wide">Conversions</p>
              <p className="text-2xl font-bold text-[var(--ink)] mt-1">{totalConversions.toLocaleString()}</p>
              <p className="text-xs text-[var(--success)] mt-1">+12% vs last month</p>
            </div>
            <div className="p-2 bg-[var(--warning-light)]/10 rounded">
              <Users size={20} className="text-[var(--warning)]" />
            </div>
          </div>
        </BlueprintCard>

        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-[var(--ink-muted)] uppercase tracking-wide">Revenue</p>
              <p className="text-2xl font-bold text-[var(--ink)] mt-1">${totalRevenue.toLocaleString()}</p>
              <p className="text-xs text-[var(--success)] mt-1">+8% vs last month</p>
            </div>
            <div className="p-2 bg-[var(--success-light)]/10 rounded">
              <TrendingUp size={20} className="text-[var(--success)]" />
            </div>
          </div>
        </BlueprintCard>

        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-[var(--ink-muted)] uppercase tracking-wide">Avg ROI</p>
              <p className="text-2xl font-bold text-[var(--ink)] mt-1">245%</p>
              <p className="text-xs text-[var(--success)] mt-1">+15% vs last month</p>
            </div>
            <div className="p-2 bg-[var(--blueprint-light)]/10 rounded">
              <BarChart3 size={20} className="text-[var(--blueprint)]" />
            </div>
          </div>
        </BlueprintCard>
      </div>

      {/* Filters and Search */}
      <div className="px-6 pb-4 flex items-center gap-4">
        <div className="flex-1 relative">
          <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--ink-ghost)]" />
          <input
            type="text"
            placeholder="Search campaigns..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter size={16} className="text-[var(--ink-ghost)]" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as CampaignStatus | 'all')}
            className="px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
          >
            <option value="all">All Status</option>
            <option value={CampaignStatus.DRAFT}>Draft</option>
            <option value={CampaignStatus.PLANNING}>Planning</option>
            <option value={CampaignStatus.ACTIVE}>Active</option>
            <option value={CampaignStatus.PAUSED}>Paused</option>
            <option value={CampaignStatus.COMPLETED}>Completed</option>
            <option value={CampaignStatus.CANCELLED}>Cancelled</option>
          </select>
        </div>

        {selectedCampaigns.length > 0 && (
          <div className="flex items-center gap-2 ml-auto">
            <span className="text-sm text-[var(--ink-muted)]">
              {selectedCampaigns.length} selected
            </span>
            <BlueprintButton
              size="sm"
              variant="secondary"
              onClick={() => handleQuickAction('activate')}
            >
              Activate
            </BlueprintButton>
            <BlueprintButton
              size="sm"
              variant="secondary"
              onClick={() => handleQuickAction('pause')}
            >
              Pause
            </BlueprintButton>
            <BlueprintButton
              size="sm"
              variant="secondary"
              onClick={() => handleQuickAction('delete')}
              className="text-[var(--destructive)] hover:bg-[var(--destructive-light)]/10"
            >
              Delete
            </BlueprintButton>
          </div>
        )}
      </div>

      {/* Campaign List */}
      <div className="flex-1 overflow-y-auto px-6 pb-6">
        {filteredCampaigns.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-full border border-[var(--structure-subtle)] flex items-center justify-center mb-4">
              <BarChart3 size={24} className="text-[var(--ink-ghost)]" />
            </div>
            <h3 className="text-lg font-semibold text-[var(--ink)] mb-2">No campaigns yet</h3>
            <p className="text-sm text-[var(--ink-muted)] mb-4">
              Create your first campaign to get started
            </p>
            <BlueprintButton onClick={onCreateCampaign}>
              Create Campaign
            </BlueprintButton>
          </div>
        ) : (
          <div className="space-y-3">
            {/* Header */}
            <div className="flex items-center gap-4 px-4 py-2 text-xs font-medium text-[var(--ink-muted)] uppercase tracking-wide">
              <input
                type="checkbox"
                checked={selectedCampaigns.length === filteredCampaigns.length}
                onChange={handleSelectAll}
                className="rounded border-[var(--structure-subtle)] text-[var(--blueprint)] focus:ring-[var(--blueprint)]"
              />
              <span className="flex-1">Campaign</span>
              <span className="w-24">Status</span>
              <span className="w-32">Budget</span>
              <span className="w-32">Performance</span>
              <span className="w-24">ROI</span>
              <span className="w-20 text-right">Actions</span>
            </div>

            {/* Campaign Rows */}
            {filteredCampaigns.map((campaign) => {
              const statusInfo = statusConfig[campaign.status];
              const StatusIcon = statusInfo.icon;
              const isSelected = selectedCampaigns.includes(campaign.id);

              return (
                <BlueprintCard
                  key={campaign.id}
                  className={cn(
                    "p-4 transition-all cursor-pointer hover:border-[var(--blueprint)]",
                    isSelected && "border-[var(--blueprint)] bg-[var(--blueprint-light)]/5"
                  )}
                >
                  <div className="flex items-center gap-4">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => handleSelectCampaign(campaign.id)}
                      className="rounded border-[var(--structure-subtle)] text-[var(--blueprint)] focus:ring-[var(--blueprint)]"
                    />

                    <div className="flex-1" onClick={() => onViewCampaign?.(campaign.id)}>
                      <h3 className="text-sm font-semibold text-[var(--ink)]">
                        {campaign.name}
                      </h3>
                      <p className="text-xs text-[var(--ink-muted)] mt-1 line-clamp-1">
                        {campaign.description}
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        <BlueprintBadge variant="default" size="sm">
                          {campaign.status}
                        </BlueprintBadge>
                        {campaign.tags.map(tag => (
                          <span key={tag} className="text-[9px] px-1.5 py-0.5 bg-[var(--surface)] text-[var(--ink-muted)] rounded">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="w-24">
                      <BlueprintBadge
                        variant="default"
                        size="sm"
                        className={cn(statusInfo.color)}
                      >
                        <StatusIcon size={12} className="mr-1" />
                        {statusInfo.label}
                      </BlueprintBadge>
                    </div>

                    <div className="w-32">
                      <p className="text-sm font-medium text-[var(--ink)]">
                        ${campaign.budget.total.toLocaleString()}
                      </p>
                      <p className="text-xs text-[var(--ink-muted)]">
                        ${campaign.budget.spent.toLocaleString()} spent
                      </p>
                    </div>

                    <div className="w-32">
                      <div className="flex items-center gap-2 text-xs">
                        <span className="text-[var(--ink-muted)]">Conversions:</span>
                        <span className="font-medium text-[var(--ink)]">
                          {campaign.analytics.overview.totalConversions}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-xs mt-1">
                        <span className="text-[var(--ink-muted)]">Revenue:</span>
                        <span className="font-medium text-[var(--success)]">
                          ${campaign.analytics.overview.totalRevenue.toLocaleString()}
                        </span>
                      </div>
                    </div>

                    <div className="w-24">
                      <p className="text-sm font-medium text-[var(--ink)]">
                        {campaign.analytics.overview.roi}%
                      </p>
                      <div className="w-full bg-[var(--surface)] rounded-full h-1 mt-1">
                        <div
                          className="bg-[var(--success)] h-1 rounded-full"
                          style={{ width: `${Math.min(campaign.analytics.overview.roi / 5, 100)}%` }}
                        />
                      </div>
                    </div>

                    <div className="w-20 flex justify-end">
                      <div className="relative group">
                        <button className="p-1 hover:bg-[var(--surface)] rounded text-[var(--ink-muted)]">
                          <MoreVertical size={16} />
                        </button>

                        {/* Dropdown Menu */}
                        <div className="absolute right-0 top-full mt-1 w-48 bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                          <div className="py-1">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                onEditCampaign?.(campaign.id);
                              }}
                              className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2"
                            >
                              <Edit size={12} />
                              Edit
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleQuickAction('duplicate', campaign.id);
                              }}
                              className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2"
                            >
                              <Copy size={12} />
                              Duplicate
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleQuickAction('activate', campaign.id);
                              }}
                              className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2"
                            >
                              <Play size={12} />
                              Activate
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleQuickAction('pause', campaign.id);
                              }}
                              className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2"
                            >
                              <Pause size={12} />
                              Pause
                            </button>
                            <hr className="my-1 border-[var(--structure-subtle)]" />
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleQuickAction('delete', campaign.id);
                              }}
                              className="w-full px-3 py-2 text-xs text-left text-[var(--destructive)] hover:bg-[var(--destructive-light)]/10 flex items-center gap-2"
                            >
                              <Trash2 size={12} />
                              Delete
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </BlueprintCard>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
