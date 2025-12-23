'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, Cpu, Code } from 'lucide-react';

interface TelemetryTrace {
    id: string;
    agent_id: string;
    action: string;
    latency: number;
    timestamp: string;
    status: 'success' | 'failed';
}

const MOCK_TRACES: TelemetryTrace[] = [
    { id: '1', agent_id: 'MoveGenerator', action: 'generate_weekly_moves', latency: 1240, timestamp: '2 mins ago', status: 'success' },
    { id: '2', agent_id: 'TavilySearch', action: 'deep_research', latency: 3400, timestamp: '5 mins ago', status: 'success' },
    { id: '3', agent_id: 'StrategicAnalyst', action: 'pivot_recommendation', latency: 890, timestamp: '12 mins ago', status: 'success' },
    { id: '4', agent_id: 'SafetyGuard', action: 'content_validation', latency: 120, timestamp: '15 mins ago', status: 'success' },
];

export function TelemetryFeed() {
    return (
        <Card className="border border-border bg-card/50 backdrop-blur-sm rounded-2xl shadow-none">
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg font-semibold font-sans tracking-tight">
                        Live Telemetry
                    </CardTitle>
                    <Badge variant="outline" className="font-mono text-[10px] uppercase tracking-tighter bg-accent/10 text-accent border-accent/20">
                        Live stream
                    </Badge>
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {MOCK_TRACES.map((trace) => (
                        <div key={trace.id} className="flex items-center justify-between py-2 border-b border-border last:border-0 group hover:bg-accent/5 transition-colors rounded-lg px-2 -mx-2">
                            <div className="flex items-center gap-3">
                                <div className="h-8 w-8 rounded bg-muted flex items-center justify-center">
                                    <Cpu className="h-4 w-4 text-muted-foreground" />
                                </div>
                                <div>
                                    <div className="text-sm font-medium font-sans flex items-center gap-2">
                                        {trace.agent_id}
                                        <span className="text-xs text-muted-foreground font-normal">→ {trace.action}</span>
                                    </div>
                                    <div className="flex items-center gap-3 mt-1">
                                        <span className="flex items-center gap-1 text-[10px] text-muted-foreground font-mono">
                                            <Clock className="h-3 w-3" /> {trace.timestamp}
                                        </span>
                                        <span className="flex items-center gap-1 text-[10px] text-muted-foreground font-mono">
                                            <Code className="h-3 w-3" /> {trace.latency}ms
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div className={`h-1.5 w-1.5 rounded-full ${trace.status === 'success' ? 'bg-green-500' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]'}`} />
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
