'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronDown,
  ChevronUp,
  MoreHorizontal,
  Calendar,
  Target,
  Play,
  AlertCircle,
  CheckCircle2,
  Clock,
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { Campaign, Move } from '@/lib/campaigns-types';
import { MoveMiniCard } from '@/components/moves/MoveMiniCard';
import { cn } from '@/lib/utils';

interface CampaignCardProps {
  campaign: Campaign;
  moves?: Move[]; // Make optional as it might not always be passed
  progress?: number;
  activeMove?: Move;
  variant?: 'default' | 'attention';
  readOnly?: boolean;
  onEdit?: (c: Campaign) => void;
  onDelete?: (c: Campaign) => void;
  onArchive?: (c: Campaign) => void;
  onMoveClick?: (m: Move) => void;
}

export function CampaignCard({
  campaign,
  moves = [],
  progress: progressProp,
  activeMove,
  variant = 'default',
  readOnly = false,
  onEdit = () => { },
  onDelete = () => { },
  onArchive = () => { },
  onMoveClick = () => { },
}: CampaignCardProps) {
  const [isExpanded, setIsExpanded] = useState(false); // Default collapsed

  const statusColors = {
    draft: 'bg-gray-100 text-gray-600',
    active: 'bg-emerald-100 text-emerald-700',
    paused: 'bg-amber-100 text-amber-700',
    completed: 'bg-blue-100 text-blue-700',
    archived: 'bg-gray-100 text-gray-400',
    planned: 'bg-purple-100 text-purple-700',
    wrapup: 'bg-orange-100 text-orange-700',
  };

  const progress = progressProp ?? (
    moves.length > 0
      ? Math.round(
        (moves.filter((m) => m.status === 'completed').length /
          moves.length) *
        100
      )
      : 0);

  return (
    <div className="bg-white rounded-2xl border border-[#E5E6E3] shadow-sm hover:shadow-md transition-shadow overflow-hidden">
      {/* Header */}
      <div
        className="p-6 cursor-pointer hover:bg-[#FCFDFB] transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className="mt-1 p-2 rounded-xl bg-[#F8F9F7] border border-[#E5E6E3]">
              <Target className="w-5 h-5 text-[#2D3538]" />
            </div>
            <div>
              <div className="flex items-center gap-3 mb-1">
                <h3 className="font-serif text-lg font-medium text-[#2D3538]">
                  {campaign.name}
                </h3>
                <span
                  className={cn(
                    'text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full',
                    statusColors[campaign.status]
                  )}
                >
                  {campaign.status}
                </span>
              </div>
              <p className="text-sm text-[#5B5F61] line-clamp-1">
                {campaign.objective} Objective
              </p>

              <div className="flex items-center gap-4 mt-3 text-xs text-[#9D9F9F]">
                <span className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5" />
                  {moves.length} Moves
                </span>
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  {progress}% Complete
                </span>
              </div>
            </div>
          </div>

          <div
            className="flex items-center gap-2"
            onClick={(e) => e.stopPropagation()}
          >
            {!readOnly && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-[#9D9F9F] hover:text-[#2D3538]"
                  >
                    <MoreHorizontal className="w-4 h-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuItem onClick={() => onEdit(campaign)}>
                    Edit Campaign
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onArchive(campaign)}>
                    Archive
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    className="text-red-600"
                    onClick={() => onDelete(campaign)}
                  >
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-[#9D9F9F]"
              onClick={(e) => {
                e.stopPropagation();
                setIsExpanded(!isExpanded);
              }}
            >
              {isExpanded ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-6 h-1 w-full bg-[#F3F4EE] rounded-full overflow-hidden">
          <div
            className="h-full bg-[#2D3538] transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Moves List (Collapsible) */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: 'auto' }}
            exit={{ height: 0 }}
            className="overflow-hidden border-t border-[#E5E6E3] bg-[#FCFDFB]"
          >
            <div className="p-4 space-y-3">
              {moves.length > 0 ? (
                moves.map((move) => (
                  <MoveMiniCard
                    key={move.id}
                    move={move}
                    onClick={() => onMoveClick(move)}
                  />
                ))
              ) : (
                <div className="text-center py-8 text-[#9D9F9F] text-xs">
                  No moves in this campaign yet.
                </div>
              )}
              {!readOnly && (
                <Button
                  variant="outline"
                  className="w-full border-dashed border-[#C0C1BE] text-[#5B5F61] hover:text-[#2D3538] hover:border-[#2D3538]"
                >
                  + Add Move to Campaign
                </Button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
