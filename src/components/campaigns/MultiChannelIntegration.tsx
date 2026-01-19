"use client";

import { useState, useEffect } from 'react';
import {
  Globe,
  Mail,
  MessageSquare,
  Phone,
  Share2,
  Zap,
  Settings,
  Plus,
  Edit,
  Trash2,
  CheckCircle,
  AlertTriangle,
  Clock,
  BarChart3,
  Users,
  TrendingUp,
  Link,
  Wifi,
  WifiOff,
  RefreshCw,
  Download,
  Upload,
  Eye,
  MoreVertical,
  ChevronDown,
  ChevronUp,
  ChevronRight,
  Copy,
  ExternalLink
} from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { useEnhancedCampaignStore } from '@/stores/enhancedCampaignStore';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';
import { formatDistanceToNow } from 'date-fns/formatDistanceToNow';

interface ChannelIntegration {
  id: string;
  name: string;
  type: 'email' | 'social' | 'sms' | 'webhook' | 'api' | 'custom';
  provider: string;
  status: 'connected' | 'disconnected' | 'error' | 'pending';
  configuration: {
    apiKey?: string;
    endpoint?: string;
    credentials?: Record<string, any>;
    settings?: Record<string, any>;
  };
  capabilities: {
    sending: boolean;
    tracking: boolean;
    automation: boolean;
    analytics: boolean;
  };
  performance: {
    lastSync: Date;
    successRate: number;
    responseTime: number;
    errorCount: number;
  };
  usage: {
    messagesSent: number;
    dataTransferred: number;
    apiCalls: number;
  };
}

interface SyncRule {
  id: string;
  name: string;
  description: string;
  sourceChannel: string;
  targetChannel: string;
  trigger: 'immediate' | 'scheduled' | 'manual';
  conditions: {
    field: string;
    operator: string;
    value: string;
  }[];
  actions: {
    type: string;
    config: Record<string, any>;
  }[];
  status: 'active' | 'inactive' | 'error';
  lastRun: Date;
  nextRun?: Date;
}

interface CrossChannelCampaign {
  id: string;
  name: string;
  description: string;
  channels: string[];
  strategy: 'sequential' | 'parallel' | 'conditional';
  rules: {
    conditions: string[];
    actions: string[];
  };
  performance: {
    totalReach: number;
    engagement: number;
    conversions: number;
    revenue: number;
  };
  status: 'draft' | 'active' | 'paused' | 'completed';
}

export function MultiChannelIntegration() {
  const [activeTab, setActiveTab] = useState<'channels' | 'sync' | 'campaigns' | 'analytics'>('channels');
  const [selectedChannel, setSelectedChannel] = useState<ChannelIntegration | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);

  // Mock channel integrations
  const [channels, setChannels] = useState<ChannelIntegration[]>([
    {
      id: '1',
      name: 'Mailchimp Email',
      type: 'email',
      provider: 'Mailchimp',
      status: 'connected',
      configuration: {
        apiKey: 'mc_***hidden***',
        endpoint: 'https://api.mailchimp.com/3.0'
      },
      capabilities: {
        sending: true,
        tracking: true,
        automation: true,
        analytics: true
      },
      performance: {
        lastSync: new Date(Date.now() - 3600000),
        successRate: 98.5,
        responseTime: 245,
        errorCount: 2
      },
      usage: {
        messagesSent: 15420,
        dataTransferred: 2.3,
        apiCalls: 890
      }
    },
    {
      id: '2',
      name: 'Twitter API',
      type: 'social',
      provider: 'Twitter',
      status: 'connected',
      configuration: {
        apiKey: 'tw_***hidden***',
        endpoint: 'https://api.twitter.com/2'
      },
      capabilities: {
        sending: true,
        tracking: true,
        automation: true,
        analytics: true
      },
      performance: {
        lastSync: new Date(Date.now() - 1800000),
        successRate: 99.2,
        responseTime: 180,
        errorCount: 1
      },
      usage: {
        messagesSent: 3240,
        dataTransferred: 0.8,
        apiCalls: 2340
      }
    },
    {
      id: '3',
      name: 'Twilio SMS',
      type: 'sms',
      provider: 'Twilio',
      status: 'error',
      configuration: {
        apiKey: 'tw_***hidden***',
        endpoint: 'https://api.twilio.com/2010-04-01'
      },
      capabilities: {
        sending: true,
        tracking: true,
        automation: false,
        analytics: true
      },
      performance: {
        lastSync: new Date(Date.now() - 7200000),
        successRate: 85.3,
        responseTime: 520,
        errorCount: 12
      },
      usage: {
        messagesSent: 8920,
        dataTransferred: 0.4,
        apiCalls: 8920
      }
    },
    {
      id: '4',
      name: 'Custom Webhook',
      type: 'webhook',
      provider: 'Custom',
      status: 'disconnected',
      configuration: {
        endpoint: 'https://api.example.com/webhook'
      },
      capabilities: {
        sending: true,
        tracking: false,
        automation: true,
        analytics: false
      },
      performance: {
        lastSync: new Date(Date.now() - 86400000),
        successRate: 0,
        responseTime: 0,
        errorCount: 0
      },
      usage: {
        messagesSent: 0,
        dataTransferred: 0,
        apiCalls: 0
      }
    }
  ]);

  // Mock sync rules
  const [syncRules, setSyncRules] = useState<SyncRule[]>([
    {
      id: '1',
      name: 'Email to Social Sync',
      description: 'Sync email subscribers to social media custom audiences',
      sourceChannel: '1',
      targetChannel: '2',
      trigger: 'scheduled',
      conditions: [
        { field: 'email_status', operator: 'equals', value: 'active' },
        { field: 'last_activity', operator: 'greater_than', value: '30_days' }
      ],
      actions: [
        { type: 'create_custom_audience', config: { platform: 'twitter' } },
        { type: 'sync_demographics', config: { fields: ['age', 'location'] } }
      ],
      status: 'active',
      lastRun: new Date(Date.now() - 3600000),
      nextRun: new Date(Date.now() + 3600000)
    },
    {
      id: '2',
      name: 'SMS Opt-out Sync',
      description: 'Remove SMS opt-outs from all marketing channels',
      sourceChannel: '3',
      targetChannel: '1',
      trigger: 'immediate',
      conditions: [
        { field: 'sms_status', operator: 'equals', value: 'opted_out' }
      ],
      actions: [
        { type: 'unsubscribe_email', config: { remove_from_lists: true } },
        { type: 'update_crm', config: { status: 'do_not_contact' } }
      ],
      status: 'active',
      lastRun: new Date(Date.now() - 1800000)
    }
  ]);

  // Mock cross-channel campaigns
  const [crossChannelCampaigns, setCrossChannelCampaigns] = useState<CrossChannelCampaign[]>([
    {
      id: '1',
      name: 'Product Launch Multi-Channel',
      description: 'Coordinated launch across email, social, and SMS',
      channels: ['1', '2', '3'],
      strategy: 'sequential',
      rules: {
        conditions: ['email_sent', 'social_engagement'],
        actions: ['sms_followup', 'retargeting_ads']
      },
      performance: {
        totalReach: 45000,
        engagement: 12.5,
        conversions: 680,
        revenue: 34000
      },
      status: 'active'
    },
    {
      id: '2',
      name: 'Holiday Sales Blitz',
      description: 'High-frequency holiday campaign across all channels',
      channels: ['1', '2', '3'],
      strategy: 'parallel',
      rules: {
        conditions: ['purchase_history', 'browse_behavior'],
        actions: ['personalized_offers', 'urgency_messaging']
      },
      performance: {
        totalReach: 78000,
        engagement: 18.2,
        conversions: 1240,
        revenue: 62000
      },
      status: 'completed'
    }
  ]);

  // Handle channel connection
  const handleConnectChannel = async (channelId: string) => {
    setIsConnecting(true);
    setTimeout(() => {
      setChannels(prev => prev.map(ch =>
        ch.id === channelId
          ? { ...ch, status: 'connected' as const, performance: { ...ch.performance, lastSync: new Date() } }
          : ch
      ));
      setIsConnecting(false);
    }, 2000);
  };

  // Handle channel disconnection
  const handleDisconnectChannel = async (channelId: string) => {
    setChannels(prev => prev.map(ch =>
      ch.id === channelId
        ? { ...ch, status: 'disconnected' as const }
        : ch
    ));
  };

  // Get channel icon
  const getChannelIcon = (type: string) => {
    switch (type) {
      case 'email': return Mail;
      case 'social': return Share2;
      case 'sms': return Phone;
      case 'webhook': return Link;
      case 'api': return Globe;
      default: return Settings;
    }
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'text-[var(--success)]';
      case 'disconnected': return 'text-[var(--ink-ghost)]';
      case 'error': return 'text-[var(--destructive)]';
      case 'pending': return 'text-[var(--warning)]';
      default: return 'text-[var(--ink-muted)]';
    }
  };

  // Render channel integrations
  const renderChannelIntegrations = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Channel Integrations</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Connect and manage your marketing channels
          </p>
        </div>

        <BlueprintButton className="flex items-center gap-2">
          <Plus size={16} />
          Add Channel
        </BlueprintButton>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {channels.map((channel) => {
          const Icon = getChannelIcon(channel.type);
          return (
            <BlueprintCard key={channel.id} className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={cn(
                    "w-12 h-12 rounded-lg flex items-center justify-center",
                    channel.status === 'connected' && "bg-[var(--success-light)]/10",
                    channel.status === 'error' && "bg-[var(--destructive-light)]/10",
                    channel.status === 'disconnected' && "bg-[var(--surface)]",
                    channel.status === 'pending' && "bg-[var(--warning-light)]/10"
                  )}>
                    <Icon size={24} className={cn(
                      channel.status === 'connected' && "text-[var(--success)]",
                      channel.status === 'error' && "text-[var(--destructive)]",
                      channel.status === 'disconnected' && "text-[var(--ink-ghost)]",
                      channel.status === 'pending' && "text-[var(--warning)]"
                    )} />
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-[var(--ink)]">{channel.name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <BlueprintBadge variant="default" size="sm">
                        {channel.provider}
                      </BlueprintBadge>
                      <BlueprintBadge
                        variant={channel.status === 'connected' ? 'success' : channel.status === 'error' ? 'error' : 'default'}
                        size="sm"
                      >
                        {channel.status}
                      </BlueprintBadge>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {channel.status === 'connected' ? (
                    <Wifi size={20} className="text-[var(--success)]" />
                  ) : (
                    <WifiOff size={20} className="text-[var(--ink-ghost)]" />
                  )}

                  <button className="p-1 text-[var(--ink-ghost)] hover:text-[var(--ink)]">
                    <MoreVertical size={16} />
                  </button>
                </div>
              </div>

              {/* Capabilities */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Capabilities</h4>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(channel.capabilities).map(([key, enabled]) => (
                    <div key={key} className="flex items-center gap-2 text-xs">
                      {enabled ? (
                        <CheckCircle size={12} className="text-[var(--success)]" />
                      ) : (
                        <AlertTriangle size={12} className="text-[var(--ink-ghost)]" />
                      )}
                      <span className="capitalize text-[var(--ink)]">{key}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Performance */}
              {channel.status === 'connected' && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Performance</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-[var(--ink-muted)]">Success Rate</span>
                      <div className="font-medium text-[var(--success)]">{channel.performance.successRate}%</div>
                    </div>
                    <div>
                      <span className="text-[var(--ink-muted)]">Response Time</span>
                      <div className="font-medium text-[var(--ink)]">{channel.performance.responseTime}ms</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Usage */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Usage</h4>
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="p-2 bg-[var(--surface)] rounded">
                    <div className="text-sm font-medium text-[var(--ink)]">{channel.usage.messagesSent.toLocaleString()}</div>
                    <div className="text-xs text-[var(--ink-muted)]">Messages</div>
                  </div>
                  <div className="p-2 bg-[var(--surface)] rounded">
                    <div className="text-sm font-medium text-[var(--ink)]">{channel.usage.dataTransferred}GB</div>
                    <div className="text-xs text-[var(--ink-muted)]">Data</div>
                  </div>
                  <div className="p-2 bg-[var(--surface)] rounded">
                    <div className="text-sm font-medium text-[var(--ink)]">{channel.usage.apiCalls}</div>
                    <div className="text-xs text-[var(--ink-muted)]">API Calls</div>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t border-[var(--structure-subtle)]">
                <div className="text-xs text-[var(--ink-muted)]">
                  Last sync {formatDistanceToNow(channel.performance.lastSync, { addSuffix: true })}
                </div>

                <div className="flex items-center gap-2">
                  {channel.status === 'connected' ? (
                    <>
                      <BlueprintButton variant="secondary" size="sm">
                        <RefreshCw size={14} />
                        Sync
                      </BlueprintButton>
                      <BlueprintButton
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDisconnectChannel(channel.id)}
                        className="text-[var(--destructive)] hover:text-[var(--destructive)]"
                      >
                        Disconnect
                      </BlueprintButton>
                    </>
                  ) : (
                    <BlueprintButton
                      size="sm"
                      onClick={() => handleConnectChannel(channel.id)}
                      disabled={isConnecting}
                    >
                      {isConnecting ? 'Connecting...' : 'Connect'}
                    </BlueprintButton>
                  )}
                </div>
              </div>
            </BlueprintCard>
          );
        })}
      </div>
    </div>
  );

  // Render sync rules
  const renderSyncRules = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Sync Rules</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Automate data synchronization between channels
          </p>
        </div>

        <BlueprintButton className="flex items-center gap-2">
          <Plus size={16} />
          Create Rule
        </BlueprintButton>
      </div>

      <div className="space-y-4">
        {syncRules.map((rule) => (
          <BlueprintCard key={rule.id} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-[var(--ink)]">{rule.name}</h3>
                <p className="text-sm text-[var(--ink-muted)]">{rule.description}</p>
              </div>

              <BlueprintBadge
                variant={rule.status === 'active' ? 'success' : 'default'}
                size="sm"
              >
                {rule.status}
              </BlueprintBadge>
            </div>

            {/* Rule Configuration */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-4">
              <div>
                <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Source → Target</h4>
                <div className="flex items-center gap-2">
                  <div className="px-3 py-1 bg-[var(--surface)] rounded text-sm">
                    {channels.find(ch => ch.id === rule.sourceChannel)?.name || 'Unknown'}
                  </div>
                  <ChevronRight size={16} className="text-[var(--ink-ghost)]" />
                  <div className="px-3 py-1 bg-[var(--surface)] rounded text-sm">
                    {channels.find(ch => ch.id === rule.targetChannel)?.name || 'Unknown'}
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Trigger</h4>
                <div className="flex items-center gap-2">
                  <Clock size={16} className="text-[var(--ink-ghost)]" />
                  <span className="text-sm capitalize">{rule.trigger}</span>
                </div>
              </div>
            </div>

            {/* Conditions */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Conditions</h4>
              <div className="space-y-1">
                {rule.conditions.map((condition, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm p-2 bg-[var(--surface)] rounded">
                    <span className="text-[var(--ink)]">{condition.field}</span>
                    <span className="text-[var(--ink-ghost)]">{condition.operator}</span>
                    <span className="text-[var(--blueprint)]">{condition.value}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Actions</h4>
              <div className="flex flex-wrap gap-2">
                {rule.actions.map((action, index) => (
                  <span key={index} className="px-3 py-1 bg-[var(--blueprint-light)]/10 text-[var(--blueprint)] rounded text-sm">
                    {action.type.replace('_', ' ')}
                  </span>
                ))}
              </div>
            </div>

            {/* Schedule */}
            <div className="flex items-center justify-between pt-4 border-t border-[var(--structure-subtle)]">
              <div className="text-sm text-[var(--ink-muted)]">
                Last run {formatDistanceToNow(rule.lastRun, { addSuffix: true })}
                {rule.nextRun && (
                  <span> • Next run {formatDistanceToNow(rule.nextRun, { addSuffix: true })}</span>
                )}
              </div>

              <div className="flex items-center gap-2">
                <BlueprintButton variant="secondary" size="sm">
                  <Eye size={14} />
                  View Logs
                </BlueprintButton>

                <BlueprintButton variant="secondary" size="sm">
                  <Edit size={14} />
                  Edit
                </BlueprintButton>
              </div>
            </div>
          </BlueprintCard>
        ))}
      </div>
    </div>
  );

  // Render cross-channel campaigns
  const renderCrossChannelCampaigns = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Cross-Channel Campaigns</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Coordinate campaigns across multiple channels
          </p>
        </div>

        <BlueprintButton className="flex items-center gap-2">
          <Plus size={16} />
          New Campaign
        </BlueprintButton>
      </div>

      <div className="space-y-4">
        {crossChannelCampaigns.map((campaign) => (
          <BlueprintCard key={campaign.id} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-[var(--ink)]">{campaign.name}</h3>
                <p className="text-sm text-[var(--ink-muted)]">{campaign.description}</p>
              </div>

              <BlueprintBadge
                variant={campaign.status === 'active' ? 'success' : campaign.status === 'completed' ? 'default' : 'default'}
                size="sm"
              >
                {campaign.status}
              </BlueprintBadge>
            </div>

            {/* Channels */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Active Channels</h4>
              <div className="flex flex-wrap gap-2">
                {campaign.channels.map((channelId) => {
                  const channel = channels.find(ch => ch.id === channelId);
                  const Icon = channel ? getChannelIcon(channel.type) : Settings;
                  return (
                    <div key={channelId} className="flex items-center gap-2 px-3 py-1 bg-[var(--surface)] rounded">
                      <Icon size={16} />
                      <span className="text-sm">{channel?.name || 'Unknown'}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Strategy */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Strategy</h4>
              <div className="flex items-center gap-2">
                <Zap size={16} className="text-[var(--blueprint)]" />
                <span className="text-sm capitalize">{campaign.strategy}</span>
              </div>
            </div>

            {/* Performance */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Performance</h4>
              <div className="grid grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-lg font-bold text-[var(--ink)]">
                    {campaign.performance.totalReach.toLocaleString()}
                  </div>
                  <div className="text-xs text-[var(--ink-muted)]">Total Reach</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-[var(--blueprint)]">
                    {campaign.performance.engagement}%
                  </div>
                  <div className="text-xs text-[var(--ink-muted)]">Engagement</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-[var(--success)]">
                    {campaign.performance.conversions}
                  </div>
                  <div className="text-xs text-[var(--ink-muted)]">Conversions</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-[var(--success)]">
                    ${campaign.performance.revenue.toLocaleString()}
                  </div>
                  <div className="text-xs text-[var(--ink-muted)]">Revenue</div>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-[var(--structure-subtle)]">
              <div className="flex items-center gap-2">
                <BlueprintButton variant="secondary" size="sm">
                  <BarChart3 size={14} />
                  Analytics
                </BlueprintButton>

                <BlueprintButton variant="secondary" size="sm">
                  <Edit size={14} />
                  Edit Campaign
                </BlueprintButton>

                <BlueprintButton variant="secondary" size="sm">
                  <Copy size={14} />
                  Duplicate
                </BlueprintButton>
              </div>
            </div>
          </BlueprintCard>
        ))}
      </div>
    </div>
  );

  // Render analytics
  const renderAnalytics = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Multi-Channel Analytics</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Comprehensive analytics across all integrated channels
          </p>
        </div>

        <div className="flex items-center gap-2">
          <BlueprintButton variant="secondary" className="flex items-center gap-2">
            <Download size={16} />
            Export
          </BlueprintButton>

          <BlueprintButton className="flex items-center gap-2">
            <RefreshCw size={16} />
            Refresh
          </BlueprintButton>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Channel Performance */}
        <BlueprintCard className="p-6">
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Channel Performance</h3>

          <div className="space-y-4">
            {channels.filter(ch => ch.status === 'connected').map((channel) => {
              const Icon = getChannelIcon(channel.type);
              return (
                <div key={channel.id} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Icon size={20} className="text-[var(--ink-ghost)]" />
                    <div>
                      <div className="text-sm font-medium text-[var(--ink)]">{channel.name}</div>
                      <div className="text-xs text-[var(--ink-muted)]">{channel.provider}</div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-sm font-medium text-[var(--success)]">
                      {channel.performance.successRate}%
                    </div>
                    <div className="text-xs text-[var(--ink-muted)]">Success Rate</div>
                  </div>
                </div>
              );
            })}
          </div>
        </BlueprintCard>

        {/* Sync Activity */}
        <BlueprintCard className="p-6">
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Sync Activity</h3>

          <div className="space-y-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-[var(--blueprint)]">
                {syncRules.filter(r => r.status === 'active').length}
              </div>
              <div className="text-sm text-[var(--ink-muted)]">Active Rules</div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-[var(--ink-muted)]">Last 24h</span>
                <span className="text-[var(--ink)]">142 syncs</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-[var(--ink-muted)]">Success Rate</span>
                <span className="text-[var(--success)]">96.8%</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-[var(--ink-muted)]">Avg Time</span>
                <span className="text-[var(--ink)]">324ms</span>
              </div>
            </div>
          </div>
        </BlueprintCard>

        {/* Cross-Channel Impact */}
        <BlueprintCard className="p-6">
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Cross-Channel Impact</h3>

          <div className="space-y-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-[var(--success)]">
                +28%
              </div>
              <div className="text-sm text-[var(--ink-muted)]">Conversion Lift</div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-[var(--ink-muted)]">Reach</span>
                <span className="text-[var(--ink)]">123K users</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-[var(--ink-muted)]">Engagement</span>
                <span className="text-[var(--blueprint)]">15.2%</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-[var(--ink-muted)]">Revenue</span>
                <span className="text-[var(--success)]">$96K</span>
              </div>
            </div>
          </div>
        </BlueprintCard>
      </div>

      {/* Detailed Analytics */}
      <BlueprintCard className="p-6">
        <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Channel Interaction Matrix</h3>

        <div className="h-64 bg-[var(--surface)] rounded-lg flex items-center justify-center">
          <div className="text-center">
            <BarChart3 size={48} className="text-[var(--blueprint)] mx-auto mb-2" />
            <p className="text-sm text-[var(--ink)]">Channel interaction heatmap</p>
            <p className="text-xs text-[var(--ink-muted)]">Shows cross-channel performance and correlations</p>
          </div>
        </div>
      </BlueprintCard>
    </div>
  );

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-[var(--structure-subtle)]">
        <div>
          <h1 className="text-2xl font-bold text-[var(--ink)]">Multi-Channel Integration</h1>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Connect and synchronize all your marketing channels
          </p>
        </div>

        <div className="flex items-center gap-2">
          <BlueprintButton variant="secondary" className="flex items-center gap-2">
            <Settings size={16} />
            Settings
          </BlueprintButton>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-6 px-6 border-b border-[var(--structure-subtle)]">
        {[
          { id: 'channels', label: 'Channels', icon: Globe },
          { id: 'sync', label: 'Sync Rules', icon: RefreshCw },
          { id: 'campaigns', label: 'Campaigns', icon: Zap },
          { id: 'analytics', label: 'Analytics', icon: BarChart3 }
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
        {activeTab === 'channels' && renderChannelIntegrations()}
        {activeTab === 'sync' && renderSyncRules()}
        {activeTab === 'campaigns' && renderCrossChannelCampaigns()}
        {activeTab === 'analytics' && renderAnalytics()}
      </div>
    </div>
  );
}
