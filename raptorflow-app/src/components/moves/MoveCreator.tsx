'use client';

import React, { useState, useRef, useEffect } from 'react';
import { ArrowRight, Sparkles, AtSign, Command } from 'lucide-react';
import { toast } from 'sonner';

interface MoveCreatorProps {
    onCreateMove: (description: string, duration: number) => void;
    cohorts?: { id: string; name: string }[];
    competitors?: { id: string; name: string }[];
}

// Mock playbook templates
const PLAYBOOKS = [
    { id: 'problem-post', name: 'Problem Post Sprint', description: '7 posts surfacing pain points', duration: 7 },
    { id: 'dm-sprint', name: 'Outbound DM Sprint', description: '15 targeted DMs/day', duration: 14 },
    { id: 'case-study', name: 'Case Study Sprint', description: 'Daily social proof posts', duration: 7 },
    { id: 'landing-page', name: 'Landing Page Sprint', description: 'Fix message match + deploy', duration: 7 },
    { id: 'webinar', name: 'Workshop Sprint', description: 'One event + promo + follow-up', duration: 14 },
];

export function MoveCreator({ onCreateMove, cohorts = [], competitors = [] }: MoveCreatorProps) {
    const [description, setDescription] = useState('');
    const [duration, setDuration] = useState(7);
    const [showAtMenu, setShowAtMenu] = useState(false);
    const [showSlashMenu, setShowSlashMenu] = useState(false);
    const [menuFilter, setMenuFilter] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Mock cohorts/competitors if not provided
    const allMentions = [
        ...cohorts.map(c => ({ type: 'cohort', ...c })),
        ...competitors.map(c => ({ type: 'competitor', ...c })),
        // Fallback mock data
        { type: 'cohort', id: 'early-stage', name: 'Early-stage founders' },
        { type: 'cohort', id: 'series-a', name: 'Series A SaaS' },
        { type: 'cohort', id: 'bootstrapped', name: 'Bootstrapped makers' },
        { type: 'competitor', id: 'competitor-a', name: 'Competitor A' },
        { type: 'competitor', id: 'competitor-b', name: 'Competitor B' },
    ].filter((v, i, a) => a.findIndex(t => t.id === v.id) === i);

    const filteredMentions = allMentions.filter(m =>
        m.name.toLowerCase().includes(menuFilter.toLowerCase())
    );

    const filteredPlaybooks = PLAYBOOKS.filter(p =>
        p.name.toLowerCase().includes(menuFilter.toLowerCase()) ||
        p.description.toLowerCase().includes(menuFilter.toLowerCase())
    );

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        const value = description;
        const cursorPos = textareaRef.current?.selectionStart || 0;

        // Check for @ trigger
        if (e.key === '@') {
            setShowAtMenu(true);
            setShowSlashMenu(false);
            setMenuFilter('');
        }

        // Check for / trigger at start or after space
        if (e.key === '/' && (cursorPos === 0 || value[cursorPos - 1] === ' ' || value[cursorPos - 1] === '\n')) {
            setShowSlashMenu(true);
            setShowAtMenu(false);
            setMenuFilter('');
        }

        // Close menus on Escape
        if (e.key === 'Escape') {
            setShowAtMenu(false);
            setShowSlashMenu(false);
        }

        // Submit on Cmd/Ctrl + Enter
        if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
            e.preventDefault();
            handleCreate();
        }
    };

    const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const value = e.target.value;
        setDescription(value);

        // Track filter text after @ or /
        if (showAtMenu || showSlashMenu) {
            const lastTrigger = showAtMenu ? '@' : '/';
            const lastIndex = value.lastIndexOf(lastTrigger);
            if (lastIndex !== -1) {
                setMenuFilter(value.slice(lastIndex + 1));
            }
        }
    };

    const insertMention = (name: string) => {
        const cursorPos = textareaRef.current?.selectionStart || description.length;
        const lastAtIndex = description.lastIndexOf('@');
        const before = description.slice(0, lastAtIndex);
        const after = description.slice(cursorPos);
        setDescription(`${before}@${name} ${after}`);
        setShowAtMenu(false);
        textareaRef.current?.focus();
    };

    const insertPlaybook = (playbook: typeof PLAYBOOKS[0]) => {
        const cursorPos = textareaRef.current?.selectionStart || description.length;
        const lastSlashIndex = description.lastIndexOf('/');
        const before = description.slice(0, lastSlashIndex);
        setDescription(`${before}${playbook.description}`);
        setDuration(playbook.duration);
        setShowSlashMenu(false);
        textareaRef.current?.focus();
        toast.success(`Applied "${playbook.name}" template`);
    };

    const handleCreate = async () => {
        if (!description.trim()) {
            toast.error('Please describe what you want to accomplish');
            return;
        }

        setIsCreating(true);
        try {
            await onCreateMove(description, duration);
            setDescription('');
            toast.success('Move created!');
        } catch (error) {
            toast.error('Failed to create move');
        } finally {
            setIsCreating(false);
        }
    };

    // Close menus when clicking outside
    useEffect(() => {
        const handleClickOutside = () => {
            setShowAtMenu(false);
            setShowSlashMenu(false);
        };
        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    }, []);

    return (
        <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6 mb-12">
            {/* Header */}
            <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-[#F8F9F7] border border-[#E5E6E3] flex items-center justify-center">
                    <Sparkles className="w-5 h-5 text-[#2D3538]" />
                </div>
                <div>
                    <h3 className="text-[16px] font-semibold text-[#2D3538]">What do you want to accomplish?</h3>
                    <p className="text-[13px] text-[#9D9F9F]">Describe your goal — we'll generate a daily plan</p>
                </div>
            </div>

            {/* Text Input */}
            <div className="relative">
                <textarea
                    ref={textareaRef}
                    value={description}
                    onChange={handleInput}
                    onKeyDown={handleKeyDown}
                    placeholder="e.g., Run a problem-post sprint targeting @early-stage-founders to generate 10 leads..."
                    className="w-full min-h-[120px] p-4 rounded-xl border border-[#E5E6E3] bg-[#F8F9F7] text-[15px] text-[#2D3538] placeholder:text-[#9D9F9F] resize-none focus:outline-none focus:border-[#2D3538] focus:bg-white transition-all"
                />

                {/* @ Mention Menu */}
                {showAtMenu && (
                    <div
                        className="absolute left-4 bottom-16 bg-white border border-[#E5E6E3] rounded-xl shadow-lg py-2 w-64 max-h-48 overflow-y-auto z-50"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-[#9D9F9F]">
                            Cohorts & Competitors
                        </div>
                        {filteredMentions.map((m) => (
                            <button
                                key={m.id}
                                onClick={() => insertMention(m.name)}
                                className="w-full px-3 py-2 text-left hover:bg-[#F8F9F7] transition-colors"
                            >
                                <span className="text-[14px] text-[#2D3538]">{m.name}</span>
                                <span className="ml-2 text-[11px] text-[#9D9F9F] capitalize">{m.type}</span>
                            </button>
                        ))}
                        {filteredMentions.length === 0 && (
                            <div className="px-3 py-2 text-[13px] text-[#9D9F9F]">No matches</div>
                        )}
                    </div>
                )}

                {/* Slash Command Menu */}
                {showSlashMenu && (
                    <div
                        className="absolute left-4 bottom-16 bg-white border border-[#E5E6E3] rounded-xl shadow-lg py-2 w-80 max-h-64 overflow-y-auto z-50"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-[#9D9F9F]">
                            Playbook Templates
                        </div>
                        {filteredPlaybooks.map((p) => (
                            <button
                                key={p.id}
                                onClick={() => insertPlaybook(p)}
                                className="w-full px-3 py-2.5 text-left hover:bg-[#F8F9F7] transition-colors"
                            >
                                <div className="text-[14px] font-medium text-[#2D3538]">{p.name}</div>
                                <div className="text-[12px] text-[#5B5F61] mt-0.5">{p.description}</div>
                                <div className="text-[11px] text-[#9D9F9F] mt-1">{p.duration} days</div>
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between mt-4">
                {/* Hints */}
                <div className="flex items-center gap-4 text-[12px] text-[#9D9F9F]">
                    <span className="flex items-center gap-1.5">
                        <AtSign className="w-3.5 h-3.5" />
                        cohorts
                    </span>
                    <span className="flex items-center gap-1.5">
                        <Command className="w-3.5 h-3.5" />
                        <span className="font-mono">/</span> playbooks
                    </span>
                </div>

                {/* Duration Toggle + Create */}
                <div className="flex items-center gap-4">
                    {/* Duration Pills */}
                    <div className="flex items-center gap-1 p-1 bg-[#F8F9F7] rounded-lg">
                        {[7, 14].map((d) => (
                            <button
                                key={d}
                                onClick={() => setDuration(d)}
                                className={`px-3 py-1.5 rounded-md text-[12px] font-medium transition-all ${duration === d
                                        ? 'bg-[#2D3538] text-white'
                                        : 'text-[#5B5F61] hover:text-[#2D3538]'
                                    }`}
                            >
                                {d} days
                            </button>
                        ))}
                    </div>

                    {/* Create Button */}
                    <button
                        onClick={handleCreate}
                        disabled={!description.trim() || isCreating}
                        className={`inline-flex items-center gap-2 h-10 px-5 rounded-xl text-[14px] font-medium transition-all ${description.trim()
                                ? 'bg-[#1A1D1E] text-white hover:bg-black'
                                : 'bg-[#E5E6E3] text-[#9D9F9F] cursor-not-allowed'
                            }`}
                    >
                        {isCreating ? 'Creating...' : 'Create Move'}
                        <ArrowRight className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    );
}
