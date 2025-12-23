'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Activity, TrendingUp, Zap, Target } from 'lucide-react';

interface BoardroomStats {
    totalMoves: number;
    momentumScore: number;
    activeCampaigns: number;
    averageRoi: string;
}

const DEFAULT_STATS: BoardroomStats = {
    totalMoves: 124,
    momentumScore: 88.4,
    activeCampaigns: 3,
    averageRoi: '+340%'
};

export function BoardroomView({ stats = DEFAULT_STATS }: { stats?: BoardroomStats }) {
    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
            <Card className="border border-border bg-card/50 backdrop-blur-sm rounded-2xl shadow-none">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium font-sans text-muted-foreground uppercase tracking-wider">
                        Momentum
                    </CardTitle>
                    <Zap className="h-4 w-4 text-accent" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold font-sans">{stats.momentumScore}</div>
                    <p className="text-xs text-muted-foreground font-sans mt-1">
                        +2.5% from last week
                    </p>
                </CardContent>
            </Card>

            <Card className="border border-border bg-card/50 backdrop-blur-sm rounded-2xl shadow-none">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium font-sans text-muted-foreground uppercase tracking-wider">
                        Avg. ROI
                    </CardTitle>
                    <TrendingUp className="h-4 w-4 text-green-500" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold font-sans">{stats.averageRoi}</div>
                    <p className="text-xs text-muted-foreground font-sans mt-1">
                        Linear attribution model
                    </p>
                </CardContent>
            </Card>

            <Card className="border border-border bg-card/50 backdrop-blur-sm rounded-2xl shadow-none">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium font-sans text-muted-foreground uppercase tracking-wider">
                        Active Campaigns
                    </CardTitle>
                    <Target className="h-4 w-4 text-blue-500" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold font-sans">{stats.activeCampaigns}</div>
                    <p className="text-xs text-muted-foreground font-sans mt-1">
                        Across 2 segments
                    </p>
                </CardContent>
            </Card>

            <Card className="border border-border bg-card/50 backdrop-blur-sm rounded-2xl shadow-none">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium font-sans text-muted-foreground uppercase tracking-wider">
                        Total Moves
                    </CardTitle>
                    <Activity className="h-4 w-4 text-purple-500" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold font-sans">{stats.totalMoves}</div>
                    <p className="text-xs text-muted-foreground font-sans mt-1">
                        Executed this month
                    </p>
                </CardContent>
            </Card>
        </div>
    );
}
