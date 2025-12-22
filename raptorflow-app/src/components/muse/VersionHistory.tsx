'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Clock, ChevronRight, RotateCcw, Eye, Diff } from 'lucide-react';

interface Version {
    id: string;
    content: string;
    timestamp: Date;
    author?: string;
    label?: string;
}

interface VersionHistoryProps {
    versions: Version[];
    currentContent: string;
    onRestore?: (version: Version) => void;
    onPreview?: (version: Version) => void;
    className?: string;
}

// Generate diff between two strings (simplified)
function generateDiff(oldText: string, newText: string): { type: 'added' | 'removed' | 'unchanged'; text: string }[] {
    const oldLines = oldText.split('\n');
    const newLines = newText.split('\n');
    const diff: { type: 'added' | 'removed' | 'unchanged'; text: string }[] = [];

    // Very simplified diff - in production use a proper diff library
    const maxLen = Math.max(oldLines.length, newLines.length);
    for (let i = 0; i < maxLen; i++) {
        const oldLine = oldLines[i] || '';
        const newLine = newLines[i] || '';

        if (oldLine === newLine && oldLine) {
            diff.push({ type: 'unchanged', text: oldLine });
        } else {
            if (oldLine) {
                diff.push({ type: 'removed', text: oldLine });
            }
            if (newLine) {
                diff.push({ type: 'added', text: newLine });
            }
        }
    }

    return diff;
}

function formatTimeAgo(date: Date): string {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
}

export function VersionHistory({
    versions,
    currentContent,
    onRestore,
    onPreview,
    className,
}: VersionHistoryProps) {
    const [selectedVersion, setSelectedVersion] = useState<Version | null>(null);
    const [showDiff, setShowDiff] = useState(false);

    const diff = selectedVersion
        ? generateDiff(selectedVersion.content, currentContent)
        : [];

    return (
        <div className={cn('flex flex-col h-full', className)}>
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-border/40">
                <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Version History</span>
                </div>
                <span className="text-xs text-muted-foreground">
                    {versions.length} version{versions.length !== 1 ? 's' : ''}
                </span>
            </div>

            {/* Version list */}
            <div className="flex-1 overflow-auto">
                {versions.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center p-4">
                        <Clock className="h-8 w-8 text-muted-foreground/30 mb-2" />
                        <p className="text-sm text-muted-foreground">No versions yet</p>
                        <p className="text-xs text-muted-foreground/60">
                            Versions are saved automatically as you edit
                        </p>
                    </div>
                ) : (
                    <div className="divide-y divide-border/40">
                        {versions.map((version, index) => (
                            <button
                                key={version.id}
                                onClick={() => setSelectedVersion(
                                    selectedVersion?.id === version.id ? null : version
                                )}
                                className={cn(
                                    'w-full flex items-center gap-3 p-4 text-left',
                                    'hover:bg-muted/30 transition-colors',
                                    selectedVersion?.id === version.id && 'bg-muted/50'
                                )}
                            >
                                {/* Timeline dot */}
                                <div className="relative flex flex-col items-center">
                                    <div className={cn(
                                        'w-2.5 h-2.5 rounded-full',
                                        index === 0 ? 'bg-foreground' : 'bg-muted-foreground/40'
                                    )} />
                                    {index < versions.length - 1 && (
                                        <div className="w-px h-8 bg-border/60 absolute top-3" />
                                    )}
                                </div>

                                {/* Content */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                        <span className="text-sm font-medium">
                                            {version.label || `Version ${versions.length - index}`}
                                        </span>
                                        {index === 0 && (
                                            <span className="px-1.5 py-0.5 rounded text-[10px] bg-foreground/10 text-foreground">
                                                Latest
                                            </span>
                                        )}
                                    </div>
                                    <div className="flex items-center gap-2 mt-0.5">
                                        <span className="text-xs text-muted-foreground">
                                            {formatTimeAgo(version.timestamp)}
                                        </span>
                                        {version.author && (
                                            <>
                                                <span className="text-muted-foreground/40">·</span>
                                                <span className="text-xs text-muted-foreground">
                                                    {version.author}
                                                </span>
                                            </>
                                        )}
                                    </div>
                                </div>

                                <ChevronRight className={cn(
                                    'h-4 w-4 text-muted-foreground transition-transform',
                                    selectedVersion?.id === version.id && 'rotate-90'
                                )} />
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {/* Selected version details */}
            {selectedVersion && (
                <div className="border-t border-border/40 bg-muted/10">
                    {/* Actions */}
                    <div className="flex items-center gap-2 p-3 border-b border-border/40">
                        <button
                            onClick={() => setShowDiff(!showDiff)}
                            className={cn(
                                'flex items-center gap-1.5 px-3 py-1.5 rounded-lg',
                                'text-xs font-medium transition-colors',
                                showDiff
                                    ? 'bg-foreground text-background'
                                    : 'border border-border/60 hover:bg-muted/30'
                            )}
                        >
                            <Diff className="h-3 w-3" />
                            View Diff
                        </button>
                        <button
                            onClick={() => onPreview?.(selectedVersion)}
                            className={cn(
                                'flex items-center gap-1.5 px-3 py-1.5 rounded-lg',
                                'border border-border/60 text-xs',
                                'hover:bg-muted/30 transition-colors'
                            )}
                        >
                            <Eye className="h-3 w-3" />
                            Preview
                        </button>
                        <button
                            onClick={() => onRestore?.(selectedVersion)}
                            className={cn(
                                'flex items-center gap-1.5 px-3 py-1.5 rounded-lg',
                                'border border-amber-500/50 text-amber-600 text-xs',
                                'hover:bg-amber-500/10 transition-colors'
                            )}
                        >
                            <RotateCcw className="h-3 w-3" />
                            Restore
                        </button>
                    </div>

                    {/* Diff view */}
                    {showDiff && (
                        <div className="max-h-48 overflow-auto p-3 font-mono text-xs">
                            {diff.map((line, i) => (
                                <div
                                    key={i}
                                    className={cn(
                                        'py-0.5 px-2 -mx-2',
                                        line.type === 'added' && 'bg-green-500/10 text-green-600',
                                        line.type === 'removed' && 'bg-red-500/10 text-red-600 line-through',
                                        line.type === 'unchanged' && 'text-muted-foreground'
                                    )}
                                >
                                    <span className="opacity-50 mr-2">
                                        {line.type === 'added' && '+'}
                                        {line.type === 'removed' && '-'}
                                        {line.type === 'unchanged' && ' '}
                                    </span>
                                    {line.text || '(empty line)'}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
