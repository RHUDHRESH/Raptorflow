'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Calendar, Clock, Send, X, Bell, Check } from 'lucide-react';

interface ScheduledPublish {
    date: Date;
    time: string;
    platform?: string;
    notifyBefore?: number; // minutes
}

interface SchedulePublishProps {
    onSchedule?: (schedule: ScheduledPublish) => void;
    onPublishNow?: () => void;
    onCancel?: () => void;
    className?: string;
}

const PLATFORMS = [
    { id: 'linkedin', label: 'LinkedIn', icon: '💼' },
    { id: 'twitter', label: 'Twitter/X', icon: '🐦' },
    { id: 'email', label: 'Email', icon: '📧' },
    { id: 'instagram', label: 'Instagram', icon: '📸' },
];

const QUICK_TIMES = [
    { label: 'Tomorrow 9am', offset: 1, hour: 9 },
    { label: 'Tomorrow 2pm', offset: 1, hour: 14 },
    { label: 'Next Monday', offset: 7, hour: 9 },
    { label: 'Next Week', offset: 7, hour: 9 },
];

export function SchedulePublish({
    onSchedule,
    onPublishNow,
    onCancel,
    className,
}: SchedulePublishProps) {
    const [showCustom, setShowCustom] = useState(false);
    const [customDate, setCustomDate] = useState('');
    const [customTime, setCustomTime] = useState('09:00');
    const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null);
    const [notifyBefore, setNotifyBefore] = useState(30);
    const [scheduled, setScheduled] = useState(false);

    const handleQuickSchedule = (quickTime: typeof QUICK_TIMES[0]) => {
        const date = new Date();
        date.setDate(date.getDate() + quickTime.offset);
        date.setHours(quickTime.hour, 0, 0, 0);

        onSchedule?.({
            date,
            time: `${quickTime.hour}:00`,
            platform: selectedPlatform || undefined,
            notifyBefore,
        });
        setScheduled(true);
        setTimeout(() => setScheduled(false), 2000);
    };

    const handleCustomSchedule = () => {
        if (!customDate) return;

        const [year, month, day] = customDate.split('-').map(Number);
        const [hour, minute] = customTime.split(':').map(Number);
        const date = new Date(year, month - 1, day, hour, minute);

        onSchedule?.({
            date,
            time: customTime,
            platform: selectedPlatform || undefined,
            notifyBefore,
        });
        setScheduled(true);
        setTimeout(() => setScheduled(false), 2000);
    };

    if (scheduled) {
        return (
            <div className={cn('flex items-center justify-center gap-2 p-6', className)}>
                <Check className="h-5 w-5 text-green-500" />
                <span className="text-sm font-medium text-green-600">Scheduled!</span>
            </div>
        );
    }

    return (
        <div className={cn('space-y-5', className)}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Schedule Publish</span>
                </div>
                {onCancel && (
                    <button onClick={onCancel} className="p-1 hover:bg-muted rounded-md">
                        <X className="h-4 w-4" />
                    </button>
                )}
            </div>

            {/* Quick schedule buttons */}
            <div className="space-y-2">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                    Quick Schedule
                </p>
                <div className="grid grid-cols-2 gap-2">
                    {QUICK_TIMES.map(time => (
                        <button
                            key={time.label}
                            onClick={() => handleQuickSchedule(time)}
                            className={cn(
                                'flex items-center gap-2 p-3 rounded-lg',
                                'border border-border/60 bg-card',
                                'text-sm text-left',
                                'hover:border-foreground/20 transition-colors'
                            )}
                        >
                            <Clock className="h-4 w-4 text-muted-foreground shrink-0" />
                            {time.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Custom date/time */}
            <div className="space-y-3">
                <button
                    onClick={() => setShowCustom(!showCustom)}
                    className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                    {showCustom ? '− Hide custom' : '+ Custom date & time'}
                </button>

                {showCustom && (
                    <div className="space-y-3 p-3 rounded-lg bg-muted/30">
                        <div className="grid grid-cols-2 gap-3">
                            <div>
                                <label className="text-xs text-muted-foreground block mb-1">Date</label>
                                <input
                                    type="date"
                                    value={customDate}
                                    onChange={(e) => setCustomDate(e.target.value)}
                                    min={new Date().toISOString().split('T')[0]}
                                    className={cn(
                                        'w-full px-3 py-2 rounded-lg',
                                        'border border-border/60 bg-card',
                                        'text-sm outline-none focus:border-foreground/30'
                                    )}
                                />
                            </div>
                            <div>
                                <label className="text-xs text-muted-foreground block mb-1">Time</label>
                                <input
                                    type="time"
                                    value={customTime}
                                    onChange={(e) => setCustomTime(e.target.value)}
                                    className={cn(
                                        'w-full px-3 py-2 rounded-lg',
                                        'border border-border/60 bg-card',
                                        'text-sm outline-none focus:border-foreground/30'
                                    )}
                                />
                            </div>
                        </div>

                        <button
                            onClick={handleCustomSchedule}
                            disabled={!customDate}
                            className={cn(
                                'w-full h-9 rounded-lg',
                                'bg-foreground text-background',
                                'text-sm font-medium',
                                'hover:opacity-90 transition-opacity',
                                'disabled:opacity-40 disabled:cursor-not-allowed'
                            )}
                        >
                            Schedule for {customDate || 'selected date'}
                        </button>
                    </div>
                )}
            </div>

            {/* Platform selection */}
            <div className="space-y-2">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                    Target Platform (optional)
                </p>
                <div className="flex flex-wrap gap-2">
                    {PLATFORMS.map(platform => (
                        <button
                            key={platform.id}
                            onClick={() => setSelectedPlatform(
                                selectedPlatform === platform.id ? null : platform.id
                            )}
                            className={cn(
                                'flex items-center gap-1.5 px-3 py-1.5 rounded-full',
                                'text-xs transition-colors',
                                selectedPlatform === platform.id
                                    ? 'bg-foreground text-background'
                                    : 'bg-muted hover:bg-muted/80'
                            )}
                        >
                            <span>{platform.icon}</span>
                            {platform.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Notification setting */}
            <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                <div className="flex items-center gap-2">
                    <Bell className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">Remind me before</span>
                </div>
                <select
                    value={notifyBefore}
                    onChange={(e) => setNotifyBefore(Number(e.target.value))}
                    className={cn(
                        'px-2 py-1 rounded-md',
                        'bg-card border border-border/60',
                        'text-xs outline-none'
                    )}
                >
                    <option value={15}>15 min</option>
                    <option value={30}>30 min</option>
                    <option value={60}>1 hour</option>
                    <option value={1440}>1 day</option>
                </select>
            </div>

            {/* Divider */}
            <div className="flex items-center gap-3">
                <div className="flex-1 h-px bg-border/40" />
                <span className="text-xs text-muted-foreground">or</span>
                <div className="flex-1 h-px bg-border/40" />
            </div>

            {/* Publish now */}
            <button
                onClick={onPublishNow}
                className={cn(
                    'w-full flex items-center justify-center gap-2 h-10 rounded-lg',
                    'border border-foreground/20',
                    'text-sm font-medium',
                    'hover:bg-muted/30 transition-colors'
                )}
            >
                <Send className="h-4 w-4" />
                Publish Now
            </button>
        </div>
    );
}
