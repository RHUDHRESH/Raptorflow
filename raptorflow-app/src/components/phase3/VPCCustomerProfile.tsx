'use client';

import React, { useState } from 'react';
import { GripVertical, Plus, X, Trash2, ChevronDown, ChevronUp, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { VPCData, VPCPain, VPCGain } from '@/lib/foundation';
import { v4 as uuidv4 } from 'uuid';

interface VPCCustomerProfileProps {
    vpc: VPCData;
    onUpdate: (vpc: VPCData) => void;
    onContinue: () => void;
    onBack: () => void;
}

// Draggable item component
function DraggableItem({
    text,
    rank,
    score,
    scoreLabel,
    onRemove,
    source,
}: {
    text: string;
    rank: number;
    score: number;
    scoreLabel: string;
    onRemove: () => void;
    source?: 'uploads' | 'edits' | 'assumption';
}) {
    const sourceColors = {
        uploads: 'bg-[#22C55E]/10 text-[#22C55E]',
        edits: 'bg-[#3B82F6]/10 text-[#3B82F6]',
        assumption: 'bg-[#F59E0B]/10 text-[#F59E0B]',
    };

    return (
        <div className="group flex items-center gap-3 bg-white border border-[#E5E6E3] rounded-xl px-4 py-4 hover:shadow-sm transition-all">
            <GripVertical className="w-4 h-4 text-[#C0C1BE] cursor-grab flex-shrink-0" />

            <div className="w-7 h-7 rounded-full bg-[#2D3538] text-white flex items-center justify-center text-[12px] font-mono flex-shrink-0">
                {rank}
            </div>

            <div className="flex-1 min-w-0">
                <p className="text-[14px] text-[#2D3538] truncate">{text}</p>
            </div>

            {source && (
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono uppercase tracking-[0.05em] flex-shrink-0 ${sourceColors[source]}`}>
                    {source}
                </span>
            )}

            <div className="flex items-center gap-1 flex-shrink-0">
                <span className="text-[11px] font-mono text-[#9D9F9F]">{scoreLabel}</span>
                <div className="flex gap-0.5">
                    {[1, 2, 3, 4, 5].map((n) => (
                        <div
                            key={n}
                            className={`w-2 h-2 rounded-full ${n <= score ? 'bg-[#2D3538]' : 'bg-[#E5E6E3]'}`}
                        />
                    ))}
                </div>
            </div>

            <button
                onClick={onRemove}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-[#F3F4EE] rounded-lg flex-shrink-0"
            >
                <Trash2 className="w-4 h-4 text-[#9D9F9F]" />
            </button>
        </div>
    );
}

// Panel component for Jobs, Pains, Gains
function ProfilePanel({
    title,
    description,
    items,
    scoreLabel,
    onAdd,
    onRemove,
    emptyMessage,
}: {
    title: string;
    description: string;
    items: Array<{ id: string; text: string; score: number; source?: 'uploads' | 'edits' | 'assumption' }>;
    scoreLabel: string;
    onAdd: (text: string) => void;
    onRemove: (id: string) => void;
    emptyMessage: string;
}) {
    const [isAdding, setIsAdding] = useState(false);
    const [newText, setNewText] = useState('');

    const handleAdd = () => {
        if (!newText.trim()) return;
        onAdd(newText.trim());
        setNewText('');
        setIsAdding(false);
    };

    return (
        <div className="bg-[#FAFAF8] rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h3 className="font-medium text-[#2D3538] text-[16px]">{title}</h3>
                    <p className="text-[12px] text-[#5B5F61] mt-1">{description}</p>
                </div>
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsAdding(!isAdding)}
                    className="text-[#5B5F61] hover:text-[#2D3538]"
                >
                    <Plus className="w-4 h-4 mr-1" />
                    Add
                </Button>
            </div>

            {isAdding && (
                <div className="flex items-center gap-2 mb-4">
                    <input
                        type="text"
                        value={newText}
                        onChange={(e) => setNewText(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
                        placeholder={`Add new ${title.toLowerCase()}...`}
                        autoFocus
                        className="flex-1 bg-white border border-[#E5E6E3] rounded-xl px-4 py-3 text-[14px] text-[#2D3538] placeholder:text-[#9D9F9F] focus:outline-none focus:ring-2 focus:ring-[#2D3538]/10"
                    />
                    <Button onClick={handleAdd} size="sm" className="bg-[#2D3538] text-white">
                        Add
                    </Button>
                    <Button onClick={() => setIsAdding(false)} variant="ghost" size="sm">
                        Cancel
                    </Button>
                </div>
            )}

            <div className="space-y-2">
                {items.slice(0, 5).map((item, index) => (
                    <DraggableItem
                        key={item.id}
                        text={item.text}
                        rank={index + 1}
                        score={item.score}
                        scoreLabel={scoreLabel}
                        source={item.source}
                        onRemove={() => onRemove(item.id)}
                    />
                ))}

                {items.length === 0 && (
                    <div className="text-center py-8 text-[#9D9F9F] text-[14px]">
                        {emptyMessage}
                    </div>
                )}

                {items.length > 5 && (
                    <div className="text-center py-2">
                        <span className="text-[12px] text-[#9D9F9F]">
                            +{items.length - 5} more (showing top 5)
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
}

export function VPCCustomerProfile({
    vpc,
    onUpdate,
    onContinue,
    onBack,
}: VPCCustomerProfileProps) {
    // Transform jobs to items format
    const jobItems = vpc.customerProfile.jobs.map((job, index) => ({
        id: `job-${index}`,
        text: job,
        score: 5 - Math.min(index, 4), // Descending score
        source: 'uploads' as const,
    }));

    // Transform pains to items format
    const painItems = vpc.customerProfile.pains.map((pain) => ({
        id: pain.id,
        text: pain.text,
        score: pain.severity,
        source: 'uploads' as const,
    }));

    // Transform gains to items format
    const gainItems = vpc.customerProfile.gains.map((gain) => ({
        id: gain.id,
        text: gain.text,
        score: gain.importance,
        source: 'uploads' as const,
    }));

    const handleAddJob = (text: string) => {
        onUpdate({
            ...vpc,
            customerProfile: {
                ...vpc.customerProfile,
                jobs: [...vpc.customerProfile.jobs, text],
            },
        });
    };

    const handleRemoveJob = (id: string) => {
        const index = parseInt(id.replace('job-', ''));
        onUpdate({
            ...vpc,
            customerProfile: {
                ...vpc.customerProfile,
                jobs: vpc.customerProfile.jobs.filter((_, i) => i !== index),
            },
        });
    };

    const handleAddPain = (text: string) => {
        const newPain: VPCPain = {
            id: uuidv4(),
            text,
            severity: 3,
        };
        onUpdate({
            ...vpc,
            customerProfile: {
                ...vpc.customerProfile,
                pains: [...vpc.customerProfile.pains, newPain],
            },
        });
    };

    const handleRemovePain = (id: string) => {
        onUpdate({
            ...vpc,
            customerProfile: {
                ...vpc.customerProfile,
                pains: vpc.customerProfile.pains.filter((p) => p.id !== id),
            },
        });
    };

    const handleAddGain = (text: string) => {
        const newGain: VPCGain = {
            id: uuidv4(),
            text,
            importance: 3,
        };
        onUpdate({
            ...vpc,
            customerProfile: {
                ...vpc.customerProfile,
                gains: [...vpc.customerProfile.gains, newGain],
            },
        });
    };

    const handleRemoveGain = (id: string) => {
        onUpdate({
            ...vpc,
            customerProfile: {
                ...vpc.customerProfile,
                gains: vpc.customerProfile.gains.filter((g) => g.id !== id),
            },
        });
    };

    return (
        <div className="space-y-8">
            {/* Info Banner */}
            <div className="flex items-center gap-3 bg-[#2D3538]/5 rounded-xl px-5 py-4">
                <Info className="w-5 h-5 text-[#5B5F61] flex-shrink-0" />
                <p className="text-[14px] text-[#5B5F61]">
                    Drag to rank your <span className="font-medium text-[#2D3538]">top 3</span> in each category.
                    Items at the top are most important.
                </p>
            </div>

            {/* Three Panels */}
            <div className="space-y-6">
                <ProfilePanel
                    title="Customer Jobs"
                    description="What is your customer trying to accomplish?"
                    items={jobItems}
                    scoreLabel="Priority"
                    onAdd={handleAddJob}
                    onRemove={handleRemoveJob}
                    emptyMessage="No jobs defined yet"
                />

                <ProfilePanel
                    title="Pains"
                    description="What frustrates or blocks them?"
                    items={painItems}
                    scoreLabel="Severity"
                    onAdd={handleAddPain}
                    onRemove={handleRemovePain}
                    emptyMessage="No pains identified"
                />

                <ProfilePanel
                    title="Gains"
                    description="What would delight them?"
                    items={gainItems}
                    scoreLabel="Importance"
                    onAdd={handleAddGain}
                    onRemove={handleRemoveGain}
                    emptyMessage="No gains identified"
                />
            </div>

            {/* Merge Duplicates Suggestion */}
            {(painItems.length > 5 || gainItems.length > 5) && (
                <div className="flex items-center justify-center">
                    <Button variant="outline" className="text-[#5B5F61] border-[#C0C1BE]">
                        Merge duplicates
                    </Button>
                </div>
            )}

            {/* Actions */}
            <div className="flex items-center justify-between pt-8 border-t border-[#E5E6E3]">
                <Button
                    variant="ghost"
                    onClick={onBack}
                    className="text-[#5B5F61] hover:text-[#2D3538]"
                >
                    ← Back
                </Button>
                <Button
                    onClick={onContinue}
                    className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-10 py-6 rounded-2xl text-[15px] font-medium"
                >
                    Continue
                </Button>
            </div>
        </div>
    );
}
