'use client';

import React, { useState } from 'react';
import { Alert } from '../types';
import { AlertCard } from './AlertCard';

interface AlertFeedProps {
    alerts: Alert[];
    onDismiss?: (id: string) => void;
    onCreateMove?: (alert: Alert) => void;
}

type FilterOption = 'all' | 'high' | 'new';

export function AlertFeed({ alerts, onDismiss, onCreateMove }: AlertFeedProps) {
    const [filter, setFilter] = useState<FilterOption>('all');

    const filteredAlerts = alerts.filter((alert) => {
        if (filter === 'high') return alert.impact === 'high';
        if (filter === 'new') return alert.status === 'new';
        return true;
    });

    // Group by date
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const groupedAlerts = {
        today: filteredAlerts.filter(a => new Date(a.createdAt) >= today),
        yesterday: filteredAlerts.filter(a => {
            const d = new Date(a.createdAt);
            return d >= yesterday && d < today;
        }),
        earlier: filteredAlerts.filter(a => new Date(a.createdAt) < yesterday),
    };

    // Empty State
    if (filteredAlerts.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-24 text-center">
                <div className="w-16 h-16 rounded-2xl bg-[#F8F9F7] border border-[#E5E6E3] flex items-center justify-center mb-6">
                    <div className="w-3 h-3 rounded-full bg-[#9D9F9F]" />
                </div>
                <h3 className="font-serif text-2xl text-[#2D3538] mb-2">No alerts yet</h3>
                <p className="text-[15px] text-[#5B5F61] max-w-sm leading-relaxed">
                    Create a watchlist and run a recon to start receiving competitive intelligence.
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Filter Strip — Minimal, Monochrome */}
            <div className="flex items-center gap-6 pb-4 border-b border-[#E5E6E3]">
                {(['all', 'high', 'new'] as FilterOption[]).map((f) => (
                    <button
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`text-[13px] font-medium transition-colors ${filter === f
                                ? 'text-[#2D3538]'
                                : 'text-[#9D9F9F] hover:text-[#5B5F61]'
                            }`}
                    >
                        {f === 'all' && 'All'}
                        {f === 'high' && 'High Impact'}
                        {f === 'new' && 'Unread'}
                        {filter === f && (
                            <span className="ml-2 text-[11px] text-[#9D9F9F]">
                                {f === 'all' ? alerts.length : filteredAlerts.length}
                            </span>
                        )}
                    </button>
                ))}
            </div>

            {/* Alerts by Date */}
            <div className="space-y-10">
                {/* Today */}
                {groupedAlerts.today.length > 0 && (
                    <section>
                        <h4 className="text-[11px] font-semibold uppercase tracking-[0.15em] text-[#9D9F9F] mb-5">
                            Today
                        </h4>
                        <div className="space-y-4">
                            {groupedAlerts.today.map((alert) => (
                                <AlertCard
                                    key={alert.id}
                                    alert={alert}
                                    onDismiss={onDismiss}
                                    onCreateMove={onCreateMove}
                                />
                            ))}
                        </div>
                    </section>
                )}

                {/* Yesterday */}
                {groupedAlerts.yesterday.length > 0 && (
                    <section>
                        <h4 className="text-[11px] font-semibold uppercase tracking-[0.15em] text-[#9D9F9F] mb-5">
                            Yesterday
                        </h4>
                        <div className="space-y-4">
                            {groupedAlerts.yesterday.map((alert) => (
                                <AlertCard
                                    key={alert.id}
                                    alert={alert}
                                    onDismiss={onDismiss}
                                    onCreateMove={onCreateMove}
                                />
                            ))}
                        </div>
                    </section>
                )}

                {/* Earlier */}
                {groupedAlerts.earlier.length > 0 && (
                    <section>
                        <h4 className="text-[11px] font-semibold uppercase tracking-[0.15em] text-[#9D9F9F] mb-5">
                            Earlier
                        </h4>
                        <div className="space-y-4">
                            {groupedAlerts.earlier.map((alert) => (
                                <AlertCard
                                    key={alert.id}
                                    alert={alert}
                                    onDismiss={onDismiss}
                                    onCreateMove={onCreateMove}
                                />
                            ))}
                        </div>
                    </section>
                )}
            </div>
        </div>
    );
}
