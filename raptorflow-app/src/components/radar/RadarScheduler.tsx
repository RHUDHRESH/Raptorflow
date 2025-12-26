'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { 
    startScheduler, 
    stopScheduler, 
    getSchedulerStatus, 
    getSourceHealth,
    scheduleManualScan
} from '@/lib/radar';
import { toast } from 'sonner';
import { 
    Play, 
    Pause, 
    Clock, 
    Activity, 
    CheckCircle, 
    AlertTriangle, 
    XCircle,
    RefreshCw
} from 'lucide-react';

interface RadarSchedulerProps {
    className?: string;
}

export function RadarScheduler({ className }: RadarSchedulerProps) {
    const [schedulerStatus, setSchedulerStatus] = useState<any>(null);
    const [sourceHealth, setSourceHealth] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [isScanning, setIsScanning] = useState(false);

    useEffect(() => {
        loadSchedulerData();
        // Auto-refresh every 30 seconds
        const interval = setInterval(loadSchedulerData, 30000);
        return () => clearInterval(interval);
    }, []);

    const loadSchedulerData = async () => {
        try {
            const [status, health] = await Promise.all([
                getSchedulerStatus(),
                getSourceHealth()
            ]);
            setSchedulerStatus(status);
            setSourceHealth(health);
        } catch (error) {
            console.error('Failed to load scheduler data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleToggleScheduler = async () => {
        try {
            if (schedulerStatus?.is_active) {
                await stopScheduler();
                toast.success('Scheduler stopped');
            } else {
                await startScheduler();
                toast.success('Scheduler started');
            }
            await loadSchedulerData();
        } catch (error) {
            toast.error('Failed to toggle scheduler', {
                description: error instanceof Error ? error.message : 'Unknown error'
            });
        }
    };

    const handleManualScan = async (sourceIds: string[]) => {
        if (isScanning) return;
        
        setIsScanning(true);
        try {
            toast.loading('Starting manual scan...', { id: 'manual-scan' });
            
            await scheduleManualScan(sourceIds, 'recon');
            
            toast.success('Manual scan scheduled!', { 
                id: 'manual-scan',
                description: `Scanning ${sourceIds.length} sources` 
            });
            
            await loadSchedulerData();
            
        } catch (error) {
            toast.error('Manual scan failed', { 
                id: 'manual-scan',
                description: error instanceof Error ? error.message : 'Unknown error'
            });
        } finally {
            setIsScanning(false);
        }
    };

    const getHealthIcon = (health: number) => {
        if (health >= 80) return <CheckCircle className="w-4 h-4 text-green-500" />;
        if (health >= 50) return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
        return <XCircle className="w-4 h-4 text-red-500" />;
    };

    const getHealthColor = (health: number) => {
        if (health >= 80) return 'text-green-600';
        if (health >= 50) return 'text-yellow-600';
        return 'text-red-600';
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                    <p className="text-muted-foreground">Loading scheduler status...</p>
                </div>
            </div>
        );
    }

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Scheduler Control */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Clock className="w-5 h-5" />
                        Scheduler Control
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center justify-between">
                        <div className="space-y-1">
                            <div className="flex items-center gap-2">
                                <span className="font-medium">Scheduler Status</span>
                                <Badge variant={schedulerStatus?.is_active ? 'default' : 'secondary'}>
                                    {schedulerStatus?.is_active ? 'Active' : 'Inactive'}
                                </Badge>
                            </div>
                            <div className="text-sm text-muted-foreground">
                                {schedulerStatus?.is_active 
                                    ? `${schedulerStatus?.active_tasks || 0} active tasks`
                                    : 'Scheduler is not running'
                                }
                            </div>
                        </div>
                        
                        <div className="flex items-center gap-2">
                            <Switch
                                checked={schedulerStatus?.is_active || false}
                                onCheckedChange={handleToggleScheduler}
                            />
                            <Button
                                onClick={handleToggleScheduler}
                                variant={schedulerStatus?.is_active ? 'destructive' : 'default'}
                                size="sm"
                            >
                                {schedulerStatus?.is_active ? (
                                    <>
                                        <Pause className="w-4 h-4 mr-2" />
                                        Stop
                                    </>
                                ) : (
                                    <>
                                        <Play className="w-4 h-4 mr-2" />
                                        Start
                                    </>
                                )}
                            </Button>
                        </div>
                    </div>

                    {/* Scheduler Stats */}
                    {schedulerStatus?.is_active && (
                        <div className="grid grid-cols-3 gap-4 mt-6">
                            <div className="text-center">
                                <div className="text-2xl font-bold text-primary">
                                    {schedulerStatus?.active_tasks || 0}
                                </div>
                                <div className="text-sm text-muted-foreground">Active Tasks</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-blue-600">
                                    {schedulerStatus?.cache_size || 0}
                                </div>
                                <div className="text-sm text-muted-foreground">Cache Size</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-green-600">
                                    {sourceHealth?.filter((s: any) => s.health >= 80).length || 0}
                                </div>
                                <div className="text-sm text-muted-foreground">Healthy Sources</div>
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Source Health */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Activity className="w-5 h-5" />
                        Source Health
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-3">
                        {sourceHealth?.map((source: any, index: number) => (
                            <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                                <div className="flex items-center gap-3">
                                    {getHealthIcon(source.health)}
                                    <div>
                                        <div className="font-medium">{source.name}</div>
                                        <div className="text-sm text-muted-foreground">
                                            {source.type} • Last checked: {source.last_checked}
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="flex items-center gap-3">
                                    <div className="text-right">
                                        <div className={`font-medium ${getHealthColor(source.health)}`}>
                                            {source.health}%
                                        </div>
                                        <div className="text-sm text-muted-foreground">
                                            {source.status}
                                        </div>
                                    </div>
                                    
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => handleManualScan([source.id])}
                                        disabled={isScanning}
                                    >
                                        {isScanning ? (
                                            <RefreshCw className="w-4 h-4 animate-spin" />
                                        ) : (
                                            'Scan'
                                        )}
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Scan All Sources */}
                    <div className="mt-6 pt-6 border-t">
                        <Button
                            onClick={() => handleManualScan(sourceHealth?.map((s: any) => s.id) || [])}
                            disabled={isScanning || !schedulerStatus?.is_active}
                            className="w-full"
                        >
                            {isScanning ? (
                                <>
                                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                                    Scanning All Sources...
                                </>
                            ) : (
                                <>
                                    <Play className="w-4 h-4 mr-2" />
                                    Scan All Sources
                                </>
                            )}
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Refresh Button */}
            <div className="flex justify-center">
                <Button onClick={loadSchedulerData} variant="outline" disabled={loading}>
                    {loading ? 'Refreshing...' : 'Refresh Status'}
                </Button>
            </div>
        </div>
    );
}
