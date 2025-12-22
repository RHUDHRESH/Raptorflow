'use client';

import React from 'react';
import {
    Clock,
    BarChart2,
    RefreshCcw,
    Rocket,
    CheckCircle2,
    ChevronRight,
    MoreHorizontal,
    Copy,
    Trash2,
    Eye,
    ArrowUp,
    ArrowDown,
    Pencil
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Experiment } from '@/lib/blackbox-types';
import { Button } from '@/components/ui/button';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface ExperimentCardProps {
    experiment: Experiment;
    index?: number;
    totalCount?: number;
    onLaunch?: (id: string) => void;
    onSwap?: (id: string) => void;
    onCheckin?: (id: string) => void;
    onView?: (id: string) => void;
    onDelete?: (id: string) => void;
    onDuplicate?: (id: string) => void;
    onMove?: (id: string, direction: 'up' | 'down') => void;
    onEdit?: (id: string) => void;
}

export function ExperimentCard({
    experiment,
    index = 0,
    totalCount = 0,
    onLaunch,
    onSwap,
    onCheckin,
    onView,
    onDelete,
    onDuplicate,
    onMove,
    onEdit
}: ExperimentCardProps) {
    const [isSwapping, setIsSwapping] = React.useState(false);

    const isDraft = experiment.status === 'draft';
    const isLaunched = experiment.status === 'launched';
    const isCheckedIn = experiment.status === 'checked_in';

    const handleSwap = () => {
        setIsSwapping(true);
        setTimeout(() => {
            onSwap?.(experiment.id);
            setIsSwapping(false);
        }, 400);
    };

    return (
        <div className={cn(
            "group flex items-start gap-4 p-5 rounded-xl border transition-all duration-200",
            isSwapping && "opacity-50",
            isCheckedIn
                ? "bg-zinc-50/50 border-zinc-100 dark:bg-zinc-900/30 dark:border-zinc-800/50"
                : "bg-white border-zinc-200 dark:bg-zinc-900 dark:border-zinc-800 hover:border-zinc-300 dark:hover:border-zinc-700"
        )}>
            {/* Number */}
            <div className={cn(
                "w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold font-mono shrink-0",
                isLaunched
                    ? "bg-zinc-900 text-white dark:bg-white dark:text-zinc-900"
                    : isCheckedIn
                        ? "bg-zinc-200 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400"
                        : "bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400"
            )}>
                {isLaunched ? <Rocket className="w-3.5 h-3.5" /> :
                    isCheckedIn ? <CheckCircle2 className="w-3.5 h-3.5" /> :
                        index + 1}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 truncate font-sans">
                        {experiment.title}
                    </h3>
                    <span className="text-[9px] font-medium uppercase tracking-wider text-zinc-400 shrink-0 font-sans">
                        {experiment.principle.replace('_', ' ')}
                    </span>
                </div>

                <p className="text-xs text-zinc-500 leading-relaxed line-clamp-1 mb-2 font-sans">
                    {experiment.bet}
                </p>

                <div className="flex items-center gap-3 text-[10px] text-zinc-400 font-sans">
                    <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {experiment.effort}
                    </span>
                    <span className="flex items-center gap-1">
                        <BarChart2 className="w-3 h-3" />
                        {experiment.time_to_signal}
                    </span>
                    <span className="capitalize">{experiment.channel}</span>
                </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-1.5 shrink-0">
                {isDraft && (
                    <>
                        <Button
                            onClick={() => onLaunch?.(experiment.id)}
                            size="sm"
                            className="rounded-lg bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200 h-8 px-3 text-xs font-sans"
                        >
                            Launch
                        </Button>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={handleSwap}
                            disabled={isSwapping}
                            className="rounded-lg h-8 w-8 text-zinc-400"
                            title="Swap Experiment"
                        >
                            <RefreshCcw className={cn("w-3.5 h-3.5", isSwapping && "animate-spin")} />
                        </Button>
                    </>
                )}

                {isLaunched && (
                    <Button
                        onClick={() => onCheckin?.(experiment.id)}
                        size="sm"
                        variant="outline"
                        className="rounded-lg h-8 px-3 text-xs border-zinc-900 dark:border-zinc-100 font-sans"
                    >
                        Check-in
                        <ChevronRight className="w-3 h-3 ml-1" />
                    </Button>
                )}

                {isCheckedIn && experiment.self_report && (
                    <span className="text-xs font-medium text-zinc-500 capitalize font-sans">
                        {experiment.self_report.outcome}
                    </span>
                )}

                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button
                            variant="ghost"
                            size="icon"
                            className="rounded-lg h-8 w-8 text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 dark:hover:bg-zinc-800"
                        >
                            <MoreHorizontal className="w-4 h-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-44">
                        <DropdownMenuItem onClick={() => onView?.(experiment.id)} className="font-sans text-xs">
                            <Eye className="w-3.5 h-3.5 mr-2" /> View Details
                        </DropdownMenuItem>

                        {isDraft && (
                            <DropdownMenuItem onClick={() => onEdit?.(experiment.id)} className="font-sans text-xs">
                                <Pencil className="w-3.5 h-3.5 mr-2" /> Edit Content
                            </DropdownMenuItem>
                        )}

                        {!isCheckedIn && totalCount > 1 && (
                            <>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem
                                    onClick={() => onMove?.(experiment.id, 'up')}
                                    disabled={index === 0}
                                    className="font-sans text-xs"
                                >
                                    <ArrowUp className="w-3.5 h-3.5 mr-2" /> Move Up
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                    onClick={() => onMove?.(experiment.id, 'down')}
                                    disabled={index === totalCount - 1}
                                    className="font-sans text-xs"
                                >
                                    <ArrowDown className="w-3.5 h-3.5 mr-2" /> Move Down
                                </DropdownMenuItem>
                            </>
                        )}

                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={() => onDuplicate?.(experiment.id)} className="font-sans text-xs">
                            <Copy className="w-3.5 h-3.5 mr-2" /> Duplicate
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onDelete?.(experiment.id)} className="text-red-600 focus:text-red-700 font-sans text-xs">
                            <Trash2 className="w-3.5 h-3.5 mr-2" /> Delete
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </div>
    );
}
