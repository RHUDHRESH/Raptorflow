'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { ShieldAlert, AlertTriangle, Info, Clock, Activity } from 'lucide-react';

export interface SystemAlert {
    id: string;
    severity: 'critical' | 'warning' | 'info';
    message: string;
    timestamp: string;
    component: string;
}

interface AlertCenterProps {
    alerts: SystemAlert[];
    className?: string;
}

export function AlertCenter({ alerts, className }: AlertCenterProps) {
    const getSeverityStyles = (severity: SystemAlert['severity']) => {
        switch (severity) {
            case 'critical':
                return "bg-red-50 text-red-700 border-red-100";
            case 'warning':
                return "bg-amber-50 text-amber-700 border-amber-100";
            default:
                return "bg-blue-50 text-blue-700 border-blue-100";
        }
    };

    const getIcon = (severity: SystemAlert['severity']) => {
        switch (severity) {
            case 'critical': return <ShieldAlert className="h-4 w-4" />;
            case 'warning': return <AlertTriangle className="h-4 w-4" />;
            default: return <Info className="h-4 w-4" />;
        }
    };

    const formatTime = (dateStr: string) => {
        return new Date(dateStr).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
    };

    return (
        <div className={cn(
            "rounded-[24px] bg-card border border-border flex flex-col h-full overflow-hidden transition-all duration-300 shadow-sm",
            className
        )}>
            {/* Header */}
            <div className="p-6 border-b border-border/50 flex items-center justify-between bg-muted/5">
                <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-primary/5 flex items-center justify-center">
                        <Activity className="h-4 w-4 text-primary/60" />
                    </div>
                    <div>
                        <h3 className="text-[11px] font-bold uppercase tracking-[0.2em] text-foreground font-sans">
                            System Alerts
                        </h3>
                        <span className="text-[10px] text-muted-foreground uppercase tracking-wider">
                            Real-time Pulse
                        </span>
                    </div>
                </div>
                <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" title="Live Monitoring" />
            </div>

            {/* Alert List */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
                <AnimatePresence initial={false}>
                    {alerts.map((alert, idx) => (
                        <motion.div
                            key={alert.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            transition={{ duration: 0.4, delay: idx * 0.05 }}
                            className={cn(
                                "p-4 rounded-xl border flex flex-col gap-3 transition-all group",
                                getSeverityStyles(alert.severity)
                            )}
                        >
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex items-center gap-2">
                                    {getIcon(alert.severity)}
                                    <span className="text-[10px] font-mono uppercase tracking-widest font-bold opacity-80">
                                        {alert.severity}
                                    </span>
                                </div>
                                <span className="text-[9px] font-mono opacity-60">
                                    {formatTime(alert.timestamp)}
                                </span>
                            </div>

                            <p className="text-xs font-sans font-medium leading-relaxed">
                                {alert.message}
                            </p>

                            <div className="flex items-center gap-2 mt-1">
                                <div className="h-1.5 w-1.5 rounded-full bg-current opacity-20" />
                                <span className="text-[9px] uppercase tracking-tighter font-bold opacity-70">
                                    Source: {alert.component}
                                </span>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {alerts.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center py-12 text-center">
                        <div className="h-12 w-12 rounded-full bg-muted/20 flex items-center justify-center mb-4">
                            <Clock className="h-6 w-6 text-muted-foreground/30" />
                        </div>
                        <p className="text-xs text-muted-foreground font-sans">
                            No critical alerts detected.<br/>
                            System is within nominal parameters.
                        </p>
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="p-4 bg-muted/5 border-t border-border/50 text-center">
                <button className="text-[9px] uppercase tracking-widest text-muted-foreground hover:text-foreground transition-colors font-bold">
                    View Full Audit Log
                </button>
            </div>
        </div>
    );
}
