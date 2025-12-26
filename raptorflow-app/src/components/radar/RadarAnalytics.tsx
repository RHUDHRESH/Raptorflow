'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
    getSignalTrends, 
    getCompetitorAnalysis, 
    getMarketIntelligence, 
    getOpportunities 
} from '@/lib/radar';
import { toast } from 'sonner';
import { TrendingUp, TrendingDown, Target, AlertTriangle, Lightbulb } from 'lucide-react';

interface RadarAnalyticsProps {
    className?: string;
}

export function RadarAnalytics({ className }: RadarAnalyticsProps) {
    const [loading, setLoading] = useState(true);
    const [trends, setTrends] = useState<any>(null);
    const [competitors, setCompetitors] = useState<any>(null);
    const [intelligence, setIntelligence] = useState<any>(null);
    const [opportunities, setOpportunities] = useState<any[]>([]);

    useEffect(() => {
        loadAnalytics();
    }, []);

    const loadAnalytics = async () => {
        setLoading(true);
        try {
            const [trendsData, competitorsData, intelligenceData, opportunitiesData] = await Promise.all([
                getSignalTrends(30),
                getCompetitorAnalysis(),
                getMarketIntelligence(),
                getOpportunities()
            ]);

            setTrends(trendsData);
            setCompetitors(competitorsData);
            setIntelligence(intelligenceData);
            setOpportunities(opportunitiesData);

        } catch (error) {
            toast.error('Failed to load analytics', {
                description: error instanceof Error ? error.message : 'Unknown error'
            });
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                    <p className="text-muted-foreground">Loading analytics...</p>
                </div>
            </div>
        );
    }

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Signal Trends */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <TrendingUp className="w-5 h-5" />
                        Signal Trends (30 days)
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                            <div className="text-2xl font-bold text-primary">
                                {trends?.total_signals || 0}
                            </div>
                            <div className="text-sm text-muted-foreground">Total Signals</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">
                                {trends?.growth_rate || 0}%
                            </div>
                            <div className="text-sm text-muted-foreground">Growth Rate</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-blue-600">
                                {trends?.velocity || 0}
                            </div>
                            <div className="text-sm text-muted-foreground">Daily Velocity</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-purple-600">
                                {trends?.active_categories || 0}
                            </div>
                            <div className="text-sm text-muted-foreground">Active Categories</div>
                        </div>
                    </div>
                    
                    {/* Category Breakdown */}
                    <div className="mt-6">
                        <h4 className="font-medium mb-3">Category Breakdown</h4>
                        <div className="space-y-2">
                            {trends?.category_trends?.map((category: any, index: number) => (
                                <div key={index} className="flex items-center justify-between">
                                    <span className="capitalize font-medium">{category.category}</span>
                                    <div className="flex items-center gap-2">
                                        <span className="text-sm text-muted-foreground">{category.count} signals</span>
                                        {category.trend === 'up' ? (
                                            <TrendingUp className="w-4 h-4 text-green-500" />
                                        ) : (
                                            <TrendingDown className="w-4 h-4 text-red-500" />
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Competitor Analysis */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Target className="w-5 h-5" />
                        Competitor Analysis
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {/* Market Leaders */}
                        <div>
                            <h4 className="font-medium mb-2">Market Leaders</h4>
                            <div className="flex flex-wrap gap-2">
                                {competitors?.market_leaders?.map((leader: string, index: number) => (
                                    <Badge key={index} variant="secondary">
                                        {leader}
                                    </Badge>
                                ))}
                            </div>
                        </div>

                        {/* Emerging Threats */}
                        <div>
                            <h4 className="font-medium mb-2 flex items-center gap-2">
                                <AlertTriangle className="w-4 h-4 text-orange-500" />
                                Emerging Threats
                            </h4>
                            <div className="flex flex-wrap gap-2">
                                {competitors?.emerging_threats?.map((threat: string, index: number) => (
                                    <Badge key={index} variant="destructive">
                                        {threat}
                                    </Badge>
                                ))}
                            </div>
                        </div>

                        {/* Competitor Activity */}
                        <div>
                            <h4 className="font-medium mb-2">Recent Activity</h4>
                            <div className="space-y-2">
                                {competitors?.competitors?.slice(0, 3).map((competitor: any, index: number) => (
                                    <div key={index} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                                        <div>
                                            <div className="font-medium">{competitor.name}</div>
                                            <div className="text-sm text-muted-foreground">
                                                {competitor.signal_count} signals • {competitor.last_activity}
                                            </div>
                                        </div>
                                        <Badge variant={competitor.threat_level === 'high' ? 'destructive' : 'secondary'}>
                                            {competitor.threat_level}
                                        </Badge>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Market Intelligence */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Lightbulb className="w-5 h-5" />
                        Market Intelligence
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {/* Market Dynamics */}
                        <div>
                            <h4 className="font-medium mb-2">Market Dynamics</h4>
                            <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="font-medium">Activity Level</span>
                                    <Badge variant={intelligence?.market_dynamics?.activity_level === 'high' ? 'default' : 'secondary'}>
                                        {intelligence?.market_dynamics?.activity_level}
                                    </Badge>
                                </div>
                                <p className="text-sm text-muted-foreground">
                                    {intelligence?.market_dynamics?.summary}
                                </p>
                            </div>
                        </div>

                        {/* Predictive Insights */}
                        <div>
                            <h4 className="font-medium mb-2">Predictive Insights</h4>
                            <div className="space-y-2">
                                {intelligence?.predictive_insights?.trends?.map((insight: any, index: number) => (
                                    <div key={index} className="p-3 bg-muted/50 rounded-lg">
                                        <div className="font-medium mb-1">{insight.trend}</div>
                                        <div className="text-sm text-muted-foreground">{insight.insight}</div>
                                        <div className="mt-2">
                                            <Badge variant="outline">Confidence: {insight.confidence}%</Badge>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Strategic Opportunities */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Target className="w-5 h-5" />
                        Strategic Opportunities
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-3">
                        {opportunities?.slice(0, 5).map((opportunity: any, index: number) => (
                            <div key={index} className="p-4 border rounded-lg">
                                <div className="flex items-start justify-between mb-2">
                                    <h4 className="font-medium">{opportunity.title}</h4>
                                    <Badge variant={opportunity.priority === 'high' ? 'default' : 'secondary'}>
                                        {opportunity.priority}
                                    </Badge>
                                </div>
                                <p className="text-sm text-muted-foreground mb-3">
                                    {opportunity.description}
                                </p>
                                <div className="flex items-center justify-between">
                                    <div className="flex gap-2">
                                        <Badge variant="outline">{opportunity.objective}</Badge>
                                        <Badge variant="outline">{opportunity.category}</Badge>
                                    </div>
                                    <Button size="sm" variant="outline">
                                        Create Move
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Refresh Button */}
            <div className="flex justify-center">
                <Button onClick={loadAnalytics} variant="outline" disabled={loading}>
                    {loading ? 'Refreshing...' : 'Refresh Analytics'}
                </Button>
            </div>
        </div>
    );
}
