'use client';

import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import { Campaign, Move } from '@/lib/campaigns-types';
import { updateCampaign } from '@/lib/campaigns';
import { X, ArrowUp, ArrowDown, GripVertical } from 'lucide-react';

interface CampaignEditModalProps {
  campaign: Campaign | null;
  moves?: Move[];
  isOpen: boolean;
  onClose: () => void;
  onSave: () => void; // Trigger refresh
}

export function CampaignEditModal({
  campaign,
  moves = [],
  isOpen,
  onClose,
  onSave,
}: CampaignEditModalProps) {
  const [name, setName] = useState(campaign?.name || '');
  const [objective, setObjective] = useState(campaign?.objective || 'acquire');
  const [isSaving, setIsSaving] = useState(false);

  // Sync state when campaign changes
  React.useEffect(() => {
    if (campaign) {
      setName(campaign.name);
      setObjective(campaign.objective);
    }
  }, [campaign]);

  const handleSave = async () => {
    if (!campaign) return;

    setIsSaving(true);
    try {
      await updateCampaign({ ...campaign, name, objective });
      toast.success('Campaign updated');
      onSave();
      onClose();
    } catch (error) {
      toast.error('Failed to update campaign');
    } finally {
      setIsSaving(false);
    }
  };

  const handleRemoveMove = async (moveId: string) => {
    toast.info('Move reassignment is coming soon.');
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-lg bg-white border-[#E5E6E3]">
        <DialogHeader>
          <DialogTitle className="font-serif text-[#2D3538]">
            Edit Campaign
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-6 py-4">
          {/* Campaign Details */}
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-[12px] font-semibold uppercase tracking-wider text-[#5B5F61]">
                Campaign Name
              </label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="bg-[#F8F9F7] border-[#E5E6E3]"
              />
            </div>

            <div className="space-y-2">
              <label className="text-[12px] font-semibold uppercase tracking-wider text-[#5B5F61]">
                Objective
              </label>
              <select
                value={objective}
                onChange={(e) => setObjective(e.target.value as any)}
                className="w-full h-10 px-3 rounded-md border border-[#E5E6E3] bg-[#F8F9F7] text-sm"
              >
                <option value="acquire">Acquire</option>
                <option value="activate">Activate</option>
                <option value="convert">Convert</option>
                <option value="retention">Retention</option>
                <option value="launch">Launch</option>
              </select>
            </div>
          </div>

          {/* Moves List */}
          <div className="space-y-3">
            <label className="text-[12px] font-semibold uppercase tracking-wider text-[#5B5F61]">
              Campaign Moves ({moves.length})
            </label>
            <div className="max-h-[200px] overflow-y-auto space-y-2 pr-2">
              {moves.length > 0 ? (
                moves.map((move) => (
                  <div
                    key={move.id}
                    className="flex items-center justify-between p-3 rounded-lg border border-[#E5E6E3] bg-card/50"
                  >
                    <span className="text-sm font-medium text-foreground truncate max-w-[200px]">
                      {move.name}
                    </span>
                    <div className="flex items-center gap-2">
                      {/* Placeholder for reorder if needed later
                                            <Button variant="ghost" size="icon" className="h-6 w-6"><ArrowUp className="w-3 h-3" /></Button>
                                            <Button variant="ghost" size="icon" className="h-6 w-6"><ArrowDown className="w-3 h-3" /></Button>
                                            */}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveMove(move.id)}
                        className="h-7 text-xs text-red-500 hover:text-red-700 hover:bg-red-50"
                      >
                        Remove
                      </Button>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-muted-foreground italic">
                  No moves assigned.
                </p>
              )}
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="ghost" onClick={onClose} className="text-[#5B5F61]">
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={isSaving}
            className="bg-[#2D3538] text-white hover:bg-black"
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
