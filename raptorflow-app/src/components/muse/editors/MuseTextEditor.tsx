'use client';

import React, { useState, useRef, useCallback, useMemo, useEffect } from 'react';
import { cn } from '@/lib/utils';
import {
    Bold,
    Italic,
    Heading1,
    Heading2,
    List,
    ListOrdered,
    Quote,
    Sparkles,
    Wand2,
    Minimize2,
    Maximize2,
    Download,
    X,
    Mic,
    TrendingUp,
    ArrowLeftRight,
    MessageCircle,
    ChevronRight,
    ChevronLeft,
    Clock,
    Link2 as LinkIcon,
    Copy,
    Share2,
    FileText,
    FileCode,
    Globe,
    Check,
    MoreVertical,
    Maximize,
    Keyboard,
    Zap,
    Hash,
    AtSign,
    Loader2
} from 'lucide-react';
import { ToneSliderCompact } from '../ToneSlider';
import { HookScore, HookScoreBadge } from '../HookScore';
import { BrandVoicePanel, BrandVoiceBadge } from '../BrandVoicePanel';
import { PredictionPanel } from '../PredictionPanel';
import { VersionHistory } from '../VersionHistory';
import { SchedulePublish } from '../SchedulePublish';
import { AssetChainPanel } from '../AssetChainPanel';
import { Asset } from '../types';
import {
    exportContent,
    copyToClipboard,
    shareContent,
    EXPORT_OPTIONS,
    ExportFormat
} from '../utils/exports';

interface MuseTextEditorProps {
    initialContent?: string;
    title?: string;
    currentAsset?: Asset;
    allAssets?: Asset[];
    onSave?: (content: string) => void;
    onClose?: () => void;
    onOpenSplitEditor?: () => void;
    className?: string;
}

// AI actions for selection
const AI_ACTIONS = [
    { id: 'improve', label: 'Improve', icon: Wand2, description: 'Enhance clarity and impact' },
    { id: 'shorten', label: 'Shorten', icon: Minimize2, description: 'Make it more concise' },
    { id: 'expand', label: 'Expand', icon: Maximize2, description: 'Add more detail' },
    { id: 'tone-professional', label: 'Professional Tone', icon: Sparkles, description: 'Make it sound formal' },
    { id: 'tone-casual', label: 'Casual Tone', icon: Sparkles, description: 'Make it conversational' },
];

// Quick insert snippets
const QUICK_SNIPPETS = [
    { id: 'cta', label: 'CTA', text: '\n\n👉 [Your Call to Action Here]' },
    { id: 'signoff', label: 'Sign-off', text: '\n\nBest,\n[Your Name]' },
    { id: 'ps', label: 'P.S.', text: '\n\nP.S. ' },
    { id: 'divider', label: '---', text: '\n\n---\n\n' },
    { id: 'bullet', label: '• List', text: '\n• Item 1\n• Item 2\n• Item 3' },
];

// Keyboard shortcuts
const KEYBOARD_SHORTCUTS = [
    { keys: '⌘S', action: 'Save' },
    { keys: '⌘B', action: 'Bold' },
    { keys: '⌘I', action: 'Italic' },
    { keys: 'Esc', action: 'Close panel' },
];

type SidePanel = 'ai' | 'brand' | 'predictions' | 'hook' | 'history' | 'chain' | null;

export function MuseTextEditor({
    initialContent = '',
    title = 'Untitled Asset',
    currentAsset,
    allAssets = [],
    onSave,
    onClose,
    onOpenSplitEditor,
    className
}: MuseTextEditorProps) {
    const [content, setContent] = useState(initialContent);
    const [activePanel, setActivePanel] = useState<SidePanel>(null);
    const [showSchedule, setShowSchedule] = useState(false);
    const [selectedText, setSelectedText] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [tone, setTone] = useState(50);
    const [showExportMenu, setShowExportMenu] = useState(false);
    const [copied, setCopied] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [lastSaved, setLastSaved] = useState<Date | null>(null);
    const [showSnippets, setShowSnippets] = useState(false);
    const [showShortcuts, setShowShortcuts] = useState(false);
    const editorRef = useRef<HTMLTextAreaElement>(null);

    // Word count and stats
    const wordCount = content.trim().split(/\s+/).filter(Boolean).length;
    const charCount = content.length;
    const readingTime = Math.max(1, Math.ceil(wordCount / 200));

    // Get first line for hook scoring
    const firstLine = useMemo(() => {
        const lines = content.split('\n').filter(l => l.trim());
        return lines[0] || '';
    }, [content]);

    // Handle text selection
    const handleSelect = useCallback(() => {
        const textarea = editorRef.current;
        if (!textarea) return;

        const selected = content.substring(textarea.selectionStart, textarea.selectionEnd);
        setSelectedText(selected);
        if (selected.length > 0) {
            setActivePanel('ai');
        }
    }, [content]);

    // Mock AI action
    const handleAIAction = async (actionId: string) => {
        if (!selectedText) return;

        setIsProcessing(true);
        await new Promise(resolve => setTimeout(resolve, 1500));

        let transformed = selectedText;
        switch (actionId) {
            case 'improve':
                transformed = `[Enhanced] ${selectedText}`;
                break;
            case 'shorten':
                transformed = selectedText.split(' ').slice(0, Math.ceil(selectedText.split(' ').length / 2)).join(' ') + '...';
                break;
            case 'expand':
                transformed = `${selectedText} [Additional context and supporting details would be added here.]`;
                break;
            case 'tone-professional':
                transformed = `[Professional tone] ${selectedText}`;
                break;
            case 'tone-casual':
                transformed = `[Casual tone] ${selectedText}`;
                break;
        }

        const textarea = editorRef.current;
        if (textarea) {
            const start = content.indexOf(selectedText);
            const newContent = content.substring(0, start) + transformed + content.substring(start + selectedText.length);
            setContent(newContent);
        }

        setIsProcessing(false);
        setActivePanel(null);
        setSelectedText('');
    };

    const togglePanel = (panel: SidePanel) => {
        setActivePanel(activePanel === panel ? null : panel);
    };

    // Export handlers
    const handleExport = (format: ExportFormat) => {
        exportContent(content, title, format);
        setShowExportMenu(false);
    };

    const handleCopy = async () => {
        const success = await copyToClipboard(content);
        if (success) {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const handleShare = async () => {
        await shareContent(title, content);
    };

    // Save with feedback
    const handleSaveWithFeedback = async () => {
        setIsSaving(true);
        await new Promise(r => setTimeout(r, 500)); // Simulate save
        onSave?.(content);
        setIsSaving(false);
        setLastSaved(new Date());
    };

    // Insert snippet at cursor
    const insertSnippet = (text: string) => {
        const textarea = editorRef.current;
        if (textarea) {
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const newContent = content.substring(0, start) + text + content.substring(end);
            setContent(newContent);
            // Move cursor to end of inserted text
            setTimeout(() => {
                textarea.selectionStart = textarea.selectionEnd = start + text.length;
                textarea.focus();
            }, 0);
        }
        setShowSnippets(false);
    };

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 's') {
                e.preventDefault();
                handleSaveWithFeedback();
            }
            if (e.key === 'Escape') {
                setActivePanel(null);
                setShowExportMenu(false);
                setShowSnippets(false);
                setShowShortcuts(false);
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [content, title]);

    // Format last saved time
    const formatLastSaved = (date: Date) => {
        const now = new Date();
        const diff = Math.floor((now.getTime() - date.getTime()) / 1000);
        if (diff < 60) return 'just now';
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className={cn('flex flex-col h-full bg-[#F8F9F7]', className)}>
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-[#E5E6E3] bg-white">
                <div className="flex items-center gap-4">
                    {onClose && (
                        <button
                            onClick={onClose}
                            className="h-8 w-8 rounded-lg flex items-center justify-center hover:bg-[#F8F9F7] transition-colors"
                        >
                            <X className="h-4 w-4 text-[#5B5F61]" />
                        </button>
                    )}
                    <div>
                        <h1 className="text-lg font-semibold text-[#2D3538]">{title}</h1>
                        <div className="flex items-center gap-2 text-xs text-[#9D9F9F]">
                            <span>{wordCount} words</span>
                            <span>•</span>
                            <span>{readingTime} min read</span>
                            <span>•</span>
                            {isSaving ? (
                                <span className="flex items-center gap-1 text-amber-500">
                                    <Loader2 className="h-3 w-3 animate-spin" />
                                    Saving...
                                </span>
                            ) : lastSaved ? (
                                <span className="text-green-600">✓ Saved {formatLastSaved(lastSaved)}</span>
                            ) : (
                                <span className="text-muted-foreground/50">Not saved</span>
                            )}
                            {firstLine && <HookScoreBadge text={firstLine} className="ml-2" />}
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    {/* Tone slider in header */}
                    <div className="w-36 px-3">
                        <ToneSliderCompact
                            value={tone}
                            onChange={(v) => setTone(v)}
                        />
                    </div>

                    <div className="w-px h-6 bg-border/40" />

                    {onOpenSplitEditor && (
                        <button
                            onClick={onOpenSplitEditor}
                            className={cn(
                                'flex items-center gap-1.5 h-8 px-3 rounded-lg',
                                'border border-border/60 text-sm',
                                'hover:bg-muted transition-colors'
                            )}
                        >
                            <ArrowLeftRight className="h-3.5 w-3.5" />
                            A/B
                        </button>
                    )}

                    {/* Copy button */}
                    <button
                        onClick={handleCopy}
                        title="Copy to clipboard"
                        className="h-9 w-9 rounded-lg flex items-center justify-center hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
                    >
                        {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                    </button>

                    {/* Share button */}
                    <button
                        onClick={handleShare}
                        title="Share"
                        className="h-9 w-9 rounded-lg flex items-center justify-center hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
                    >
                        <Share2 className="h-4 w-4" />
                    </button>

                    {/* Export dropdown */}
                    <div className="relative">
                        <button
                            onClick={() => setShowExportMenu(!showExportMenu)}
                            title="Download"
                            className="h-9 w-9 rounded-lg flex items-center justify-center hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
                        >
                            <Download className="h-4 w-4" />
                        </button>

                        {showExportMenu && (
                            <div className="absolute right-0 top-full mt-2 w-48 bg-card border border-border/60 rounded-xl shadow-xl z-50 overflow-hidden">
                                <div className="p-2 border-b border-border/40">
                                    <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide px-2">Export As</span>
                                </div>
                                {EXPORT_OPTIONS.map((opt) => (
                                    <button
                                        key={opt.id}
                                        onClick={() => handleExport(opt.id)}
                                        className="w-full flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-muted transition-colors text-left"
                                    >
                                        {opt.id === 'txt' && <FileText className="h-4 w-4 text-muted-foreground" />}
                                        {opt.id === 'md' && <FileCode className="h-4 w-4 text-muted-foreground" />}
                                        {opt.id === 'doc' && <FileText className="h-4 w-4 text-blue-500" />}
                                        {opt.id === 'html' && <Globe className="h-4 w-4 text-orange-500" />}
                                        <span>{opt.label}</span>
                                        <span className="ml-auto text-xs text-muted-foreground">{opt.extension}</span>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="w-px h-6 bg-border/40" />

                    <button
                        onClick={handleSaveWithFeedback}
                        disabled={isSaving}
                        className={cn(
                            'h-9 px-4 rounded-lg',
                            'bg-[#1a1d1e] text-white',
                            'text-sm font-medium',
                            'hover:bg-[#2D3538] transition-colors',
                            'disabled:opacity-70'
                        )}
                    >
                        {isSaving ? 'Saving...' : 'Save'}
                    </button>
                </div>
            </div>

            {/* Toolbar */}
            <div className="flex items-center gap-1 px-6 py-2 border-b border-[#E5E6E3] bg-white">
                <ToolbarButton icon={Bold} label="Bold" />
                <ToolbarButton icon={Italic} label="Italic" />
                <div className="w-px h-5 bg-border/40 mx-1" />
                <ToolbarButton icon={Heading1} label="Heading 1" />
                <ToolbarButton icon={Heading2} label="Heading 2" />
                <div className="w-px h-5 bg-border/40 mx-1" />
                <ToolbarButton icon={List} label="Bullet List" />
                <ToolbarButton icon={ListOrdered} label="Numbered List" />
                <ToolbarButton icon={Quote} label="Quote" />

                <div className="w-px h-5 bg-border/40 mx-1" />

                {/* Quick Insert Snippets */}
                <div className="relative">
                    <button
                        onClick={() => setShowSnippets(!showSnippets)}
                        title="Insert snippet"
                        className={cn(
                            'flex items-center gap-1.5 h-8 px-3 rounded-md text-sm',
                            'hover:bg-muted transition-colors',
                            showSnippets && 'bg-muted'
                        )}
                    >
                        <Zap className="h-3.5 w-3.5" />
                        Insert
                    </button>
                    {showSnippets && (
                        <div className="absolute left-0 top-full mt-1 w-40 bg-card border border-border/60 rounded-lg shadow-lg z-50 overflow-hidden">
                            {QUICK_SNIPPETS.map(snippet => (
                                <button
                                    key={snippet.id}
                                    onClick={() => insertSnippet(snippet.text)}
                                    className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-muted transition-colors text-left"
                                >
                                    {snippet.label}
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Keyboard Shortcuts Help */}
                <div className="relative">
                    <button
                        onClick={() => setShowShortcuts(!showShortcuts)}
                        title="Keyboard shortcuts"
                        className={cn(
                            'h-8 w-8 rounded-md flex items-center justify-center',
                            'hover:bg-muted transition-colors',
                            showShortcuts && 'bg-muted'
                        )}
                    >
                        <Keyboard className="h-4 w-4 text-muted-foreground" />
                    </button>
                    {showShortcuts && (
                        <div className="absolute left-0 top-full mt-1 w-48 bg-card border border-border/60 rounded-lg shadow-lg z-50 p-3">
                            <p className="text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wide">Shortcuts</p>
                            <div className="space-y-1">
                                {KEYBOARD_SHORTCUTS.map(sc => (
                                    <div key={sc.keys} className="flex items-center justify-between text-sm">
                                        <span className="text-muted-foreground">{sc.action}</span>
                                        <kbd className="px-1.5 py-0.5 rounded bg-muted font-mono text-xs">{sc.keys}</kbd>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                <div className="flex-1" />

                {/* Status indicators (Passive) */}
                <div className="flex items-center gap-4 text-xs text-muted-foreground/60">
                    <div className="flex items-center gap-1">
                        <div className="h-1.5 w-1.5 rounded-full bg-green-500/50" />
                        Brand Aligned
                    </div>
                    <div className="flex items-center gap-1">
                        <div className="h-1.5 w-1.5 rounded-full bg-blue-500/50" />
                        Hook: 82%
                    </div>
                </div>
            </div>

            {/* Main editor container */}
            <div className="flex-1 flex overflow-hidden">
                {/* Editor Content Area */}
                <div className="flex-1 flex flex-col relative min-w-0">
                    {/* Helper for centered modal */}
                    {showSchedule && (
                        <div className="absolute inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
                            <div className="w-full max-w-md bg-card border border-border rounded-xl shadow-2xl p-6 animate-in fade-in zoom-in-95 duration-200">
                                <SchedulePublish
                                    onCancel={() => setShowSchedule(false)}
                                    onPublishNow={() => {
                                        onSave?.(content);
                                        setShowSchedule(false);
                                    }}
                                    onSchedule={(schedule) => {
                                        console.log('Scheduled:', schedule);
                                        setShowSchedule(false);
                                    }}
                                />
                            </div>
                        </div>
                    )}

                    {/* TextArea */}
                    <div className="flex-1 p-8 overflow-auto scroll-smooth">
                        <textarea
                            ref={editorRef}
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                            onSelect={handleSelect}
                            placeholder="Start writing your content..."
                            className={cn(
                                'w-full h-full resize-none bg-transparent',
                                'text-base lg:text-lg leading-relaxed',
                                'placeholder:text-muted-foreground/30',
                                'focus:outline-none',
                                'font-sans'
                            )}
                            style={{
                                maxWidth: '800px',
                                margin: '0 auto',
                                minHeight: '400px',
                                letterSpacing: '-0.01em',
                                lineHeight: '1.8',
                            }}
                        />
                    </div>
                </div>

                {/* Intelligence Side-Rail (Always Visible) */}
                <div className="w-14 border-l border-[#E5E6E3] flex flex-col items-center py-4 gap-4 bg-white">
                    <RailButton
                        icon={Clock}
                        active={activePanel === 'history'}
                        onClick={() => togglePanel('history')}
                        label="History"
                    />
                    <RailButton
                        icon={TrendingUp}
                        active={activePanel === 'predictions'}
                        onClick={() => togglePanel('predictions')}
                        label="Predict"
                    />
                    <RailButton
                        icon={Sparkles}
                        active={activePanel === 'hook'}
                        onClick={() => togglePanel('hook')}
                        label="Hook"
                    />
                    <RailButton
                        icon={Mic}
                        active={activePanel === 'brand'}
                        onClick={() => togglePanel('brand')}
                        label="Confident"
                    />
                    {currentAsset && (
                        <RailButton
                            icon={LinkIcon}
                            active={activePanel === 'chain'}
                            onClick={() => togglePanel('chain')}
                            label="Chain"
                        />
                    )}
                    <div className="flex-1" />
                    <RailButton
                        icon={Wand2}
                        active={activePanel === 'ai'}
                        onClick={() => togglePanel('ai')}
                        label="AI Assist"
                        primary
                    />
                </div>

                {/* Contextual Panel (Expands when button clicked) */}
                <div
                    className={cn(
                        'border-l border-[#E5E6E3] bg-white transition-all duration-300 ease-in-out overflow-hidden',
                        activePanel ? 'w-80' : 'w-0 border-0'
                    )}
                >
                    <div className="w-80 h-full flex flex-col">
                        {/* Panel Header */}
                        <div className="p-4 border-b border-border/40 flex items-center justify-between bg-muted/5">
                            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                {activePanel === 'ai' && 'AI Assist'}
                                {activePanel === 'brand' && 'Voice: Confident'}
                                {activePanel === 'predictions' && 'Performance Predictions'}
                                {activePanel === 'hook' && 'Hook Engagement'}
                                {activePanel === 'history' && 'Version History'}
                                {activePanel === 'chain' && 'Asset Chain'}
                            </span>
                            <button
                                onClick={() => setActivePanel(null)}
                                className="h-6 w-6 rounded-full flex items-center justify-center hover:bg-muted transition-colors"
                            >
                                <X className="h-3 w-3" />
                            </button>
                        </div>

                        {/* Panel Content */}
                        <div className="flex-1 overflow-auto p-4">
                            {/* Asset Chain Panel */}
                            {activePanel === 'chain' && currentAsset && (
                                <AssetChainPanel
                                    currentAsset={currentAsset}
                                    allAssets={allAssets}
                                />
                            )}

                            {/* History Panel */}
                            {activePanel === 'history' && (
                                <VersionHistory
                                    versions={[
                                        { id: 'v1', timestamp: new Date(Date.now() - 3600000), content: initialContent, author: 'You' },
                                        { id: 'v2', timestamp: new Date(Date.now() - 1800000), content: content + ' (Draft)', author: 'You' }
                                    ]}
                                    currentContent={content}
                                    onRestore={(v) => {
                                        setContent(v.content);
                                        setActivePanel(null);
                                    }}
                                />
                            )}

                            {/* AI Panel */}
                            {activePanel === 'ai' && (
                                <>
                                    {selectedText ? (
                                        <div className="space-y-4">
                                            <div className="p-3 rounded-lg bg-muted text-sm italic text-muted-foreground border-l-2 border-primary/20">
                                                "{selectedText}"
                                            </div>

                                            <div className="grid grid-cols-1 gap-2">
                                                {AI_ACTIONS.map(action => (
                                                    <button
                                                        key={action.id}
                                                        onClick={() => handleAIAction(action.id)}
                                                        disabled={isProcessing}
                                                        className={cn(
                                                            'w-full flex items-center gap-3 p-3 rounded-xl text-left border border-transparent',
                                                            'hover:border-border hover:bg-muted transition-all',
                                                            'disabled:opacity-50'
                                                        )}
                                                    >
                                                        <div className="h-8 w-8 rounded-lg bg-background flex items-center justify-center border border-border/40 shadow-sm">
                                                            <action.icon className="h-4 w-4 text-primary" />
                                                        </div>
                                                        <div>
                                                            <p className="text-sm font-medium">{action.label}</p>
                                                            <p className="text-[10px] text-muted-foreground uppercase">{action.description}</p>
                                                        </div>
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="text-center py-12 px-6">
                                            <div className="w-12 h-12 bg-muted/30 rounded-full flex items-center justify-center mx-auto mb-4">
                                                <Sparkles className="h-6 w-6 text-muted-foreground/50" />
                                            </div>
                                            <p className="text-sm font-medium mb-1">Select text to surgicalize</p>
                                            <p className="text-xs text-muted-foreground">Choose any section to improve, shorten, or adjust tone.</p>
                                        </div>
                                    )}
                                </>
                            )}

                            {/* Brand Voice Panel */}
                            {activePanel === 'brand' && (
                                <BrandVoicePanel isCollapsed={false} />
                            )}

                            {/* Predictions Panel */}
                            {activePanel === 'predictions' && (
                                <PredictionPanel content={content} />
                            )}

                            {/* Hook Score Panel */}
                            {activePanel === 'hook' && (
                                <HookScore text={firstLine} />
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function ToolbarButton({
    icon: Icon,
    label,
    active,
    onClick
}: {
    icon: React.ComponentType<{ className?: string }>;
    label: string;
    active?: boolean;
    onClick?: () => void;
}) {
    return (
        <button
            onClick={onClick}
            title={label}
            className={cn(
                'h-8 w-8 rounded-md flex items-center justify-center transition-all',
                active
                    ? 'bg-muted text-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted'
            )}
        >
            <Icon className="h-4 w-4" />
        </button>
    );
}

function RailButton({
    icon: Icon,
    label,
    active,
    onClick,
    primary
}: {
    icon: React.ComponentType<{ className?: string }>;
    label: string;
    active?: boolean;
    onClick?: () => void;
    primary?: boolean;
}) {
    return (
        <button
            onClick={onClick}
            title={label}
            className={cn(
                'group relative h-10 w-10 rounded-xl flex items-center justify-center transition-all duration-200',
                active
                    ? primary ? 'bg-foreground text-background shadow-lg shadow-foreground/10' : 'bg-background text-foreground shadow-sm ring-1 ring-border'
                    : primary ? 'text-muted-foreground hover:text-foreground hover:bg-muted' : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
            )}
        >
            <Icon className={cn('h-5 w-5', active && 'animate-in zoom-in-75 duration-300')} />
            {!active && (
                <div className="absolute left-full ml-2 px-2 py-1 rounded bg-foreground text-background text-[10px] font-medium opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50">
                    {label}
                </div>
            )}
        </button>
    );
}
