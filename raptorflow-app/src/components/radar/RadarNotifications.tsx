'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { 
    processNotifications, 
    getDailyDigest 
} from '@/lib/radar';
import { toast } from 'sonner';
import { 
    Bell, 
    BellOff, 
    Mail, 
    AlertTriangle, 
    TrendingUp, 
    DollarSign,
    Calendar,
    CheckCircle,
    Settings,
    RefreshCw
} from 'lucide-react';

interface RadarNotificationsProps {
    className?: string;
}

export function RadarNotifications({ className }: RadarNotificationsProps) {
    const [notifications, setNotifications] = useState<any[]>([]);
    const [dailyDigest, setDailyDigest] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [preferences, setPreferences] = useState({
        highStrengthSignals: true,
        competitorActivitySpikes: true,
        pricingChanges: true,
        dailyDigest: true
    });

    useEffect(() => {
        loadNotificationData();
    }, []);

    const loadNotificationData = async () => {
        setLoading(true);
        try {
            const [digestData] = await Promise.all([
                getDailyDigest()
            ]);
            setDailyDigest(digestData);
            
            // Mock notifications for now
            const mockNotifications = [
                {
                    id: '1',
                    type: 'high_strength_signal',
                    priority: 'high',
                    title: 'High-Strength Signal Detected',
                    message: 'Competitor A launched new enterprise pricing tier',
                    created_at: new Date().toISOString(),
                    signal_id: 'signal-123'
                },
                {
                    id: '2',
                    type: 'competitor_activity_spike',
                    priority: 'medium',
                    title: 'Competitor Activity Spike',
                    message: 'Unusual activity detected from 3 competitors',
                    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
                },
                {
                    id: '3',
                    type: 'pricing_change',
                    priority: 'high',
                    title: 'Pricing Change Alert',
                    message: 'Competitor B changed pricing structure',
                    created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString()
                }
            ];
            setNotifications(mockNotifications);
            
        } catch (error) {
            toast.error('Failed to load notifications', {
                description: error instanceof Error ? error.message : 'Unknown error'
            });
        } finally {
            setLoading(false);
        }
    };

    const handleProcessNotifications = async (signalIds: string[]) => {
        try {
            toast.loading('Processing notifications...', { id: 'process-notifications' });
            
            const processedNotifications = await processNotifications(signalIds, preferences);
            
            toast.success('Notifications processed!', { 
                id: 'process-notifications',
                description: `Generated ${processedNotifications.length} notifications` 
            });
            
            await loadNotificationData();
            
        } catch (error) {
            toast.error('Failed to process notifications', { 
                id: 'process-notifications',
                description: error instanceof Error ? error.message : 'Unknown error'
            });
        }
    };

    const getNotificationIcon = (type: string) => {
        switch (type) {
            case 'high_strength_signal':
                return <TrendingUp className="w-4 h-4 text-blue-500" />;
            case 'competitor_activity_spike':
                return <AlertTriangle className="w-4 h-4 text-orange-500" />;
            case 'pricing_change':
                return <DollarSign className="w-4 h-4 text-green-500" />;
            default:
                return <Bell className="w-4 h-4 text-gray-500" />;
        }
    };

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case 'high':
                return 'bg-red-50 text-red-600 border-red-200';
            case 'medium':
                return 'bg-yellow-50 text-yellow-600 border-yellow-200';
            case 'low':
                return 'bg-gray-50 text-gray-600 border-gray-200';
            default:
                return 'bg-gray-50 text-gray-600 border-gray-200';
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                    <p className="text-muted-foreground">Loading notifications...</p>
                </div>
            </div>
        );
    }

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Notification Preferences */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Settings className="w-5 h-5" />
                        Notification Preferences
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <div className="space-y-1">
                                <div className="font-medium">High-Strength Signals</div>
                                <div className="text-sm text-muted-foreground">
                                    Get notified about high-confidence competitive signals
                                </div>
                            </div>
                            <Switch
                                checked={preferences.highStrengthSignals}
                                onCheckedChange={(checked) => 
                                    setPreferences(prev => ({ ...prev, highStrengthSignals: checked }))
                                }
                            />
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="space-y-1">
                                <div className="font-medium">Competitor Activity Spikes</div>
                                <div className="text-sm text-muted-foreground">
                                    Alert on unusual competitor activity patterns
                                </div>
                            </div>
                            <Switch
                                checked={preferences.competitorActivitySpikes}
                                onCheckedChange={(checked) => 
                                    setPreferences(prev => ({ ...prev, competitorActivitySpikes: checked }))
                                }
                            />
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="space-y-1">
                                <div className="font-medium">Pricing Changes</div>
                                <div className="text-sm text-muted-foreground">
                                    Monitor competitor pricing updates
                                </div>
                            </div>
                            <Switch
                                checked={preferences.pricingChanges}
                                onCheckedChange={(checked) => 
                                    setPreferences(prev => ({ ...prev, pricingChanges: checked }))
                                }
                            />
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="space-y-1">
                                <div className="font-medium">Daily Digest</div>
                                <div className="text-sm text-muted-foreground">
                                    Receive daily summary of competitive intelligence
                                </div>
                            </div>
                            <Switch
                                checked={preferences.dailyDigest}
                                onCheckedChange={(checked) => 
                                    setPreferences(prev => ({ ...prev, dailyDigest: checked }))
                                }
                            />
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Daily Digest */}
            {dailyDigest && preferences.dailyDigest && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Calendar className="w-5 h-5" />
                            Daily Digest
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="font-medium">Today's Summary</div>
                                    <div className="text-sm text-muted-foreground">
                                        {dailyDigest.signal_count} signals detected
                                    </div>
                                </div>
                                <Badge variant="outline">
                                    {new Date().toLocaleDateString()}
                                </Badge>
                            </div>

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                {Object.entries(dailyDigest.by_category || {}).map(([category, count]: [string, any]) => (
                                    <div key={category} className="text-center">
                                        <div className="text-2xl font-bold text-primary">
                                            {count}
                                        </div>
                                        <div className="text-sm text-muted-foreground capitalize">
                                            {category}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="pt-4 border-t">
                                <h4 className="font-medium mb-2">Key Insights</h4>
                                <div className="space-y-2">
                                    {dailyDigest.top_signals?.slice(0, 3).map((signal: any, index: number) => (
                                        <div key={index} className="p-3 bg-muted/50 rounded-lg">
                                            <div className="font-medium">{signal.title}</div>
                                            <div className="text-sm text-muted-foreground">{signal.summary}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Recent Notifications */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Bell className="w-5 h-5" />
                        Recent Notifications
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-3">
                        {notifications.map((notification) => (
                            <div key={notification.id} className="flex items-start gap-3 p-3 border rounded-lg">
                                <div className="mt-1">
                                    {getNotificationIcon(notification.type)}
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center justify-between mb-1">
                                        <h4 className="font-medium">{notification.title}</h4>
                                        <Badge variant="outline" className={getPriorityColor(notification.priority)}>
                                            {notification.priority}
                                        </Badge>
                                    </div>
                                    <p className="text-sm text-muted-foreground mb-2">
                                        {notification.message}
                                    </p>
                                    <div className="flex items-center justify-between">
                                        <span className="text-xs text-muted-foreground">
                                            {new Date(notification.created_at).toLocaleString()}
                                        </span>
                                        <Button size="sm" variant="outline">
                                            View Details
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {notifications.length === 0 && (
                        <div className="text-center py-8">
                            <BellOff className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                            <h3 className="font-medium mb-2">No notifications</h3>
                            <p className="text-sm text-muted-foreground">
                                You're all caught up! No new notifications to display.
                            </p>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Test Notifications */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Mail className="w-5 h-5" />
                        Test Notifications
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <p className="text-sm text-muted-foreground">
                            Test your notification preferences by processing recent signals.
                        </p>
                        
                        <Button 
                            onClick={() => handleProcessNotifications(['signal-123', 'signal-456'])}
                            className="w-full"
                        >
                            <RefreshCw className="w-4 h-4 mr-2" />
                            Test Notification Processing
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Refresh Button */}
            <div className="flex justify-center">
                <Button onClick={loadNotificationData} variant="outline" disabled={loading}>
                    {loading ? 'Refreshing...' : 'Refresh Notifications'}
                </Button>
            </div>
        </div>
    );
}
