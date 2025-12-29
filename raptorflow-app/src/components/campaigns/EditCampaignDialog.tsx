'use client';

import React, { useState } from 'react';
import { Campaign, Move } from '@/lib/campaigns-types';
import { updateCampaign, deleteMove } from '@/lib/campaigns';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Trash2, GripVertical, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';

interface EditCampaignDialogProps {
    campaign: Campaign | null;
    moves: Move[];
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSuccess: () => void;
}

export function EditCampaignDialog({
    campaign,
    moves,
    open,
    onOpenChange,
    onSuccess,
}: EditCampaignDialogProps) {
    const [name, setName] = useState(campaign?.name || '');
    const [objective, setObjective] = useState(campaign?.objective || 'growth');
    const [description, setDescription] = useState(
        'Focus on rapid experimentation to validate core value proposition.' // Placeholder logic
    );
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Sync state when campaign changes
    React.useEffect(() => {
        if (campaign && open) {
            setName(campaign.name);
            setObjective(campaign.objective);
            // Logic for description hydration if available
        }
    }, [campaign, open]);

    const handleSave = async () => {
        if (!campaign) return;
        setIsSubmitting(true);
        try {
            await updateCampaign({
                ...campaign,
                name,
                objective: objective as any,
            });
            toast.success('Campaign updated');
            onSuccess();
            onOpenChange(false);
        } catch (error) {
            toast.error('Failed to update campaign');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDeleteMove = async (moveId: string) => {
        if (!confirm('Are you sure you want to delete this move?')) return;
        try {
            await deleteMove(moveId);
            toast.success('Move deleted');
            onSuccess(); // Triggers refresh
        } catch (error) {
            toast.error('Failed to delete move');
        }
    };

    if (!campaign) return null;

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-2xl bg-canvas-card border-border">
                <DialogHeader>
                    <DialogTitle className="font-serif text-xl text-ink">
                        Edit Campaign
                    </DialogTitle>
                </DialogHeader>

                <div className="space-y-6 py-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-xs font-bold uppercase tracking-wider text-secondary-text">
                                Campaign Name
                            </label>
                            <Input
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                className="bg-canvas border-border font-medium"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-bold uppercase tracking-wider text-secondary-text">
                                Objective
                            </label>
                            <select
                                value={objective}
                                onChange={(e) => setObjective(e.target.value)}
                                className="w-full h-10 px-3 rounded-md border border-border bg-canvas text-sm focus:outline-none focus:ring-1 focus:ring-ink"
                            >
                                <option value="growth">Growth</option>
                                <option value="retention">Retention</option>
                                <option value="brand">Brand</option>
                                <option value="launch">Launch</option>
                            </select>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs font-bold uppercase tracking-wider text-secondary-text">
                            Context / Description
                        </label>
                        <Textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            className="bg-canvas border-border min-h-[80px]"
                        />
                    </div>

                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <label className="text-xs font-bold uppercase tracking-wider text-secondary-text">
                                Campaign Moves {moves.length > 0 && `(${moves.length})`}
                            </label>
                            <span className="text-[10px] text-muted-foreground uppercase tracking-widest">
                                Drag to Reorder (Coming Soon)
                            </span>
                        </div>

                        <div className="bg-canvas rounded-lg border border-border divide-y divide-border max-h-[200px] overflow-y-auto">
                            {moves.length === 0 ? (
                                <div className="p-8 text-center text-sm text-secondary-text">
                                    No moves added yet.
                                </div>
                            ) : (
                                moves.map((move) => (
                                    <div
                                        key={move.id}
                                        className="flex items-center gap-3 p-3 hover:bg-surface/50 transition-colors group"
                                    >
                                        <GripVertical className="w-4 h-4 text-border cursor-grab" />
                                        <div className="flex-1 min-w-0">
                                            <div className="font-medium text-sm text-ink truncate">
                                                {move.name}
                                            </div>
                                            <div className="flex items-center gap-2 text-[11px] text-secondary-text">
                                                <span className="uppercase">{move.status}</span>
                                                <span>•</span>
                                                <span>{move.channel}</span>
                                            </div>
                                        </div>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-7 w-7 text-secondary-text hover:text-red-500 hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-all"
                                            onClick={() => handleDeleteMove(move.id)}
                                        >
                                            <Trash2 className="w-3.5 h-3.5" />
                                        </Button>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>

                <DialogFooter className="gap-2">
                    <Button
                        variant="ghost"
                        onClick={() => onOpenChange(false)}
                        className="text-secondary-text hover:text-ink"
                    >
                        Cancel
                    </Button>
                    <Button
                        onClick={handleSave}
                        disabled={isSubmitting}
                        className="bg-ink text-canvas hover:bg-ink/90"
                    >
                        {isSubmitting ? 'Saving...' : 'Save Changes'}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
