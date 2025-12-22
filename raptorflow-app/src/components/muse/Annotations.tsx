'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { MessageCircle, X, Send, User } from 'lucide-react';

interface Annotation {
    id: string;
    startIndex: number;
    endIndex: number;
    text: string;
    author: string;
    timestamp: Date;
    comment: string;
    resolved?: boolean;
}

interface AnnotationMarkerProps {
    annotation: Annotation;
    onResolve?: (id: string) => void;
    onReply?: (id: string, reply: string) => void;
    className?: string;
}

export function AnnotationMarker({
    annotation,
    onResolve,
    onReply,
    className
}: AnnotationMarkerProps) {
    const [showPopover, setShowPopover] = useState(false);
    const [replyText, setReplyText] = useState('');

    const handleReply = () => {
        if (replyText.trim()) {
            onReply?.(annotation.id, replyText);
            setReplyText('');
        }
    };

    return (
        <span className="relative inline">
            {/* Highlighted text */}
            <span
                className={cn(
                    'bg-amber-500/20 border-b-2 border-amber-500 cursor-pointer',
                    'hover:bg-amber-500/30 transition-colors',
                    annotation.resolved && 'bg-green-500/10 border-green-500/50',
                    className
                )}
                onClick={() => setShowPopover(!showPopover)}
            >
                {annotation.text}
            </span>

            {/* Annotation popover */}
            {showPopover && (
                <div className={cn(
                    'absolute z-50 top-full left-0 mt-2',
                    'w-72 rounded-xl border border-border/60 bg-card shadow-xl',
                    'overflow-hidden'
                )}>
                    {/* Header */}
                    <div className="flex items-center justify-between px-3 py-2 bg-muted/30 border-b border-border/40">
                        <div className="flex items-center gap-2">
                            <div className="h-6 w-6 rounded-full bg-foreground/10 flex items-center justify-center">
                                <User className="h-3 w-3" />
                            </div>
                            <span className="text-xs font-medium">{annotation.author}</span>
                        </div>
                        <button
                            onClick={() => setShowPopover(false)}
                            className="p-1 hover:bg-muted rounded-md transition-colors"
                        >
                            <X className="h-3 w-3" />
                        </button>
                    </div>

                    {/* Comment */}
                    <div className="p-3">
                        <p className="text-sm">{annotation.comment}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                            {annotation.timestamp.toLocaleDateString()}
                        </p>
                    </div>

                    {/* Reply input */}
                    <div className="px-3 pb-3">
                        <div className="flex items-center gap-2">
                            <input
                                type="text"
                                value={replyText}
                                onChange={(e) => setReplyText(e.target.value)}
                                placeholder="Reply..."
                                className={cn(
                                    'flex-1 px-3 py-1.5 rounded-lg',
                                    'bg-muted border-none outline-none',
                                    'text-sm placeholder:text-muted-foreground/40'
                                )}
                                onKeyDown={(e) => e.key === 'Enter' && handleReply()}
                            />
                            <button
                                onClick={handleReply}
                                disabled={!replyText.trim()}
                                className={cn(
                                    'p-1.5 rounded-lg',
                                    'bg-foreground text-background',
                                    'disabled:opacity-40'
                                )}
                            >
                                <Send className="h-3 w-3" />
                            </button>
                        </div>
                    </div>

                    {/* Resolve button */}
                    {!annotation.resolved && (
                        <div className="px-3 pb-3 pt-0">
                            <button
                                onClick={() => {
                                    onResolve?.(annotation.id);
                                    setShowPopover(false);
                                }}
                                className={cn(
                                    'w-full py-1.5 rounded-lg',
                                    'border border-green-500/50 text-green-600',
                                    'text-xs font-medium',
                                    'hover:bg-green-500/10 transition-colors'
                                )}
                            >
                                Mark as resolved
                            </button>
                        </div>
                    )}
                </div>
            )}
        </span>
    );
}

// Button to add new annotation
interface AddAnnotationButtonProps {
    onAdd?: () => void;
    hasSelection?: boolean;
    className?: string;
}

export function AddAnnotationButton({ onAdd, hasSelection, className }: AddAnnotationButtonProps) {
    return (
        <button
            onClick={onAdd}
            disabled={!hasSelection}
            className={cn(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-lg',
                'border border-border/60 text-xs',
                'hover:bg-muted/30 transition-colors',
                'disabled:opacity-40 disabled:cursor-not-allowed',
                className
            )}
        >
            <MessageCircle className="h-3.5 w-3.5" />
            Add Comment
        </button>
    );
}

// Panel showing all annotations
interface AnnotationsPanelProps {
    annotations: Annotation[];
    onJumpTo?: (annotation: Annotation) => void;
    onResolve?: (id: string) => void;
    className?: string;
}

export function AnnotationsPanel({
    annotations,
    onJumpTo,
    onResolve,
    className
}: AnnotationsPanelProps) {
    const unresolvedCount = annotations.filter(a => !a.resolved).length;

    return (
        <div className={cn('space-y-3', className)}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <MessageCircle className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Comments</span>
                </div>
                {unresolvedCount > 0 && (
                    <span className="px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-600 text-xs">
                        {unresolvedCount} open
                    </span>
                )}
            </div>

            {/* Annotations list */}
            {annotations.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                    No comments yet. Select text to add one.
                </p>
            ) : (
                <div className="space-y-2">
                    {annotations.map(annotation => (
                        <button
                            key={annotation.id}
                            onClick={() => onJumpTo?.(annotation)}
                            className={cn(
                                'w-full p-3 rounded-lg text-left',
                                'border border-border/60 bg-card',
                                'hover:border-foreground/20 transition-colors',
                                annotation.resolved && 'opacity-50'
                            )}
                        >
                            <div className="flex items-start justify-between gap-2">
                                <div className="flex-1 min-w-0">
                                    <p className="text-xs text-muted-foreground truncate">
                                        "{annotation.text}"
                                    </p>
                                    <p className="text-sm mt-1">{annotation.comment}</p>
                                    <p className="text-xs text-muted-foreground mt-1">
                                        {annotation.author} · {annotation.timestamp.toLocaleDateString()}
                                    </p>
                                </div>
                                {!annotation.resolved && (
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onResolve?.(annotation.id);
                                        }}
                                        className="p-1 hover:bg-green-500/10 rounded-md text-green-600"
                                    >
                                        ✓
                                    </button>
                                )}
                            </div>
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}
