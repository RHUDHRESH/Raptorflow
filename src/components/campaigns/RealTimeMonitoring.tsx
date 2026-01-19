"use client";

import { useState, useEffect } from 'react';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  TrendingUp,
  TrendingDown,
  Users,
  DollarSign,
  Target,
  Bell,
  Settings,
  RefreshCw,
  Play,
  Pause,
  Square,
  Eye,
  Download,
  Filter,
  Search,
  MoreVertical,
  ChevronDown,
  ChevronUp,
  Wifi,
  WifiOff,
  Cpu,
  Database,
  Globe,
  Mail,
  MessageSquare,
  Phone
} from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { useEnhancedCampaignStore } from '@/stores/enhancedCampaignStore';
import { cn } from '@/lib/utils';
import { format, formatDistanceToNow } from 'date-fns';

interface RealTimeMetric {
  id: string;
  name: string;
  value: number;
  previousValue: number;
  change: number;
  changeType: 'increase' | 'decrease';
  unit: string;
  trend: number[];
  status: 'normal' | 'warning' | 'critical';
  threshold: {
    warning: number;
    critical: number;
  };
  lastUpdated: Date;
}

interface LiveActivity {
  id: string;
  type: 'email_sent' | 'social_post' | 'sms_sent' | 'conversion' | 'error' | 'alert';
  description: string;
  channel: string;
  campaign?: string;
  timestamp: Date;
  status: 'success' | 'pending' | 'failed';
  metadata: {
    recipient?: string;
    subject?: string;
    platform?: string;
    amount?: number;
    error?: string;
  };
}

interface SystemHealth {
  component: string;
  status: 'healthy' | 'degraded' | 'down';
  responseTime: number;
  uptime: number;
  errorRate: number;
  lastCheck: Date;
  dependencies: string[];
}

interface Alert {
  id: string;
  type: 'performance' | 'error' | 'budget' | 'engagement';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  timestamp: Date;
  status: 'active' | 'acknowledged' | 'resolved';
  actions: {
    primary: string;
    secondary?: string;
  };
  metadata: {
    campaign?: string;
    channel?: string;
    metric?: string;
    threshold?: number;
    currentValue?: number;
  };
}

interface ActiveCampaign {
  id: string;
  name: string;
  status: 'running' | 'paused' | 'stopped';
  progress: number;
  startTime: Date;
  estimatedEnd?: Date;
  currentActivity: string;
  metrics: {
    sent: number;
    opens: number;
    clicks: number;
    conversions: number;
    revenue: number;
  };
  issues: {
    type: string;
    count: number;
    description: string;
  }[];
}

export function RealTimeMonitoring() {
  const [activeTab, setActiveTab] = useState<'metrics' | 'activity' | 'health' | 'alerts' | 'campaigns'>('metrics');
  const [isMonitoring, setIsMonitoring] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  // Mock real-time metrics
  const [metrics, setMetrics] = useState<RealTimeMetric[]>([
    {
      id: '1',
      name: 'Active Users',
      value: 1247,
      previousValue: 1156,
      change: 7.9,
      changeType: 'increase',
      unit: 'users',
      trend: [980, 1050, 1100, 1156, 1200, 1247],
      status: 'normal',
      threshold: { warning: 1500, critical: 2000 },
      lastUpdated: new Date()
    },
    {
      id: '2',
      name: 'Email Send Rate',
      value: 892,
      previousValue: 945,
      change: -5.6,
      changeType: 'decrease',
      unit: '/min',
      trend: [980, 965, 950, 945, 920, 892],
      status: 'warning',
      threshold: { warning: 800, critical: 500 },
      lastUpdated: new Date()
    },
    {
      id: '3',
      name: 'Conversion Rate',
      value: 4.2,
      previousValue: 4.5,
      change: -6.7,
      changeType: 'decrease',
      unit: '%',
      trend: [4.8, 4.7, 4.6, 4.5, 4.3, 4.2],
      status: 'warning',
      threshold: { warning: 3.5, critical: 2.5 },
      lastUpdated: new Date()
    },
    {
      id: '4',
      name: 'Revenue/Minute',
      value: 245.60,
      previousValue: 198.40,
      change: 23.8,
      changeType: 'increase',
      unit: '$',
      trend: [150, 165, 180, 195, 210, 245.60],
      status: 'normal',
      threshold: { warning: 100, critical: 50 },
      lastUpdated: new Date()
    },
    {
      id: '5',
      name: 'API Response Time',
      value: 245,
      previousValue: 198,
      change: 23.7,
      changeType: 'increase',
      unit: 'ms',
      trend: [180, 190, 200, 210, 225, 245],
      status: 'warning',
      threshold: { warning: 300, critical: 500 },
      lastUpdated: new Date()
    }
  ]);

  // Mock live activity
  const [liveActivity, setLiveActivity] = useState<LiveActivity[]>([
    {
      id: '1',
      type: 'email_sent',
      description: 'Welcome email sent to new subscriber',
      channel: 'email',
      campaign: 'Q1 Product Launch',
      timestamp: new Date(Date.now() - 30000),
      status: 'success',
      metadata: {
        recipient: 'user@example.com',
        subject: 'Welcome to our platform!'
      }
    },
    {
      id: '2',
      type: 'conversion',
      description: 'Purchase completed - Premium Plan',
      channel: 'web',
      campaign: 'Holiday Sales Campaign',
      timestamp: new Date(Date.now() - 45000),
      status: 'success',
      metadata: {
        amount: 99.00
      }
    },
    {
      id: '3',
      type: 'social_post',
      description: 'New product announcement posted',
      channel: 'social',
      campaign: 'Q1 Product Launch',
      timestamp: new Date(Date.now() - 60000),
      status: 'success',
      metadata: {
        platform: 'Twitter',
        subject: 'Exciting news! Our new product is now live!'
      }
    },
    {
      id: '4',
      type: 'error',
      description: 'SMS delivery failed - invalid number',
      channel: 'sms',
      campaign: 'Holiday Sales Campaign',
      timestamp: new Date(Date.now() - 90000),
      status: 'failed',
      metadata: {
        error: 'Invalid phone number format'
      }
    },
    {
      id: '5',
      type: 'alert',
      description: 'Budget threshold reached for campaign',
      channel: 'system',
      campaign: 'Q1 Product Launch',
      timestamp: new Date(Date.now() - 120000),
      status: 'pending',
      metadata: {}
    }
  ]);

  // Mock system health
  const [systemHealth, setSystemHealth] = useState<SystemHealth[]>([
    {
      component: 'Email Service',
      status: 'healthy',
      responseTime: 145,
      uptime: 99.9,
      errorRate: 0.1,
      lastCheck: new Date(),
      dependencies: ['SMTP Server', 'Database']
    },
    {
      component: 'Social Media API',
      status: 'degraded',
      responseTime: 450,
      uptime: 98.5,
      errorRate: 2.3,
      lastCheck: new Date(),
      dependencies: ['Twitter API', 'Facebook API']
    },
    {
      component: 'SMS Gateway',
      status: 'healthy',
      responseTime: 89,
      uptime: 99.7,
      errorRate: 0.3,
      lastCheck: new Date(),
      dependencies: ['Twilio API']
    },
    {
      component: 'Database',
      status: 'healthy',
      responseTime: 23,
      uptime: 99.99,
      errorRate: 0.01,
      lastCheck: new Date(),
      dependencies: []
    },
    {
      component: 'Web Server',
      status: 'healthy',
      responseTime: 67,
      uptime: 99.8,
      errorRate: 0.2,
      lastCheck: new Date(),
      dependencies: ['Load Balancer', 'Application Server']
    }
  ]);

  // Mock alerts
  const [alerts, setAlerts] = useState<Alert[]>([
    {
      id: '1',
      type: 'performance',
      severity: 'medium',
      title: 'Email send rate below threshold',
      description: 'Email send rate has dropped below the warning threshold of 800/min',
      timestamp: new Date(Date.now() - 300000),
      status: 'active',
      actions: {
        primary: 'Investigate email service',
        secondary: 'Pause affected campaigns'
      },
      metadata: {
        channel: 'email',
        metric: 'send_rate',
        threshold: 800,
        currentValue: 892
      }
    },
    {
      id: '2',
      type: 'budget',
      severity: 'high',
      title: 'Campaign budget nearly exhausted',
      description: 'Q1 Product Launch campaign has used 95% of allocated budget',
      timestamp: new Date(Date.now() - 600000),
      status: 'active',
      actions: {
        primary: 'Review budget allocation',
        secondary: 'Pause campaign'
      },
      metadata: {
        campaign: 'Q1 Product Launch',
        threshold: 95,
        currentValue: 95
      }
    },
    {
      id: '3',
      type: 'error',
      severity: 'low',
      title: 'SMS delivery failures increasing',
      description: 'SMS delivery failure rate has increased to 3.2%',
      timestamp: new Date(Date.now() - 900000),
      status: 'acknowledged',
      actions: {
        primary: 'Check phone number validation'
      },
      metadata: {
        channel: 'sms',
        metric: 'delivery_failure_rate',
        currentValue: 3.2
      }
    }
  ]);

  // Mock active campaigns
  const [activeCampaigns, setActiveCampaigns] = useState<ActiveCampaign[]>([
    {
      id: '1',
      name: 'Q1 Product Launch',
      status: 'running',
      progress: 67,
      startTime: new Date(Date.now() - 3600000),
      estimatedEnd: new Date(Date.now() + 1800000),
      currentActivity: 'Sending follow-up emails',
      metrics: {
        sent: 15420,
        opens: 8920,
        clicks: 2340,
        conversions: 680,
        revenue: 34000
      },
      issues: [
        {
          type: 'delivery',
          count: 12,
          description: 'Email delivery failures'
        }
      ]
    },
    {
      id: '2',
      name: 'Holiday Sales Campaign',
      status: 'paused',
      progress: 85,
      startTime: new Date(Date.now() - 7200000),
      currentActivity: 'Paused - budget review',
      metrics: {
        sent: 32400,
        opens: 18920,
        clicks: 5480,
        conversions: 1240,
        revenue: 62000
      },
      issues: []
    }
  ]);

  // Simulate real-time updates
  useEffect(() => {
    if (!isMonitoring || !autoRefresh) return;

    const interval = setInterval(() => {
      // Update metrics with random changes
      setMetrics(prev => prev.map(metric => ({
        ...metric,
        value: metric.value + (Math.random() - 0.5) * metric.value * 0.05,
        trend: [...metric.trend.slice(1), metric.value + (Math.random() - 0.5) * metric.value * 0.05],
        lastUpdated: new Date()
      })));

      // Add new live activity
      const activityTypes = ['email_sent', 'conversion', 'social_post'];
      const newActivity: LiveActivity = {
        id: Date.now().toString(),
        type: activityTypes[Math.floor(Math.random() * activityTypes.length)] as any,
        description: 'New activity generated',
        channel: ['email', 'web', 'social'][Math.floor(Math.random() * 3)],
        timestamp: new Date(),
        status: 'success',
        metadata: {}
      };

      setLiveActivity(prev => [newActivity, ...prev.slice(0, 49)]);
    }, 5000);

    return () => clearInterval(interval);
  }, [isMonitoring, autoRefresh]);

  // Get activity icon
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'email_sent': return Mail;
      case 'social_post': return MessageSquare;
      case 'sms_sent': return Phone;
      case 'conversion': return DollarSign;
      case 'error': return AlertTriangle;
      case 'alert': return Bell;
      default: return Activity;
    }
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'normal':
      case 'success':
      case 'running': return 'text-[var(--success)]';
      case 'degraded':
      case 'warning':
      case 'paused': return 'text-[var(--warning)]';
      case 'down':
      case 'critical':
      case 'failed':
      case 'stopped': return 'text-[var(--destructive)]';
      default: return 'text-[var(--ink-muted)]';
    }
  };

  // Render real-time metrics
  const renderRealTimeMetrics = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Real-Time Metrics</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Live performance metrics and trends
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2">
            <div className={cn(
              "w-2 h-2 rounded-full",
              isMonitoring ? "bg-[var(--success)] animate-pulse" : "bg-[var(--ink-ghost)]"
            )} />
            <span className="text-sm text-[var(--ink)]">
              {isMonitoring ? 'Monitoring' : 'Paused'}
            </span>
          </div>

          <BlueprintButton
            variant={isMonitoring ? 'secondary' : 'blueprint'}
            size="sm"
            onClick={() => setIsMonitoring(!isMonitoring)}
          >
            {isMonitoring ? <Pause size={14} /> : <Play size={14} />}
            {isMonitoring ? 'Pause' : 'Resume'}
          </BlueprintButton>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {metrics.map((metric) => (
          <BlueprintCard key={metric.id} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-sm font-medium text-[var(--ink-muted)]">{metric.name}</h3>
                <div className="text-2xl font-bold text-[var(--ink)] mt-1">
                  {metric.unit === '$' ? `$${metric.value.toFixed(2)}` :
                   metric.unit === '%' ? `${metric.value.toFixed(1)}%` :
                   metric.unit === 'ms' ? `${Math.round(metric.value)}ms` :
                   metric.unit === '/min' ? `${Math.round(metric.value)}/min` :
                   Math.round(metric.value).toLocaleString()}
                </div>
              </div>

              <div className={cn(
                "flex items-center gap-1 px-2 py-1 rounded text-xs font-medium",
                metric.changeType === 'increase' && "bg-[var(--success-light)]/10 text-[var(--success)]",
                metric.changeType === 'decrease' && "bg-[var(--destructive-light)]/10 text-[var(--destructive)]"
              )}>
                {metric.changeType === 'increase' ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                {Math.abs(metric.change).toFixed(1)}%
              </div>
            </div>

            {/* Status indicator */}
            <div className="flex items-center gap-2 mb-4">
              <div className={cn(
                "w-2 h-2 rounded-full",
                metric.status === 'normal' && "bg-[var(--success)]",
                metric.status === 'warning' && "bg-[var(--warning)]",
                metric.status === 'critical' && "bg-[var(--destructive)]"
              )} />
              <span className="text-xs text-[var(--ink-muted)] capitalize">{metric.status}</span>
              <span className="text-xs text-[var(--ink-ghost)]">
                Updated {formatDistanceToNow(metric.lastUpdated, { addSuffix: true })}
              </span>
            </div>

            {/* Mini trend chart */}
            <div className="h-12">
              <div className="h-full flex items-end gap-1">
                {metric.trend.map((value, index) => (
                  <div
                    key={index}
                    className={cn(
                      "flex-1 rounded-t",
                      metric.status === 'normal' && "bg-[var(--success-light)]/20",
                      metric.status === 'warning' && "bg-[var(--warning-light)]/20",
                      metric.status === 'critical' && "bg-[var(--destructive-light)]/20"
                    )}
                    style={{ height: `${(value / Math.max(...metric.trend)) * 100}%` }}
                  />
                ))}
              </div>
            </div>
          </BlueprintCard>
        ))}
      </div>
    </div>
  );

  // Render live activity feed
  const renderLiveActivity = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Live Activity Feed</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Real-time activity across all channels
          </p>
        </div>

        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-[var(--structure-subtle)] text-[var(--blueprint)]"
            />
            Auto-refresh
          </label>

          <BlueprintButton variant="secondary" size="sm">
            <Filter size={14} />
            Filter
          </BlueprintButton>
        </div>
      </div>

      <BlueprintCard className="p-6">
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {liveActivity.map((activity) => {
            const Icon = getActivityIcon(activity.type);
            return (
              <div key={activity.id} className="flex items-start gap-3 p-3 bg-[var(--surface)] rounded-lg">
                <div className={cn(
                  "w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0",
                  activity.status === 'success' && "bg-[var(--success-light)]/10",
                  activity.status === 'pending' && "bg-[var(--warning-light)]/10",
                  activity.status === 'failed' && "bg-[var(--destructive-light)]/10"
                )}>
                  <Icon size={16} className={cn(
                    activity.status === 'success' && "text-[var(--success)]",
                    activity.status === 'pending' && "text-[var(--warning)]",
                    activity.status === 'failed' && "text-[var(--destructive)]"
                  )} />
                </div>

                <div className="flex-1">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-[var(--ink)]">{activity.description}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-[var(--ink-muted)] capitalize">{activity.channel}</span>
                        {activity.campaign && (
                          <span className="text-xs text-[var(--blueprint)]">{activity.campaign}</span>
                        )}
                      </div>
                      {activity.metadata.amount && (
                        <p className="text-sm font-medium text-[var(--success)] mt-1">
                          ${activity.metadata.amount.toFixed(2)}
                        </p>
                      )}
                      {activity.metadata.error && (
                        <p className="text-xs text-[var(--destructive)] mt-1">
                          {activity.metadata.error}
                        </p>
                      )}
                    </div>

                    <div className="text-right">
                      <span className="text-xs text-[var(--ink-muted)]">
                        {formatDistanceToNow(activity.timestamp, { addSuffix: true })}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </BlueprintCard>
    </div>
  );

  // Render system health
  const renderSystemHealth = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">System Health</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Monitor system components and dependencies
          </p>
        </div>

        <BlueprintButton variant="secondary" className="flex items-center gap-2">
          <RefreshCw size={16} />
          Refresh
        </BlueprintButton>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {systemHealth.map((component) => (
          <BlueprintCard key={component.component} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-[var(--ink)]">{component.component}</h3>
                <BlueprintBadge
                  variant={component.status === 'healthy' ? 'success' : component.status === 'degraded' ? 'warning' : 'error'}
                  size="sm"
                >
                  {component.status}
                </BlueprintBadge>
              </div>

              <div className={cn(
                "flex items-center gap-1",
                getStatusColor(component.status)
              )}>
                {component.status === 'healthy' && <Wifi size={20} />}
                {component.status === 'degraded' && <Wifi size={20} />}
                {component.status === 'down' && <WifiOff size={20} />}
              </div>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div>
                <div className="text-xs text-[var(--ink-muted)]">Response Time</div>
                <div className="text-sm font-medium text-[var(--ink)]">
                  {component.responseTime}ms
                </div>
              </div>
              <div>
                <div className="text-xs text-[var(--ink-muted)]">Uptime</div>
                <div className="text-sm font-medium text-[var(--success)]">
                  {component.uptime}%
                </div>
              </div>
              <div>
                <div className="text-xs text-[var(--ink-muted)]">Error Rate</div>
                <div className="text-sm font-medium text-[var(--destructive)]">
                  {component.errorRate}%
                </div>
              </div>
            </div>

            {/* Dependencies */}
            {component.dependencies.length > 0 && (
              <div>
                <div className="text-xs text-[var(--ink-muted)] mb-2">Dependencies</div>
                <div className="flex flex-wrap gap-1">
                  {component.dependencies.map((dep) => (
                    <span key={dep} className="px-2 py-1 text-xs bg-[var(--surface)] text-[var(--ink)] rounded">
                      {dep}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Last check */}
            <div className="flex items-center justify-between pt-4 border-t border-[var(--structure-subtle)]">
              <span className="text-xs text-[var(--ink-muted)]">
                Last checked {formatDistanceToNow(component.lastCheck, { addSuffix: true })}
              </span>

              <BlueprintButton variant="secondary" size="sm">
                <Eye size={14} />
                Details
              </BlueprintButton>
            </div>
          </BlueprintCard>
        ))}
      </div>
    </div>
  );

  // Render alerts
  const renderAlerts = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Active Alerts</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            System alerts and notifications
          </p>
        </div>

        <div className="flex items-center gap-2">
          <BlueprintBadge variant="error" size="sm">
            {alerts.filter(a => a.status === 'active').length} Active
          </BlueprintBadge>
        </div>
      </div>

      <div className="space-y-4">
        {alerts.map((alert) => (
          <BlueprintCard key={alert.id} className={cn(
            "p-6",
            alert.status === 'resolved' && "opacity-50"
          )}>
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-start gap-3">
                <div className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0",
                  alert.severity === 'critical' && "bg-[var(--destructive-light)]/10",
                  alert.severity === 'high' && "bg-[var(--warning-light)]/10",
                  alert.severity === 'medium' && "bg-[var(--info-light)]/10",
                  alert.severity === 'low' && "bg-[var(--surface)]"
                )}>
                  <AlertTriangle size={20} className={cn(
                    alert.severity === 'critical' && "text-[var(--destructive)]",
                    alert.severity === 'high' && "text-[var(--warning)]",
                    alert.severity === 'medium' && "text-[var(--info)]",
                    alert.severity === 'low' && "text-[var(--ink-ghost)]"
                  )} />
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-[var(--ink)]">{alert.title}</h3>
                  <p className="text-sm text-[var(--ink-muted)] mt-1">{alert.description}</p>

                  <div className="flex items-center gap-2 mt-2">
                    <BlueprintBadge
                      variant={alert.severity === 'critical' ? 'error' : alert.severity === 'high' ? 'warning' : 'default'}
                      size="sm"
                    >
                      {alert.severity}
                    </BlueprintBadge>

                    <BlueprintBadge
                      variant={alert.status === 'active' ? 'success' : 'default'}
                      size="sm"
                    >
                      {alert.status}
                    </BlueprintBadge>

                    <span className="text-xs text-[var(--ink-muted)]">
                      {formatDistanceToNow(alert.timestamp, { addSuffix: true })}
                    </span>
                  </div>
                </div>
              </div>

              <button className="p-1 text-[var(--ink-ghost)] hover:text-[var(--ink)]">
                <MoreVertical size={16} />
              </button>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <BlueprintButton size="sm">
                {alert.actions.primary}
              </BlueprintButton>

              {alert.actions.secondary && (
                <BlueprintButton variant="secondary" size="sm">
                  {alert.actions.secondary}
                </BlueprintButton>
              )}
            </div>
          </BlueprintCard>
        ))}
      </div>
    </div>
  );

  // Render active campaigns
  const renderActiveCampaigns = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Active Campaigns</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Monitor running campaigns in real-time
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {activeCampaigns.map((campaign) => (
          <BlueprintCard key={campaign.id} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-[var(--ink)]">{campaign.name}</h3>
                <div className="flex items-center gap-2 mt-1">
                  <BlueprintBadge
                    variant={campaign.status === 'running' ? 'success' : campaign.status === 'paused' ? 'warning' : 'default'}
                    size="sm"
                  >
                    {campaign.status}
                  </BlueprintBadge>

                  <span className="text-xs text-[var(--ink-muted)]">
                    Started {formatDistanceToNow(campaign.startTime, { addSuffix: true })}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {campaign.status === 'running' ? (
                  <BlueprintButton variant="secondary" size="sm">
                    <Pause size={14} />
                    Pause
                  </BlueprintButton>
                ) : (
                  <BlueprintButton size="sm">
                    <Play size={14} />
                    Resume
                  </BlueprintButton>
                )}
              </div>
            </div>

            {/* Progress */}
            <div className="mb-4">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-[var(--ink-muted)]">Progress</span>
                <span className="text-[var(--ink)]">{campaign.progress}%</span>
              </div>
              <div className="w-full bg-[var(--structure-subtle)] rounded-full h-2">
                <div
                  className="bg-[var(--blueprint)] h-2 rounded-full transition-all"
                  style={{ width: `${campaign.progress}%` }}
                />
              </div>
            </div>

            {/* Current activity */}
            <div className="mb-4">
              <div className="text-sm text-[var(--ink-muted)] mb-1">Current Activity</div>
              <div className="text-sm text-[var(--ink)]">{campaign.currentActivity}</div>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-5 gap-4 mb-4">
              <div className="text-center">
                <div className="text-lg font-bold text-[var(--ink)]">
                  {campaign.metrics.sent.toLocaleString()}
                </div>
                <div className="text-xs text-[var(--ink-muted)]">Sent</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-[var(--blueprint)]">
                  {campaign.metrics.opens.toLocaleString()}
                </div>
                <div className="text-xs text-[var(--ink-muted)]">Opens</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-[var(--success)]">
                  {campaign.metrics.clicks.toLocaleString()}
                </div>
                <div className="text-xs text-[var(--ink-muted)]">Clicks</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-[var(--success)]">
                  {campaign.metrics.conversions.toLocaleString()}
                </div>
                <div className="text-xs text-[var(--ink-muted)]">Conversions</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-[var(--success)]">
                  ${campaign.metrics.revenue.toLocaleString()}
                </div>
                <div className="text-xs text-[var(--ink-muted)]">Revenue</div>
              </div>
            </div>

            {/* Issues */}
            {campaign.issues.length > 0 && (
              <div className="p-3 bg-[var(--warning-light)]/10 rounded-lg">
                <div className="text-sm font-medium text-[var(--warning)] mb-2">Issues Detected</div>
                <div className="space-y-1">
                  {campaign.issues.map((issue, index) => (
                    <div key={index} className="text-xs text-[var(--ink)]">
                      {issue.count}x {issue.description}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </BlueprintCard>
        ))}
      </div>
    </div>
  );

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-[var(--structure-subtle)]">
        <div>
          <h1 className="text-2xl font-bold text-[var(--ink)]">Real-Time Monitoring</h1>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Live monitoring of campaigns and system health
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className={cn(
            "flex items-center gap-2 px-3 py-1 rounded-full text-sm",
            isMonitoring ? "bg-[var(--success-light)]/10 text-[var(--success)]" : "bg-[var(--surface)] text-[var(--ink-muted)]"
          )}>
            <div className={cn(
              "w-2 h-2 rounded-full",
              isMonitoring && "animate-pulse"
            )} />
            {isMonitoring ? 'Live' : 'Paused'}
          </div>

          <BlueprintButton variant="secondary" className="flex items-center gap-2">
            <Settings size={16} />
            Settings
          </BlueprintButton>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-6 px-6 border-b border-[var(--structure-subtle)]">
        {[
          { id: 'metrics', label: 'Metrics', icon: Activity },
          { id: 'activity', label: 'Activity', icon: Zap },
          { id: 'health', label: 'Health', icon: Cpu },
          { id: 'alerts', label: 'Alerts', icon: Bell },
          { id: 'campaigns', label: 'Campaigns', icon: Target }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={cn(
                "flex items-center gap-2 py-3 px-1 text-sm font-medium border-b-2 transition-colors",
                activeTab === tab.id
                  ? "text-[var(--ink)] border-[var(--ink)]"
                  : "text-[var(--ink-muted)] border-transparent hover:text-[var(--ink)]"
              )}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'metrics' && renderRealTimeMetrics()}
        {activeTab === 'activity' && renderLiveActivity()}
        {activeTab === 'health' && renderSystemHealth()}
        {activeTab === 'alerts' && renderAlerts()}
        {activeTab === 'campaigns' && renderActiveCampaigns()}
      </div>
    </div>
  );
}
