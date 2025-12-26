'use client';

import React, { useState } from 'react';
import { Sheet, SheetContent } from '@/components/ui/sheet';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Move, MoveSelfReport, GOAL_LABELS, CHANNEL_LABELS, RAGStatus } from '@/lib/campaigns-types';
import {
    updateMove,
    toggleChecklistItem,
    extendMove,
} from '@/lib/campaigns';
import {
    Check,
    X,
    Target,
    Clock,
    Sparkles,
    MoreHorizontal,
    Trash2,
    Pause,
    Play,
    Copy,
    FileText,
    BarChart3,
    Activity
} from 'lucide-react';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toast } from 'sonner';

interface MoveDetailProps {
    move: Move | null;
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onUpdate: (move: Move) => void;
    onDelete: (moveId: string) => void;
    onRefresh?: () => void;
}

type TabId = 'today' | 'plan' | 'assets' | 'results' | 'log';

interface Tab {
    id: TabId;
    label: string;
    icon: React.ReactNode;
}

const TABS: Tab[] = [
    { id: 'today', label: 'Today', icon: <Clock style={{ width: 14, height: 14 }} /> },
    { id: 'plan', label: 'Plan', icon: <FileText style={{ width: 14, height: 14 }} /> },
    { id: 'assets', label: 'Assets', icon: <Sparkles style={{ width: 14, height: 14 }} /> },
    { id: 'results', label: 'Results', icon: <BarChart3 style={{ width: 14, height: 14 }} /> },
    { id: 'log', label: 'Activity', icon: <Activity style={{ width: 14, height: 14 }} /> },
];

function calculateRAG(move: Move): { status: RAGStatus; reason: string } {
    if (move.rag && move.ragReason) {
        return { status: move.rag, reason: move.ragReason };
    }
    return { status: 'green', reason: 'On pace' };
}

function getDayNumber(move: Move): number {
    if (!move.startedAt) return 0;
    const now = new Date();
    const startedAt = new Date(move.startedAt);
    const daysElapsed = Math.floor((now.getTime() - startedAt.getTime()) / (1000 * 60 * 60 * 24)) + 1;
    return Math.min(daysElapsed, move.duration);
}

export function MoveDetail({ move, open, onOpenChange, onUpdate, onDelete, onRefresh }: MoveDetailProps) {
    const [activeTab, setActiveTab] = useState<TabId>('today');
    const [completing, setCompleting] = useState(false);
    const [whatHappened, setWhatHappened] = useState('');
    const [metricValue, setMetricValue] = useState('');
    const [confirmDelete, setConfirmDelete] = useState(false);

    // Quick log state
    const [logLeads, setLogLeads] = useState(0);
    const [logReplies, setLogReplies] = useState(0);
    const [logCalls, setLogCalls] = useState(0);
    const [logConfidence, setLogConfidence] = useState(7);

    if (!move) return null;

    const rag = calculateRAG(move);
    const dayNumber = getDayNumber(move);
    const totalTasks = move.checklist?.length || 0;
    const completedTasks = move.checklist?.filter(t => t.completed).length || 0;
    const progress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

    const handleToggleChecklist = (itemId: string) => {
        toggleChecklistItem(move.id, itemId);
        const updatedChecklist = move.checklist.map(item =>
            item.id === itemId ? { ...item, completed: !item.completed } : item
        );
        onUpdate({ ...move, checklist: updatedChecklist });
    };

    const handlePause = async () => {
        const updated = { ...move, status: 'paused' as const, pausedAt: new Date().toISOString() };
        await updateMove(updated);
        onUpdate(updated);
        toast.info('Move paused');
    };

    const handleResume = async () => {
        const updated = { ...move, status: 'active' as const, pausedAt: undefined };
        await updateMove(updated);
        onUpdate(updated);
        toast.success('Move resumed');
    };

    const handleActivate = async () => {
        const now = new Date().toISOString();
        const dueDate = new Date(Date.now() + move.duration * 24 * 60 * 60 * 1000).toISOString();
        const updated = {
            ...move,
            status: 'active' as const,
            startedAt: now,
            dueDate
        };
        await updateMove(updated);
        onUpdate(updated);
        if (onRefresh) onRefresh();
        toast.success('Move activated!');
    };

    const handleDeleteConfirm = () => {
        onDelete(move.id);
        setConfirmDelete(false);
        onOpenChange(false);
    };

    const handleComplete = () => {
        setCompleting(true);
    };

    const submitCompletion = async () => {
        const report: MoveSelfReport = {
            didComplete: true,
            whatHappened,
            metrics: metricValue ? { name: move.goal, value: parseInt(metricValue) } : undefined,
            submittedAt: new Date().toISOString(),
        };

        const updated: Move = {
            ...move,
            status: 'completed',
            completedAt: new Date().toISOString(),
            selfReport: report
        };

        await updateMove(updated);
        onUpdate(updated);
        if (onRefresh) onRefresh();
        setCompleting(false);
        onOpenChange(false);
        toast.success('Move completed!');
    };

    const handleSaveLog = async () => {
        const newMetrics = {
            leads: logLeads,
            replies: logReplies,
            calls: logCalls,
            energy: 7,
            quality: 7,
            executed: true,
            submittedAt: new Date().toISOString()
        };

        const updated = {
            ...move,
            confidence: logConfidence,
            dailyMetrics: [...(move.dailyMetrics || []), newMetrics]
        };

        await updateMove(updated);
        onUpdate(updated);
        toast.success('Progress logged');
    };

    // Get today's tasks (incomplete ones)
    const todaysTasks = move.checklist?.filter(t => !t.completed).slice(0, 5) || [];

    // Get today's asset (first draft asset)
    const todaysAsset = move.assets?.find(a => a.status === 'draft');

    const renderTabContent = () => {
        switch (activeTab) {
            case 'today':
                return (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                        {/* Today's Tasks */}
                        <div>
                            <h4 style={{
                                fontFamily: 'Inter, sans-serif',
                                fontSize: 11,
                                fontWeight: 600,
                                textTransform: 'uppercase',
                                letterSpacing: '0.15em',
                                color: '#9D9F9F',
                                marginBottom: 12
                            }}>
                                Tasks ({move.dailyEffort}m)
                            </h4>
                            <div style={{
                                background: '#FFFFFF',
                                border: '1px solid #E5E6E3',
                                borderRadius: 16,
                                overflow: 'hidden'
                            }}>
                                {todaysTasks.length > 0 ? todaysTasks.map(task => (
                                    <div
                                        key={task.id}
                                        onClick={() => handleToggleChecklist(task.id)}
                                        style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: 12,
                                            padding: 16,
                                            borderBottom: '1px solid #F8F9F7',
                                            cursor: 'pointer',
                                            transition: 'background 150ms ease'
                                        }}
                                    >
                                        <div style={{
                                            width: 20,
                                            height: 20,
                                            borderRadius: 6,
                                            border: '1px solid #E5E6E3',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center'
                                        }}>
                                            {task.completed && <Check style={{ width: 12, height: 12, color: '#22C55E' }} />}
                                        </div>
                                        <span style={{
                                            fontFamily: 'Inter, sans-serif',
                                            fontSize: 14,
                                            color: '#2D3538'
                                        }}>
                                            {task.label}
                                        </span>
                                    </div>
                                )) : (
                                    <div style={{ padding: 24, textAlign: 'center', color: '#9D9F9F' }}>
                                        All tasks completed! 🎉
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Today's Asset */}
                        {todaysAsset && (
                            <div>
                                <h4 style={{
                                    fontFamily: 'Inter, sans-serif',
                                    fontSize: 11,
                                    fontWeight: 600,
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.15em',
                                    color: '#9D9F9F',
                                    marginBottom: 12
                                }}>
                                    Today's Asset
                                </h4>
                                <div style={{
                                    background: '#FFFFFF',
                                    border: '1px solid #E5E6E3',
                                    borderRadius: 16,
                                    padding: 20
                                }}>
                                    <div style={{
                                        fontFamily: 'Inter, sans-serif',
                                        fontSize: 14,
                                        fontWeight: 500,
                                        color: '#2D3538',
                                        marginBottom: 12
                                    }}>
                                        {todaysAsset.title}
                                    </div>
                                    <p style={{
                                        fontFamily: 'Inter, sans-serif',
                                        fontSize: 13,
                                        color: '#5B5F61',
                                        lineHeight: 1.6,
                                        marginBottom: 16
                                    }}>
                                        {todaysAsset.content.slice(0, 200)}...
                                    </p>
                                    <div style={{ display: 'flex', gap: 8 }}>
                                        <Button variant="outline" size="sm">
                                            <Copy style={{ width: 14, height: 14, marginRight: 6 }} />
                                            Copy
                                        </Button>
                                        <Button variant="outline" size="sm">
                                            Mark Used
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Quick Log */}
                        <div>
                            <h4 style={{
                                fontFamily: 'Inter, sans-serif',
                                fontSize: 11,
                                fontWeight: 600,
                                textTransform: 'uppercase',
                                letterSpacing: '0.15em',
                                color: '#9D9F9F',
                                marginBottom: 12
                            }}>
                                Quick Log Progress
                            </h4>
                            <div style={{
                                background: '#FFFFFF',
                                border: '1px solid #E5E6E3',
                                borderRadius: 16,
                                padding: 20
                            }}>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 16 }}>
                                    <div>
                                        <label style={{ fontSize: 11, color: '#9D9F9F', display: 'block', marginBottom: 4 }}>Replies</label>
                                        <input
                                            type="number"
                                            value={logReplies}
                                            onChange={(e) => setLogReplies(parseInt(e.target.value) || 0)}
                                            style={{
                                                width: '100%',
                                                padding: '8px 12px',
                                                border: '1px solid #E5E6E3',
                                                borderRadius: 8,
                                                fontFamily: 'JetBrains Mono, monospace',
                                                fontSize: 14
                                            }}
                                        />
                                    </div>
                                    <div>
                                        <label style={{ fontSize: 11, color: '#9D9F9F', display: 'block', marginBottom: 4 }}>Leads</label>
                                        <input
                                            type="number"
                                            value={logLeads}
                                            onChange={(e) => setLogLeads(parseInt(e.target.value) || 0)}
                                            style={{
                                                width: '100%',
                                                padding: '8px 12px',
                                                border: '1px solid #E5E6E3',
                                                borderRadius: 8,
                                                fontFamily: 'JetBrains Mono, monospace',
                                                fontSize: 14
                                            }}
                                        />
                                    </div>
                                    <div>
                                        <label style={{ fontSize: 11, color: '#9D9F9F', display: 'block', marginBottom: 4 }}>Calls</label>
                                        <input
                                            type="number"
                                            value={logCalls}
                                            onChange={(e) => setLogCalls(parseInt(e.target.value) || 0)}
                                            style={{
                                                width: '100%',
                                                padding: '8px 12px',
                                                border: '1px solid #E5E6E3',
                                                borderRadius: 8,
                                                fontFamily: 'JetBrains Mono, monospace',
                                                fontSize: 14
                                            }}
                                        />
                                    </div>
                                </div>
                                <div style={{ marginBottom: 16 }}>
                                    <label style={{ fontSize: 11, color: '#9D9F9F', display: 'block', marginBottom: 4 }}>Confidence (1-10)</label>
                                    <input
                                        type="range"
                                        min="1"
                                        max="10"
                                        value={logConfidence}
                                        onChange={(e) => setLogConfidence(parseInt(e.target.value))}
                                        style={{ width: '100%' }}
                                    />
                                    <div style={{ textAlign: 'center', fontFamily: 'JetBrains Mono', fontSize: 14 }}>{logConfidence}/10</div>
                                </div>
                                <Button onClick={handleSaveLog} style={{ width: '100%' }}>
                                    Save Log
                                </Button>
                            </div>
                        </div>
                    </div>
                );

            case 'plan':
                const groups = {
                    setup: move.checklist?.filter(i => i.group === 'setup') || [],
                    create: move.checklist?.filter(i => i.group === 'create') || [],
                    publish: move.checklist?.filter(i => i.group === 'publish') || [],
                    followup: move.checklist?.filter(i => i.group === 'followup') || [],
                };

                return (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                        {Object.entries(groups).map(([group, items]) => items.length > 0 && (
                            <div key={group}>
                                <h4 style={{
                                    fontFamily: 'Inter, sans-serif',
                                    fontSize: 11,
                                    fontWeight: 600,
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.15em',
                                    color: '#9D9F9F',
                                    marginBottom: 12
                                }}>
                                    {group} Phase
                                </h4>
                                <div style={{
                                    background: '#FFFFFF',
                                    border: '1px solid #E5E6E3',
                                    borderRadius: 16,
                                    overflow: 'hidden'
                                }}>
                                    {items.map(item => (
                                        <div
                                            key={item.id}
                                            onClick={() => handleToggleChecklist(item.id)}
                                            style={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: 12,
                                                padding: 16,
                                                borderBottom: '1px solid #F8F9F7',
                                                cursor: 'pointer'
                                            }}
                                        >
                                            <div style={{
                                                width: 20,
                                                height: 20,
                                                borderRadius: 6,
                                                border: item.completed ? 'none' : '1px solid #E5E6E3',
                                                background: item.completed ? '#22C55E' : 'transparent',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center'
                                            }}>
                                                {item.completed && <Check style={{ width: 12, height: 12, color: '#FFFFFF' }} />}
                                            </div>
                                            <span style={{
                                                fontFamily: 'Inter, sans-serif',
                                                fontSize: 14,
                                                color: item.completed ? '#9D9F9F' : '#2D3538',
                                                textDecoration: item.completed ? 'line-through' : 'none'
                                            }}>
                                                {item.label}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                );

            case 'assets':
                return (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                        {move.assets && move.assets.length > 0 ? move.assets.map(asset => (
                            <div key={asset.id} style={{
                                background: '#FFFFFF',
                                border: '1px solid #E5E6E3',
                                borderRadius: 16,
                                padding: 20
                            }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                                    <span style={{
                                        fontFamily: 'Inter',
                                        fontSize: 14,
                                        fontWeight: 500,
                                        color: '#2D3538'
                                    }}>
                                        {asset.title}
                                    </span>
                                    <span style={{
                                        fontSize: 10,
                                        fontWeight: 600,
                                        textTransform: 'uppercase',
                                        padding: '4px 8px',
                                        background: asset.status === 'used' ? '#E5E6E3' : '#F8F9F7',
                                        borderRadius: 6,
                                        color: '#5B5F61'
                                    }}>
                                        {asset.status}
                                    </span>
                                </div>
                                <p style={{
                                    fontFamily: 'Inter',
                                    fontSize: 13,
                                    color: '#5B5F61',
                                    lineHeight: 1.6
                                }}>
                                    {asset.content.slice(0, 150)}...
                                </p>
                            </div>
                        )) : (
                            <div style={{
                                textAlign: 'center',
                                padding: 48,
                                color: '#9D9F9F'
                            }}>
                                <Sparkles style={{ width: 32, height: 32, marginBottom: 12, opacity: 0.3 }} />
                                <p>No assets generated yet</p>
                                <Button variant="outline" style={{ marginTop: 16 }}>
                                    Generate Assets
                                </Button>
                            </div>
                        )}
                    </div>
                );

            case 'results':
                const latestMetrics = move.dailyMetrics?.[move.dailyMetrics.length - 1];
                return (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                        {/* Outcome vs Target */}
                        <div style={{
                            background: '#FFFFFF',
                            border: '1px solid #E5E6E3',
                            borderRadius: 16,
                            padding: 24
                        }}>
                            <h4 style={{
                                fontFamily: 'Inter',
                                fontSize: 11,
                                fontWeight: 600,
                                textTransform: 'uppercase',
                                letterSpacing: '0.15em',
                                color: '#9D9F9F',
                                marginBottom: 16
                            }}>
                                Progress vs Target
                            </h4>
                            <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                                <span style={{
                                    fontFamily: 'Playfair Display',
                                    fontSize: 48,
                                    fontWeight: 500,
                                    color: '#2D3538'
                                }}>
                                    {latestMetrics?.calls || latestMetrics?.leads || 0}
                                </span>
                                <span style={{
                                    fontFamily: 'Inter',
                                    fontSize: 18,
                                    color: '#9D9F9F'
                                }}>
                                    / {move.targetNumber || 10} {move.outcomeType || 'calls'}
                                </span>
                            </div>
                        </div>

                        {/* Daily Metrics History */}
                        {move.dailyMetrics && move.dailyMetrics.length > 0 && (
                            <div>
                                <h4 style={{
                                    fontFamily: 'Inter',
                                    fontSize: 11,
                                    fontWeight: 600,
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.15em',
                                    color: '#9D9F9F',
                                    marginBottom: 12
                                }}>
                                    Daily Check-ins
                                </h4>
                                <div style={{
                                    background: '#FFFFFF',
                                    border: '1px solid #E5E6E3',
                                    borderRadius: 16,
                                    overflow: 'hidden'
                                }}>
                                    {move.dailyMetrics.slice(-7).reverse().map((m, i) => (
                                        <div key={i} style={{
                                            display: 'flex',
                                            justifyContent: 'space-between',
                                            padding: 16,
                                            borderBottom: '1px solid #F8F9F7'
                                        }}>
                                            <span style={{ fontFamily: 'Inter', fontSize: 13, color: '#5B5F61' }}>
                                                {m.submittedAt ? new Date(m.submittedAt).toLocaleDateString() : 'Today'}
                                            </span>
                                            <div style={{ display: 'flex', gap: 16, fontFamily: 'JetBrains Mono', fontSize: 12 }}>
                                                <span>{m.leads}L</span>
                                                <span>{m.replies}R</span>
                                                <span>{m.calls}C</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                );

            case 'log':
                return (
                    <div style={{
                        textAlign: 'center',
                        padding: 48,
                        color: '#9D9F9F'
                    }}>
                        <Activity style={{ width: 32, height: 32, marginBottom: 12, opacity: 0.3 }} />
                        <p>Activity log coming soon</p>
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <Sheet open={open} onOpenChange={onOpenChange}>
            <SheetContent
                side="right"
                style={{
                    width: 480,
                    maxWidth: '100vw',
                    padding: 0,
                    background: '#F8F9F7',
                    borderLeft: '1px solid #E5E6E3'
                }}
            >
                {/* Header */}
                <div style={{
                    padding: 24,
                    background: '#FFFFFF',
                    borderBottom: '1px solid #E5E6E3'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                        <div>
                            <h2 style={{
                                fontFamily: 'Playfair Display, Georgia, serif',
                                fontSize: 24,
                                fontWeight: 500,
                                color: '#2D3538',
                                marginBottom: 8
                            }}>
                                {move.name}
                            </h2>
                            <div style={{ display: 'flex', gap: 8 }}>
                                <span style={{
                                    fontSize: 10,
                                    fontWeight: 600,
                                    textTransform: 'uppercase',
                                    padding: '4px 8px',
                                    background: '#F8F9F7',
                                    borderRadius: 6,
                                    color: '#5B5F61'
                                }}>
                                    {GOAL_LABELS[move.goal]?.label}
                                </span>
                                <span style={{
                                    fontSize: 10,
                                    fontWeight: 600,
                                    textTransform: 'uppercase',
                                    padding: '4px 8px',
                                    background: '#F8F9F7',
                                    borderRadius: 6,
                                    color: '#5B5F61'
                                }}>
                                    {CHANNEL_LABELS[move.channel]}
                                </span>
                            </div>
                        </div>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon">
                                    <MoreHorizontal style={{ width: 16, height: 16 }} />
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                                <DropdownMenuItem
                                    onClick={() => setConfirmDelete(true)}
                                    style={{ color: '#DC2626' }}
                                >
                                    <Trash2 style={{ width: 14, height: 14, marginRight: 8 }} />
                                    Delete Move
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </div>

                    {/* Status Row */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                <Clock style={{ width: 14, height: 14, color: '#9D9F9F' }} />
                                <span style={{ fontFamily: 'JetBrains Mono', fontSize: 12, color: '#2D3538' }}>
                                    Day {dayNumber}/{move.duration}
                                </span>
                            </div>
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 6,
                                padding: '4px 10px',
                                background: rag.status === 'green' ? 'rgba(34, 197, 94, 0.1)' :
                                    rag.status === 'amber' ? 'rgba(245, 158, 11, 0.1)' :
                                        'rgba(239, 68, 68, 0.1)',
                                borderRadius: 6
                            }}>
                                <div style={{
                                    width: 6,
                                    height: 6,
                                    borderRadius: '50%',
                                    background: rag.status === 'green' ? '#22C55E' :
                                        rag.status === 'amber' ? '#F59E0B' : '#EF4444'
                                }} />
                                <span style={{
                                    fontFamily: 'Inter',
                                    fontSize: 11,
                                    fontWeight: 600,
                                    textTransform: 'uppercase',
                                    color: rag.status === 'green' ? '#16A34A' :
                                        rag.status === 'amber' ? '#D97706' : '#DC2626'
                                }}>
                                    {rag.status}
                                </span>
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: 8 }}>
                            {move.status === 'queued' && (
                                <Button variant="default" size="sm" onClick={handleActivate}>
                                    <Play style={{ width: 14, height: 14, marginRight: 4 }} />
                                    Activate
                                </Button>
                            )}
                            {move.status === 'active' && (
                                <Button variant="outline" size="sm" onClick={handlePause}>
                                    <Pause style={{ width: 14, height: 14 }} />
                                </Button>
                            )}
                            {move.status === 'paused' && (
                                <Button variant="outline" size="sm" onClick={handleResume}>
                                    <Play style={{ width: 14, height: 14 }} />
                                </Button>
                            )}
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div style={{
                    display: 'flex',
                    gap: 4,
                    padding: '12px 24px',
                    background: '#FFFFFF',
                    borderBottom: '1px solid #E5E6E3'
                }}>
                    {TABS.map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 6,
                                padding: '8px 12px',
                                background: activeTab === tab.id ? '#1A1D1E' : 'transparent',
                                color: activeTab === tab.id ? '#FFFFFF' : '#5B5F61',
                                border: 'none',
                                borderRadius: 8,
                                fontFamily: 'Inter, sans-serif',
                                fontSize: 12,
                                fontWeight: 500,
                                cursor: 'pointer',
                                transition: 'all 150ms ease'
                            }}
                        >
                            {tab.icon}
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Tab Content */}
                <div style={{ padding: 24, overflowY: 'auto', height: 'calc(100vh - 280px)' }}>
                    {completing ? (
                        <div style={{
                            background: '#FFFFFF',
                            border: '1px solid #E5E6E3',
                            borderRadius: 16,
                            padding: 24
                        }}>
                            <h3 style={{
                                fontFamily: 'Playfair Display',
                                fontSize: 20,
                                marginBottom: 24
                            }}>
                                Complete Move
                            </h3>
                            <div style={{ marginBottom: 16 }}>
                                <label style={{ fontSize: 12, color: '#9D9F9F', display: 'block', marginBottom: 8 }}>
                                    What happened?
                                </label>
                                <textarea
                                    value={whatHappened}
                                    onChange={e => setWhatHappened(e.target.value)}
                                    placeholder="Brief summary..."
                                    style={{
                                        width: '100%',
                                        minHeight: 100,
                                        padding: 12,
                                        border: '1px solid #E5E6E3',
                                        borderRadius: 12,
                                        fontFamily: 'Inter',
                                        fontSize: 14,
                                        resize: 'none'
                                    }}
                                />
                            </div>
                            <div style={{ display: 'flex', gap: 12 }}>
                                <Button variant="outline" onClick={() => setCompleting(false)}>Cancel</Button>
                                <Button onClick={submitCompletion}>Complete</Button>
                            </div>
                        </div>
                    ) : (
                        renderTabContent()
                    )}
                </div>

                {/* Footer */}
                {!completing && move.status === 'active' && (
                    <div style={{
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        right: 0,
                        padding: 24,
                        background: '#FFFFFF',
                        borderTop: '1px solid #E5E6E3',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                    }}>
                        <span style={{ fontFamily: 'JetBrains Mono', fontSize: 12, color: '#9D9F9F' }}>
                            {completedTasks}/{totalTasks} tasks
                        </span>
                        <Button onClick={handleComplete}>
                            Complete Move
                        </Button>
                    </div>
                )}
            </SheetContent>

            {/* Delete Confirmation Dialog */}
            <Dialog open={confirmDelete} onOpenChange={setConfirmDelete}>
                <DialogContent style={{ maxWidth: 400 }}>
                    <DialogHeader>
                        <DialogTitle style={{ fontFamily: 'Playfair Display, Georgia, serif' }}>
                            Delete Move?
                        </DialogTitle>
                        <DialogDescription>
                            This will permanently delete "{move.name}" and all associated data. This action cannot be undone.
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter style={{ gap: 12 }}>
                        <Button variant="outline" onClick={() => setConfirmDelete(false)}>
                            Cancel
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={handleDeleteConfirm}
                            style={{ background: '#DC2626' }}
                        >
                            <Trash2 style={{ width: 14, height: 14, marginRight: 6 }} />
                            Delete
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </Sheet>
    );
}
