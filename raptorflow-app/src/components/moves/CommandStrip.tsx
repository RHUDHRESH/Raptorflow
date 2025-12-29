'use client';

import React from 'react';
import { Search, List, LayoutGrid, Calendar } from 'lucide-react';
import { cn } from '@/lib/utils';
import styles from './Moves.module.css';
import {
  Move,
  MoveStatus,
  RAGStatus,
  ChannelType,
  MoveGoal,
  MoveDuration,
} from '@/lib/campaigns-types';

export type ViewMode = 'list' | 'board' | 'calendar';

export interface MoveFilters {
  search: string;
  status: MoveStatus | 'all';
  goal: MoveGoal | 'all';
  channel: ChannelType | 'all';
  duration: MoveDuration | 'all';
  rag: RAGStatus | 'all';
}

interface CommandStripProps {
  filters: MoveFilters;
  onFiltersChange: (filters: MoveFilters) => void;
  viewMode: ViewMode;
  onViewModeChange: (mode: ViewMode) => void;
}

const STATUS_OPTIONS: { value: MoveStatus | 'all'; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Active' },
  { value: 'queued', label: 'Queued' },
  { value: 'completed', label: 'Completed' },
];

const GOAL_OPTIONS: { value: MoveGoal | 'all'; label: string }[] = [
  { value: 'all', label: 'Objective' },
  { value: 'leads', label: 'Leads' },
  { value: 'calls', label: 'Calls' },
  { value: 'sales', label: 'Sales' },
  { value: 'proof', label: 'Proof' },
  { value: 'distribution', label: 'Distribution' },
  { value: 'activation', label: 'Activation' },
];

const CHANNEL_OPTIONS: { value: ChannelType | 'all'; label: string }[] = [
  { value: 'all', label: 'Channel' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'email', label: 'Email' },
  { value: 'instagram', label: 'Instagram' },
  { value: 'whatsapp', label: 'WhatsApp' },
  { value: 'twitter', label: 'Twitter' },
  { value: 'cold_dms', label: 'Cold DMs' },
];

const DURATION_OPTIONS: { value: MoveDuration | 'all'; label: string }[] = [
  { value: 'all', label: 'Duration' },
  { value: 7, label: '7D' },
  { value: 14, label: '14D' },
  { value: 28, label: '28D' },
];

const RAG_OPTIONS: {
  value: RAGStatus | 'all';
  label: string;
  color?: string;
}[] = [
  { value: 'all', label: 'RAG' },
  { value: 'green', label: 'G', color: '#22C55E' },
  { value: 'amber', label: 'A', color: '#F59E0B' },
  { value: 'red', label: 'R', color: '#EF4444' },
];

export function CommandStrip({
  filters,
  onFiltersChange,
  viewMode,
  onViewModeChange,
}: CommandStripProps) {
  const updateFilter = <K extends keyof MoveFilters>(
    key: K,
    value: MoveFilters[K]
  ) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  return (
    <div className={styles.commandStrip}>
      {/* Search */}
      <div style={{ position: 'relative' }}>
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
        <input
          type="text"
          placeholder="Search moves..."
          value={filters.search}
          onChange={(e) => updateFilter('search', e.target.value)}
          className={styles.searchInput}
          style={{ paddingLeft: '40px' }}
        />
      </div>

      {/* Filter Chips */}
      <div className={styles.filterChips}>
        {/* Status Filter */}
        <select
          value={filters.status}
          onChange={(e) =>
            updateFilter('status', e.target.value as MoveStatus | 'all')
          }
          className={cn(
            styles.filterChip,
            filters.status !== 'all' && styles.active
          )}
          style={{ cursor: 'pointer' }}
        >
          {STATUS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {/* Goal Filter */}
        <select
          value={filters.goal}
          onChange={(e) =>
            updateFilter('goal', e.target.value as MoveGoal | 'all')
          }
          className={cn(
            styles.filterChip,
            filters.goal !== 'all' && styles.active
          )}
          style={{ cursor: 'pointer' }}
        >
          {GOAL_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {/* Channel Filter */}
        <select
          value={filters.channel}
          onChange={(e) =>
            updateFilter('channel', e.target.value as ChannelType | 'all')
          }
          className={cn(
            styles.filterChip,
            filters.channel !== 'all' && styles.active
          )}
          style={{ cursor: 'pointer' }}
        >
          {CHANNEL_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {/* Duration Filter */}
        <select
          value={filters.duration}
          onChange={(e) => {
            const val = e.target.value;
            updateFilter(
              'duration',
              val === 'all' ? 'all' : (parseInt(val) as MoveDuration)
            );
          }}
          className={cn(
            styles.filterChip,
            filters.duration !== 'all' && styles.active
          )}
          style={{ cursor: 'pointer' }}
        >
          {DURATION_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {/* RAG Filter */}
        <div className={styles.filterChips} style={{ gap: '4px' }}>
          {RAG_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => updateFilter('rag', opt.value)}
              className={cn(
                styles.filterChip,
                filters.rag === opt.value && styles.active
              )}
              style={{
                padding: '0 10px',
                minWidth: opt.value === 'all' ? 'auto' : '32px',
                color:
                  filters.rag === opt.value && opt.color ? '#fff' : undefined,
                background:
                  filters.rag === opt.value && opt.color
                    ? opt.color
                    : undefined,
                borderColor:
                  filters.rag === opt.value && opt.color
                    ? opt.color
                    : undefined,
              }}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* View Toggle */}
      <div className={styles.viewToggle}>
        <button
          onClick={() => onViewModeChange('list')}
          className={cn(
            styles.viewOption,
            viewMode === 'list' && styles.active
          )}
          title="List view"
        >
          <List className="w-4 h-4" />
        </button>
        <button
          onClick={() => onViewModeChange('board')}
          className={cn(
            styles.viewOption,
            viewMode === 'board' && styles.active
          )}
          title="Board view"
        >
          <LayoutGrid className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

/**
 * Apply filters to moves list
 */
export function applyFilters(moves: Move[], filters: MoveFilters) {
  return moves.filter((move) => {
    // Search filter
    if (filters.search) {
      const search = filters.search.toLowerCase();
      const matchesName = move.name.toLowerCase().includes(search);
      const matchesCampaign = move.campaignName?.toLowerCase().includes(search);
      if (!matchesName && !matchesCampaign) return false;
    }

    // Status filter
    if (filters.status !== 'all' && move.status !== filters.status)
      return false;

    // Goal filter
    if (filters.goal !== 'all' && move.goal !== filters.goal) return false;

    // Channel filter
    if (filters.channel !== 'all' && move.channel !== filters.channel)
      return false;

    // Duration filter
    if (filters.duration !== 'all' && move.duration !== filters.duration)
      return false;

    // RAG filter
    if (filters.rag !== 'all' && move.rag !== filters.rag) return false;

    return true;
  });
}
