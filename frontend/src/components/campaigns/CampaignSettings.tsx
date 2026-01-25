"use client";

import { useState, useEffect } from 'react';
import {
  Settings,
  Bell,
  Shield,
  Users,
  Globe,
  Clock,
  DollarSign,
  BarChart3,
  Zap,
  Save,
  X,
  Plus,
  Trash2,
  Edit,
  Copy,
  Download,
  Upload,
  AlertTriangle,
  CheckCircle,
  Info
} from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { useEnhancedCampaignStore } from '@/stores/enhancedCampaignStore';
import { format, formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';

interface CampaignSettingsProps {
  campaignId: string;
  onSave?: () => void;
  onClose?: () => void;
}

interface NotificationRule {
  id: string;
  name: string;
  event: string;
  channels: ('email' | 'push' | 'sms' | 'webhook')[];
  recipients: string[];
  enabled: boolean;
  conditions?: {
    metric?: string;
    operator?: string;
    value?: any;
  }[];
}

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: 'owner' | 'admin' | 'editor' | 'viewer';
  permissions: string[];
  addedAt: Date;
}

interface Integration {
  id: string;
  name: string;
  type: 'crm' | 'email' | 'analytics' | 'social' | 'webhook';
  status: 'connected' | 'disconnected' | 'error';
  config?: Record<string, any>;
  lastSync?: Date;
}

export function CampaignSettings({ campaignId, onSave, onClose }: CampaignSettingsProps) {
  const campaign = useEnhancedCampaignStore(state => state.campaigns[campaignId]);
  const updateCampaign = useEnhancedCampaignStore(state => state.updateCampaign);

  const [activeTab, setActiveTab] = useState<'general' | 'notifications' | 'team' | 'integrations' | 'advanced'>('general');
  const [hasChanges, setHasChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Settings state
  const [generalSettings, setGeneralSettings] = useState({
    name: campaign?.name || '',
    description: campaign?.description || '',
    timezone: 'UTC',
    currency: 'USD',
    autoOptimization: campaign?.settings?.autoOptimization || false,
    abTesting: campaign?.settings?.abTesting || false,
    budgetAlerts: true,
    performanceThresholds: {
      minROI: 200,
      maxCAC: 50,
      minConversionRate: 2.5
    }
  });

  const [notificationRules, setNotificationRules] = useState<NotificationRule[]>([
    {
      id: '1',
      name: 'Budget Alert',
      event: 'budget_threshold',
      channels: ['email'],
      recipients: ['admin@example.com'],
      enabled: true,
      conditions: [
        { metric: 'budget_spent', operator: 'greater_than', value: 80 }
      ]
    },
    {
      id: '2',
      name: 'Performance Drop',
      event: 'performance_decline',
      channels: ['email', 'push'],
      recipients: ['admin@example.com'],
      enabled: true,
      conditions: [
        { metric: 'roi', operator: 'less_than', value: 150 }
      ]
    }
  ]);

  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([
    {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      role: 'owner',
      permissions: ['all'],
      addedAt: new Date('2024-01-01')
    },
    {
      id: '2',
      name: 'Jane Smith',
      email: 'jane@example.com',
      role: 'admin',
      permissions: ['edit', 'view', 'execute'],
      addedAt: new Date('2024-01-15')
    }
  ]);

  const [integrations, setIntegrations] = useState<Integration[]>([
    {
      id: '1',
      name: 'Salesforce',
      type: 'crm',
      status: 'connected',
      lastSync: new Date()
    },
    {
      id: '2',
      name: 'Mailchimp',
      type: 'email',
      status: 'connected',
      lastSync: new Date()
    },
    {
      id: '3',
      name: 'Google Analytics',
      type: 'analytics',
      status: 'error'
    }
  ]);

  if (!campaign) return null;

  // Handle save
  const handleSave = async () => {
    setIsSaving(true);
    try {
      await updateCampaign({
        id: campaign.id,
        name: generalSettings.name,
        description: generalSettings.description
      });
      setHasChanges(false);
      onSave?.();
    } finally {
      setIsSaving(false);
    }
  };

  // Add notification rule
  const addNotificationRule = () => {
    const newRule: NotificationRule = {
      id: Date.now().toString(),
      name: 'New Rule',
      event: 'custom',
      channels: ['email'],
      recipients: [],
      enabled: true
    };
    setNotificationRules(prev => [...prev, newRule]);
    setHasChanges(true);
  };

  // Delete notification rule
  const deleteNotificationRule = (id: string) => {
    setNotificationRules(prev => prev.filter(rule => rule.id !== id));
    setHasChanges(true);
  };

  // Add team member
  const addTeamMember = () => {
    const newMember: TeamMember = {
      id: Date.now().toString(),
      name: 'New Member',
      email: '',
      role: 'viewer',
      permissions: ['view'],
      addedAt: new Date()
    };
    setTeamMembers(prev => [...prev, newMember]);
    setHasChanges(true);
  };

  // Delete team member
  const deleteTeamMember = (id: string) => {
    setTeamMembers(prev => prev.filter(member => member.id !== id));
    setHasChanges(true);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-[var(--structure-subtle)]">
        <div>
          <h1 className="text-2xl font-bold text-[var(--ink)]">Campaign Settings</h1>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            {campaign.name} • Configure campaign preferences
          </p>
        </div>

        <div className="flex items-center gap-2">
          {hasChanges && (
            <div className="flex items-center gap-2 text-sm text-[var(--warning)]">
              <Info size={16} />
              Unsaved changes
            </div>
          )}

          <BlueprintButton
            variant="secondary"
            size="sm"
            onClick={onClose}
          >
            Cancel
          </BlueprintButton>

          <BlueprintButton
            size="sm"
            onClick={handleSave}
            disabled={!hasChanges || isSaving}
            className="flex items-center gap-2"
          >
            <Save size={16} />
            {isSaving ? 'Saving...' : 'Save Changes'}
          </BlueprintButton>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-6 px-6 border-b border-[var(--structure-subtle)]">
        {[
          { id: 'general', label: 'General', icon: Settings },
          { id: 'notifications', label: 'Notifications', icon: Bell },
          { id: 'team', label: 'Team', icon: Users },
          { id: 'integrations', label: 'Integrations', icon: Zap },
          { id: 'advanced', label: 'Advanced', icon: Shield }
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
        <BlueprintCard className="p-6">
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Basic Information</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                Campaign Name
              </label>
              <input
                type="text"
                value={generalSettings.name}
                onChange={(e) => {
                  setGeneralSettings(prev => ({ ...prev, name: e.target.value }));
                  setHasChanges(true);
                }}
                className="w-full px-3 py-2 bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                Description
              </label>
              <textarea
                value={generalSettings.description}
                onChange={(e) => {
                  setGeneralSettings(prev => ({ ...prev, description: e.target.value }));
                  setHasChanges(true);
                }}
                rows={3}
                className="w-full px-3 py-2 bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)] resize-none"
              />
            </div>
          </div>
        </BlueprintCard>
      </div>
    </div>
  );
}
