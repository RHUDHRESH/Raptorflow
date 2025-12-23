'use client';

import React, { useState } from 'react';
import { Icp } from '@/types/icp-types';
import { cn } from '@/lib/utils';
import { X, Save, AlertTriangle, MessageSquare, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

interface ICPRefinementProps {
    icp: Partial<Icp>;
    onSave: (updates: Partial<Icp>) => void;
    onClose: () => void;
}

/**
 * Lite editor for refining auto-generated ICPs
 * Not full creation - just adjustments
 */
export function ICPRefinement({ icp, onSave, onClose }: ICPRefinementProps) {
    const [name, setName] = useState(icp.name || '');
    const [primaryPains, setPrimaryPains] = useState(icp.painMap?.primaryPains?.join('\n') || '');
    const [tonePreference, setTonePreference] = useState(icp.psycholinguistics?.tonePreference || []);
    const [wordsToUse, setWordsToUse] = useState(icp.psycholinguistics?.wordsToUse?.join(', ') || '');
    const [wordsToAvoid, setWordsToAvoid] = useState(icp.psycholinguistics?.wordsToAvoid?.join(', ') || '');
    const [priority, setPriority] = useState(icp.priority || 'secondary');

    const toneOptions = ['direct', 'friendly', 'professional', 'casual', 'authoritative', 'empathetic'];

    const toggleTone = (tone: string) => {
        if (tonePreference.includes(tone)) {
            setTonePreference(tonePreference.filter(t => t !== tone));
        } else {
            setTonePreference([...tonePreference, tone]);
        }
    };

    const handleSave = () => {
        const updates: Partial<Icp> = {
            name,
            priority: priority as 'primary' | 'secondary',
            painMap: {
                ...icp.painMap!,
                primaryPains: primaryPains.split('\n').map(p => p.trim()).filter(Boolean)
            },
            psycholinguistics: {
                ...icp.psycholinguistics!,
                tonePreference,
                wordsToUse: wordsToUse.split(',').map(w => w.trim()).filter(Boolean),
                wordsToAvoid: wordsToAvoid.split(',').map(w => w.trim()).filter(Boolean)
            }
        };
        onSave(updates);
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-card border border-border rounded-2xl w-full max-w-lg max-h-[90vh] overflow-hidden flex flex-col animate-in zoom-in-95 fade-in duration-200">
                {/* Header */}
                <div className="px-6 py-4 border-b border-border flex items-center justify-between">
                    <div>
                        <h2 className="font-serif text-xl font-medium">Refine ICP</h2>
                        <p className="text-sm text-muted-foreground">Adjust the auto-generated profile</p>
                    </div>
                    <Button variant="ghost" size="icon" onClick={onClose}>
                        <X className="h-5 w-5" />
                    </Button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {/* Name */}
                    <div>
                        <label className="text-sm font-medium text-foreground mb-2 block">ICP Name</label>
                        <Input
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="e.g., The Tech-Savvy Founder"
                            className="h-11"
                        />
                    </div>

                    {/* Priority */}
                    <div>
                        <label className="text-sm font-medium text-foreground mb-2 block">Priority</label>
                        <div className="flex gap-2">
                            <button
                                onClick={() => setPriority('primary')}
                                className={cn(
                                    "flex-1 py-2 px-4 rounded-lg border text-sm font-medium transition-colors",
                                    priority === 'primary'
                                        ? "bg-primary text-primary-foreground border-primary"
                                        : "bg-background border-border text-foreground hover:border-primary/50"
                                )}
                            >
                                Primary
                            </button>
                            <button
                                onClick={() => setPriority('secondary')}
                                className={cn(
                                    "flex-1 py-2 px-4 rounded-lg border text-sm font-medium transition-colors",
                                    priority === 'secondary'
                                        ? "bg-primary text-primary-foreground border-primary"
                                        : "bg-background border-border text-foreground hover:border-primary/50"
                                )}
                            >
                                Secondary
                            </button>
                        </div>
                    </div>

                    {/* Pain Points */}
                    <div>
                        <label className="text-sm font-medium text-foreground mb-2 flex items-center gap-2">
                            <AlertTriangle className="h-4 w-4 text-muted-foreground" /> Primary Pain Points
                        </label>
                        <Textarea
                            value={primaryPains}
                            onChange={(e) => setPrimaryPains(e.target.value)}
                            placeholder="One pain point per line"
                            className="min-h-[100px] resize-none"
                        />
                        <p className="text-xs text-muted-foreground mt-1">One per line. Max 2 recommended.</p>
                    </div>

                    {/* Tone */}
                    <div>
                        <label className="text-sm font-medium text-foreground mb-2 flex items-center gap-2">
                            <MessageSquare className="h-4 w-4 text-muted-foreground" /> Preferred Tone
                        </label>
                        <div className="flex flex-wrap gap-2">
                            {toneOptions.map((tone) => (
                                <button
                                    key={tone}
                                    onClick={() => toggleTone(tone)}
                                    className={cn(
                                        "px-3 py-1.5 rounded-full text-sm font-medium transition-colors capitalize",
                                        tonePreference.includes(tone)
                                            ? "bg-primary text-primary-foreground"
                                            : "bg-muted text-muted-foreground hover:bg-muted/80"
                                    )}
                                >
                                    {tone}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Words to Use */}
                    <div>
                        <label className="text-sm font-medium text-foreground mb-2 block">Words to Use</label>
                        <Input
                            value={wordsToUse}
                            onChange={(e) => setWordsToUse(e.target.value)}
                            placeholder="e.g., scale, automate, ROI"
                            className="h-11"
                        />
                        <p className="text-xs text-muted-foreground mt-1">Comma-separated</p>
                    </div>

                    {/* Words to Avoid */}
                    <div>
                        <label className="text-sm font-medium text-foreground mb-2 block">Words to Avoid</label>
                        <Input
                            value={wordsToAvoid}
                            onChange={(e) => setWordsToAvoid(e.target.value)}
                            placeholder="e.g., cheap, basic, manual"
                            className="h-11"
                        />
                        <p className="text-xs text-muted-foreground mt-1">Comma-separated</p>
                    </div>
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-border flex justify-end gap-3">
                    <Button variant="outline" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button onClick={handleSave}>
                        <Save className="h-4 w-4 mr-2" /> Save Changes
                    </Button>
                </div>
            </div>
        </div>
    );
}
