'use client';

import React, { useState } from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Signal, SignalConfidence } from '../types';
import {
    Pin,
    PinOff,
    FileText,
    MessageSquare,
    MoreVertical,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

interface SignalTableProps {
    signals: Signal[];
    onPin: (id: string) => void;
    onUnpin: (id: string) => void;
    onAddNote: (id: string) => void;
    onGenerateDossier: (signalIds: string[]) => void;
}

export function SignalTable({
    signals,
    onPin,
    onUnpin,
    onAddNote,
    onGenerateDossier,
}: SignalTableProps) {
    const [selectedIds, setSelectedIds] = useState<string[]>([]);

    const toggleSelect = (id: string) => {
        setSelectedIds((prev) =>
            prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
        );
    };

    const getConfidenceColor = (confidence: SignalConfidence) => {
        switch (confidence) {
            case 'high':
                return 'bg-green-100 text-green-800 border-green-200';
            case 'medium':
                return 'bg-blue-100 text-blue-800 border-blue-200';
            case 'low':
                return 'bg-gray-100 text-gray-800 border-gray-200';
            default:
                return 'bg-gray-100 text-gray-800 border-gray-200';
        }
    };

    // Helper to extract specific tags
    const getTagValue = (tags: string[], prefix: string) => {
        // In our mapping, tags are [type, strength, freshness, 'competitor']
        // We'll just look for standard values if prefix isn't explicit
        return tags.find((t) => t !== 'competitor') || 'N/A';
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div className="text-sm text-muted-foreground">
                    {selectedIds.length} signals selected
                </div>
                <Button
                    size="sm"
                    disabled={selectedIds.length === 0}
                    onClick={() => onGenerateDossier(selectedIds)}
                    className="bg-[#1A1D1E] hover:bg-black text-white"
                >
                    <FileText className="w-4 h-4 mr-2" />
                    Generate Dossier
                </Button>
            </div>

            <div className="rounded-xl border border-[#E5E6E3] bg-white overflow-hidden">
                <Table>
                    <TableHeader className="bg-[#F8F9F7]">
                        <TableRow>
                            <TableHead className="w-[40px]"></TableHead>
                            <TableHead className="font-medium text-[#2D3538]">Signal</TableHead>
                            <TableHead className="font-medium text-[#2D3538]">Source</TableHead>
                            <TableHead className="font-medium text-[#2D3538]">Type</TableHead>
                            <TableHead className="font-medium text-[#2D3538]">Confidence</TableHead>
                            <TableHead className="font-medium text-[#2D3538]">Freshness</TableHead>
                            <TableHead className="font-medium text-[#2D3538]">Strength</TableHead>
                            <TableHead className="text-right font-medium text-[#2D3538]">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {signals.map((signal) => {
                            // Extracting from tags based on backend mapping: [type, strength, freshness, 'competitor']
                            const signalType = signal.tags[0] || 'Unknown';
                            const strength = signal.tags[1] || 'Neutral';
                            const freshness = signal.tags[2] || 'Recent';

                            return (
                                <TableRow
                                    key={signal.id}
                                    className={cn(
                                        'transition-colors hover:bg-[#F3F4EE]/50',
                                        selectedIds.includes(signal.id) && 'bg-[#F3F4EE]'
                                    )}
                                >
                                    <TableCell>
                                        <input
                                            type="checkbox"
                                            className="rounded border-[#C0C1BE]"
                                            checked={selectedIds.includes(signal.id)}
                                            onChange={() => toggleSelect(signal.id)}
                                        />
                                    </TableCell>
                                    <TableCell className="max-w-[300px]">
                                        <div className="font-medium text-[#2D3538] line-clamp-1">
                                            {signal.title}
                                        </div>
                                        <div className="text-xs text-[#5B5F61] mt-0.5 line-clamp-1">
                                            {signal.whyItMatters}
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        <div className="text-sm text-[#2D3538]">
                                            {signal.source.name}
                                        </div>
                                        <div className="text-[10px] text-[#9D9F9F] uppercase tracking-wider font-semibold">
                                            {signal.source.type}
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        <Badge variant="outline" className="capitalize text-[10px] py-0 px-1.5 h-5 border-[#C0C1BE]">
                                            {signalType}
                                        </Badge>
                                    </TableCell>
                                    <TableCell>
                                        <Badge
                                            className={cn(
                                                'capitalize text-[10px] py-0 px-1.5 h-5 border-transparent font-bold',
                                                getConfidenceColor(signal.confidence)
                                            )}
                                        >
                                            {signal.confidence}
                                        </Badge>
                                    </TableCell>
                                    <TableCell>
                                        <span className="text-xs text-[#5B5F61]">{freshness}</span>
                                    </TableCell>
                                    <TableCell>
                                        <Badge variant="secondary" className="bg-[#D7C9AE]/20 text-[#A68F68] border-none text-[10px] py-0 px-1.5 h-5">
                                            {strength}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <div className="flex items-center justify-end gap-1">
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-8 w-8 text-[#5B5F61] hover:text-[#2D3538]"
                                                onClick={() =>
                                                    signal.isSaved ? onUnpin(signal.id) : onPin(signal.id)
                                                }
                                            >
                                                {signal.isSaved ? (
                                                    <PinOff className="w-4 h-4 text-[#D7C9AE]" />
                                                ) : (
                                                    <Pin className="w-4 h-4" />
                                                )}
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-8 w-8 text-[#5B5F61] hover:text-[#2D3538]"
                                                onClick={() => onAddNote(signal.id)}
                                            >
                                                <MessageSquare className="w-4 h-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-8 w-8 text-[#5B5F61] hover:text-[#2D3538]"
                                            >
                                                <MoreVertical className="w-4 h-4" />
                                            </Button>
                                        </div>
                                    </TableCell>
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
