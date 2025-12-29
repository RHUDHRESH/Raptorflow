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
function generateDiff(
  oldText: string,
  newText: string
): { type: 'added' | 'removed' | 'unchanged'; text: string }[] {
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

import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { ButtonGroup } from '@/components/ui/button-group';
import { Separator } from '@/components/ui/separator';

// ... existing interfaces ...

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
      <ScrollArea className="flex-1">
        {versions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-center p-4">
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
                onClick={() =>
                  setSelectedVersion(
                    selectedVersion?.id === version.id ? null : version
                  )
                }
                className={cn(
                  'w-full flex items-center gap-3 p-4 text-left group',
                  'hover:bg-muted/30 transition-colors',
                  selectedVersion?.id === version.id && 'bg-muted/50'
                )}
              >
                {/* Timeline dot */}
                <div className="relative flex flex-col items-center self-stretch">
                  <div
                    className={cn(
                      'w-2.5 h-2.5 rounded-full z-10',
                      index === 0 ? 'bg-primary' : 'bg-muted-foreground/40'
                    )}
                  />
                  {index < versions.length - 1 && (
                    <div className="w-px h-full bg-border/60 absolute top-2.5" />
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">
                        {version.label || `Version ${versions.length - index}`}
                      </span>
                      {index === 0 && (
                        <Badge
                          variant="secondary"
                          className="text-[10px] h-5 px-1.5"
                        >
                          Latest
                        </Badge>
                      )}
                    </div>
                    <span className="text-xs text-muted-foreground tabular-nums">
                      {formatTimeAgo(version.timestamp)}
                    </span>
                  </div>

                  {version.author && (
                    <div className="flex items-center gap-1.5">
                      <Avatar className="h-4 w-4">
                        <AvatarImage
                          src={`https://avatar.vercel.sh/${version.author}`}
                        />
                        <AvatarFallback className="text-[9px]">
                          {version.author[0]}
                        </AvatarFallback>
                      </Avatar>
                      <span className="text-xs text-muted-foreground">
                        {version.author}
                      </span>
                    </div>
                  )}
                </div>

                <ChevronRight
                  className={cn(
                    'h-4 w-4 text-muted-foreground/50 transition-transform group-hover:text-muted-foreground',
                    selectedVersion?.id === version.id && 'rotate-90'
                  )}
                />
              </button>
            ))}
          </div>
        )}
      </ScrollArea>

      {/* Selected version details */}
      {selectedVersion && (
        <div className="border-t border-border/40 bg-muted/10">
          {/* Actions */}
          <div className="flex items-center justify-between p-3 border-b border-border/40">
            <div className="flex items-center gap-2">
              <ButtonGroup>
                <button
                  onClick={() => setShowDiff(!showDiff)}
                  className={cn(
                    'px-3 py-1.5 text-xs font-medium transition-colors flex items-center gap-1.5',
                    showDiff
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-muted'
                  )}
                >
                  <Diff className="h-3 w-3" />
                  {showDiff ? 'Hide Diff' : 'Show Diff'}
                </button>
                <button
                  onClick={() => onPreview?.(selectedVersion)}
                  className="px-3 py-1.5 text-xs font-medium hover:bg-muted transition-colors flex items-center gap-1.5"
                >
                  <Eye className="h-3 w-3" />
                  Preview
                </button>
              </ButtonGroup>
            </div>

            <button
              onClick={() => onRestore?.(selectedVersion)}
              className={cn(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-md',
                'bg-amber-500/10 text-amber-600 text-xs font-medium',
                'hover:bg-amber-500/20 transition-colors border border-amber-500/20'
              )}
            >
              <RotateCcw className="h-3 w-3" />
              Restore
            </button>
          </div>

          {/* Diff view */}
          {showDiff && (
            <ScrollArea className="h-48 w-full border-b">
              <div className="p-3 font-mono text-xs">
                {diff.map((line, i) => (
                  <div
                    key={i}
                    className={cn(
                      'py-0.5 px-2 -mx-2 flex',
                      line.type === 'added' &&
                        'bg-green-500/10 text-green-700 dark:text-green-400',
                      line.type === 'removed' &&
                        'bg-red-500/10 text-red-700 dark:text-red-400 line-through decoration-red-900/30',
                      line.type === 'unchanged' && 'text-muted-foreground'
                    )}
                  >
                    <span className="opacity-50 w-4 inline-block select-none shrink-0">
                      {line.type === 'added' && '+'}
                      {line.type === 'removed' && '-'}
                    </span>
                    <span className="whitespace-pre-wrap break-all">
                      {line.text || ' '}
                    </span>
                  </div>
                ))}
              </div>
            </ScrollArea>
          )}
        </div>
      )}
    </div>
  );
}
