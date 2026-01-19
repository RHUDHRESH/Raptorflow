import React, { useState, useEffect } from 'react';
import {
  Users,
  Target,
  TrendingUp,
  Search,
  Filter,
  Plus,
  Edit,
  Trash2,
  Download,
  Upload,
  Copy,
  Eye,
  EyeOff,
  Settings,
  Play,
  Pause,
  RefreshCw,
  BarChart3,
  PieChart,
  LineChart,
  Activity,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  ChevronRight,
  ChevronDown,
  Zap,
  Brain,
  Globe,
  MapPin,
  Calendar,
  DollarSign,
  ShoppingBag,
  Heart,
  Star,
  Award,
  Shield,
  Flag,
  Layers,
  Database,
  FileText,
  Mail,
  Phone,
  MessageSquare,
  Webhook
} from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { useEnhancedCampaignStore } from '@/stores/enhancedCampaignStore';
import { format } from 'date-fns';
import { formatDistanceToNow } from 'date-fns/formatDistanceToNow';
import { cn } from '@/lib/utils';

// Types
interface Segment {
  id: string;
  name: string;
  description: string;
  type: 'demographic' | 'behavioral' | 'psychographic' | 'geographic' | 'custom';
  status: 'active' | 'inactive' | 'building' | 'error';
  size: number;
  criteria: SegmentCriteria[];
  performance: SegmentPerformance;
  createdAt: Date;
  updatedAt: Date;
  lastRefreshed?: Date;
  lookalike?: LookalikeData;
}

interface SegmentCriteria {
  id: string;
  field: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than' | 'between' | 'in' | 'not_in';
  value: any;
  weight?: number;
}

interface SegmentPerformance {
  engagement: number;
  conversion: number;
  retention: number;
  revenue: number;
  score: number;
  trend: 'up' | 'down' | 'stable';
}

interface LookalikeData {
  sourceSegment: string;
  similarity: number;
  size: number;
  accuracy: number;
  countries: string[];
}

interface BehavioralPattern {
  id: string;
  name: string;
  pattern: string;
  frequency: number;
  conversion: number;
  lastSeen: Date;
}

interface TargetingRule {
  id: string;
  name: string;
  conditions: SegmentCriteria[];
  actions: TargetingAction[];
  priority: number;
  active: boolean;
}

interface TargetingAction {
  type: 'show_campaign' | 'hide_campaign' | 'modify_content' | 'send_email' | 'trigger_webhook';
  parameters: Record<string, any>;
}

// Mock data
const mockSegments: Segment[] = [
  {
    id: 'seg_1',
    name: 'High Value Customers',
    description: 'Customers with lifetime value > $10,000 and frequent purchases',
    type: 'behavioral',
    status: 'active',
    size: 12543,
    criteria: [
      { id: 'c1', field: 'lifetime_value', operator: 'greater_than', value: 10000, weight: 0.4 },
      { id: 'c2', field: 'purchase_frequency', operator: 'greater_than', value: 5, weight: 0.3 },
      { id: 'c3', field: 'avg_order_value', operator: 'greater_than', value: 200, weight: 0.3 }
    ],
    performance: {
      engagement: 85,
      conversion: 12,
      retention: 78,
      revenue: 456000,
      score: 92,
      trend: 'up'
    },
    createdAt: new Date('2024-01-15'),
    updatedAt: new Date('2024-01-20'),
    lastRefreshed: new Date('2024-01-20T10:30:00')
  },
  {
    id: 'seg_2',
    name: 'Cart Abandoners',
    description: 'Users who added items to cart but didn\'t complete purchase in last 7 days',
    type: 'behavioral',
    status: 'active',
    size: 8932,
    criteria: [
      { id: 'c4', field: 'cart_items', operator: 'greater_than', value: 0, weight: 0.5 },
      { id: 'c5', field: 'last_purchase', operator: 'greater_than', value: 7, weight: 0.3 },
      { id: 'c6', field: 'session_count', operator: 'greater_than', value: 2, weight: 0.2 }
    ],
    performance: {
      engagement: 72,
      conversion: 8,
      retention: 65,
      revenue: 234000,
      score: 78,
      trend: 'stable'
    },
    createdAt: new Date('2024-01-10'),
    updatedAt: new Date('2024-01-18'),
    lastRefreshed: new Date('2024-01-20T09:15:00')
  },
  {
    id: 'seg_3',
    name: 'New Subscribers',
    description: 'Users who subscribed in last 30 days but haven\'t made first purchase',
    type: 'demographic',
    status: 'active',
    size: 15678,
    criteria: [
      { id: 'c7', field: 'subscription_date', operator: 'greater_than', value: 30, weight: 0.4 },
      { id: 'c8', field: 'purchase_count', operator: 'equals', value: 0, weight: 0.6 }
    ],
    performance: {
      engagement: 68,
      conversion: 15,
      retention: 45,
      revenue: 123000,
      score: 71,
      trend: 'up'
    },
    createdAt: new Date('2024-01-05'),
    updatedAt: new Date('2024-01-19'),
    lastRefreshed: new Date('2024-01-20T11:45:00')
  },
  {
    id: 'seg_4',
    name: 'Lookalike - High Value',
    description: 'Lookalike audience based on high value customers',
    type: 'custom',
    status: 'building',
    size: 25000,
    criteria: [],
    performance: {
      engagement: 0,
      conversion: 0,
      retention: 0,
      revenue: 0,
      score: 0,
      trend: 'stable'
    },
    createdAt: new Date('2024-01-18'),
    updatedAt: new Date('2024-01-18'),
    lookalike: {
      sourceSegment: 'seg_1',
      similarity: 85,
      size: 25000,
      accuracy: 78,
      countries: ['US', 'CA', 'GB', 'AU']
    }
  }
];

const mockBehavioralPatterns: BehavioralPattern[] = [
  {
    id: 'bp1',
    name: 'Weekend Shoppers',
    pattern: 'Visits site on weekends, adds multiple items to cart',
    frequency: 45,
    conversion: 12,
    lastSeen: new Date('2024-01-20T18:30:00')
  },
  {
    id: 'bp2',
    name: 'Price Sensitive',
    pattern: 'Uses discount codes, compares prices, waits for sales',
    frequency: 38,
    conversion: 8,
    lastSeen: new Date('2024-01-20T14:22:00')
  },
  {
    id: 'bp3',
    name: 'Brand Loyalists',
    pattern: 'Always buys same brand, writes reviews, refers friends',
    frequency: 25,
    conversion: 28,
    lastSeen: new Date('2024-01-20T16:45:00')
  }
];

const mockTargetingRules: TargetingRule[] = [
  {
    id: 'tr1',
    name: 'High Value Priority',
    conditions: [
      { id: 'tc1', field: 'segment_id', operator: 'in', value: ['seg_1'] },
      { id: 'tc2', field: 'device_type', operator: 'equals', value: 'mobile' }
    ],
    actions: [
      { type: 'show_campaign', parameters: { campaign_id: 'camp_premium' } },
      { type: 'modify_content', parameters: { discount: 15 } }
    ],
    priority: 1,
    active: true
  },
  {
    id: 'tr2',
    name: 'Cart Recovery',
    conditions: [
      { id: 'tc3', field: 'segment_id', operator: 'in', value: ['seg_2'] },
      { id: 'tc4', field: 'hours_since_abandon', operator: 'less_than', value: 24 }
    ],
    actions: [
      { type: 'send_email', parameters: { template: 'cart_recovery' } },
      { type: 'show_campaign', parameters: { campaign_id: 'camp_recovery' } }
    ],
    priority: 2,
    active: true
  }
];

export default function AdvancedSegmentation() {
  const [activeTab, setActiveTab] = useState<'segments' | 'patterns' | 'lookalike' | 'targeting'>('segments');
  const [selectedSegment, setSelectedSegment] = useState<Segment | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showLookalakeModal, setShowLookalakeModal] = useState(false);
  const [refreshingSegments, setRefreshingSegments] = useState<string[]>([]);
  const { campaigns } = useEnhancedCampaignStore();

  const filteredSegments = mockSegments.filter(segment => {
    const matchesSearch = segment.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      segment.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'all' || segment.type === filterType;
    return matchesSearch && matchesType;
  });

  const handleRefreshSegment = async (segmentId: string) => {
    setRefreshingSegments(prev => [...prev, segmentId]);
    // Simulate refresh
    await new Promise(resolve => setTimeout(resolve, 2000));
    setRefreshingSegments(prev => prev.filter(id => id !== segmentId));
  };

  const getStatusColor = (status: Segment['status']) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'building': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getTypeIcon = (type: Segment['type']) => {
    switch (type) {
      case 'demographic': return <Users size={16} />;
      case 'behavioral': return <Activity size={16} />;
      case 'psychographic': return <Brain size={16} />;
      case 'geographic': return <MapPin size={16} />;
      case 'custom': return <Settings size={16} />;
      default: return <Users size={16} />;
    }
  };

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up': return <TrendingUp size={14} className="text-green-500" />;
      case 'down': return <TrendingUp size={14} className="text-red-500 rotate-180" />;
      case 'stable': return <Activity size={14} className="text-blue-500" />;
      default: return <Activity size={14} />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--ink)]">Advanced Segmentation</h1>
          <p className="text-[var(--ink-muted)] mt-1">
            Dynamic audience segmentation and behavioral targeting
          </p>
        </div>
        <div className="flex items-center gap-3">
          <BlueprintButton variant="secondary" size="sm">
            <Upload size={16} />
            Import
          </BlueprintButton>
          <BlueprintButton variant="secondary" size="sm">
            <Download size={16} />
            Export
          </BlueprintButton>
          <BlueprintButton variant="blueprint" onClick={() => setShowCreateModal(true)}>
            <Plus size={16} />
            Create Segment
          </BlueprintButton>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-[var(--ink-muted)]">Total Segments</p>
              <p className="text-2xl font-bold text-[var(--ink)] mt-1">{mockSegments.length}</p>
            </div>
            <div className="p-2 bg-blue-100 rounded-lg">
              <Layers size={20} className="text-blue-600" />
            </div>
          </div>
        </BlueprintCard>

        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-[var(--ink-muted)]">Total Audience</p>
              <p className="text-2xl font-bold text-[var(--ink)] mt-1">
                {mockSegments.reduce((sum, seg) => sum + seg.size, 0).toLocaleString()}
              </p>
            </div>
            <div className="p-2 bg-green-100 rounded-lg">
              <Users size={20} className="text-green-600" />
            </div>
          </div>
        </BlueprintCard>

        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-[var(--ink-muted)]">Avg Performance</p>
              <p className="text-2xl font-bold text-[var(--ink)] mt-1">
                {Math.round(mockSegments.reduce((sum, seg) => sum + seg.performance.score, 0) / mockSegments.length)}%
              </p>
            </div>
            <div className="p-2 bg-purple-100 rounded-lg">
              <Target size={20} className="text-purple-600" />
            </div>
          </div>
        </BlueprintCard>

        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-[var(--ink-muted)]">Active Rules</p>
              <p className="text-2xl font-bold text-[var(--ink)] mt-1">{mockTargetingRules.filter(r => r.active).length}</p>
            </div>
            <div className="p-2 bg-orange-100 rounded-lg">
              <Settings size={20} className="text-orange-600" />
            </div>
          </div>
        </BlueprintCard>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 bg-[var(--structure-subtle)] p-1 rounded-lg">
        {[
          { id: 'segments', label: 'Segments', icon: <Users size={16} /> },
          { id: 'patterns', label: 'Behavioral Patterns', icon: <Activity size={16} /> },
          { id: 'lookalike', label: 'Lookalike Audiences', icon: <Target size={16} /> },
          { id: 'targeting', label: 'Targeting Rules', icon: <Settings size={16} /> }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'bg-[var(--paper)] text-[var(--ink)] shadow-sm'
                : 'text-[var(--ink-muted)] hover:text-[var(--ink)]'
            )}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Search and Filters */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--ink-muted)]" />
            <input
              type="text"
              placeholder="Search segments..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 border border-[var(--structure-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--blueprint)] focus:border-transparent"
            />
          </div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-2 border border-[var(--structure-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--blueprint)] focus:border-transparent"
          >
            <option value="all">All Types</option>
            <option value="demographic">Demographic</option>
            <option value="behavioral">Behavioral</option>
            <option value="psychographic">Psychographic</option>
            <option value="geographic">Geographic</option>
            <option value="custom">Custom</option>
          </select>
        </div>
        <div className="flex items-center gap-2">
          <BlueprintButton variant="secondary" size="sm">
            <Filter size={16} />
            Filters
          </BlueprintButton>
          <BlueprintButton variant="secondary" size="sm">
            <RefreshCw size={16} />
            Refresh All
          </BlueprintButton>
        </div>
      </div>

      {/* Segments Tab */}
      {activeTab === 'segments' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Segments List */}
          <div className="lg:col-span-2 space-y-4">
            {filteredSegments.map(segment => (
              <BlueprintCard key={segment.id} className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="flex items-center gap-2">
                        {getTypeIcon(segment.type)}
                        <h3 className="font-semibold text-[var(--ink)]">{segment.name}</h3>
                      </div>
                      <BlueprintBadge variant={getStatusColor(segment.status)}>
                        {segment.status}
                      </BlueprintBadge>
                    </div>
                    <p className="text-sm text-[var(--ink-muted)] mb-4">{segment.description}</p>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div>
                        <p className="text-xs text-[var(--ink-muted)]">Size</p>
                        <p className="font-semibold text-[var(--ink)]">{segment.size.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[var(--ink-muted)]">Performance</p>
                        <div className="flex items-center gap-1">
                          <p className="font-semibold text-[var(--ink)]">{segment.performance.score}%</p>
                          {getTrendIcon(segment.performance.trend)}
                        </div>
                      </div>
                      <div>
                        <p className="text-xs text-[var(--ink-muted)]">Conversion</p>
                        <p className="font-semibold text-[var(--ink)]">{segment.performance.conversion}%</p>
                      </div>
                      <div>
                        <p className="text-xs text-[var(--ink-muted)]">Revenue</p>
                        <p className="font-semibold text-[var(--ink)]">${segment.performance.revenue.toLocaleString()}</p>
                      </div>
                    </div>

                    {segment.lookalike && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Target size={16} className="text-blue-600" />
                          <span className="text-sm font-medium text-blue-800">Lookalike Audience</span>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-xs text-blue-700">
                          <div>Source: {segment.lookalike.sourceSegment}</div>
                          <div>Similarity: {segment.lookalike.similarity}%</div>
                          <div>Accuracy: {segment.lookalike.accuracy}%</div>
                          <div>Countries: {segment.lookalike.countries.join(', ')}</div>
                        </div>
                      </div>
                    )}

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 text-xs text-[var(--ink-muted)]">
                        <span>Created {formatDistanceToNow(segment.createdAt, { addSuffix: true })}</span>
                        {segment.lastRefreshed && (
                          <span>Updated {formatDistanceToNow(segment.lastRefreshed, { addSuffix: true })}</span>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <BlueprintButton variant="secondary" size="sm">
                          <Eye size={14} />
                          View
                        </BlueprintButton>
                        <BlueprintButton variant="secondary" size="sm">
                          <Edit size={14} />
                          Edit
                        </BlueprintButton>
                        <BlueprintButton
                          variant="secondary"
                          size="sm"
                          onClick={() => handleRefreshSegment(segment.id)}
                          disabled={refreshingSegments.includes(segment.id)}
                        >
                          <RefreshCw size={14} className={refreshingSegments.includes(segment.id) ? 'animate-spin' : ''} />
                          Refresh
                        </BlueprintButton>
                        <BlueprintButton variant="secondary" size="sm">
                          <Copy size={14} />
                          Clone
                        </BlueprintButton>
                      </div>
                    </div>
                  </div>
                </div>
              </BlueprintCard>
            ))}
          </div>

          {/* Segment Details */}
          <div className="space-y-4">
            {selectedSegment ? (
              <BlueprintCard className="p-6">
                <h3 className="font-semibold text-[var(--ink)] mb-4">Segment Details</h3>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-[var(--ink-muted)] mb-2">Criteria</p>
                    <div className="space-y-2">
                      {selectedSegment.criteria.map(criteria => (
                        <div key={criteria.id} className="flex items-center justify-between p-2 bg-[var(--structure-subtle)] rounded">
                          <div className="flex-1">
                            <p className="text-sm font-medium">{criteria.field}</p>
                            <p className="text-xs text-[var(--ink-muted)]">
                              {criteria.operator} {criteria.value}
                            </p>
                          </div>
                          {criteria.weight && (
                            <BlueprintBadge variant="default" size="sm">
                              {Math.round(criteria.weight * 100)}%
                            </BlueprintBadge>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-[var(--ink-muted)] mb-2">Performance Breakdown</p>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Engagement</span>
                        <span className="text-sm font-medium">{selectedSegment.performance.engagement}%</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Conversion</span>
                        <span className="text-sm font-medium">{selectedSegment.performance.conversion}%</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Retention</span>
                        <span className="text-sm font-medium">{selectedSegment.performance.retention}%</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <BlueprintButton variant="blueprint" size="sm" className="flex-1">
                      <Target size={14} />
                      Apply to Campaign
                    </BlueprintButton>
                    <BlueprintButton variant="secondary" size="sm">
                      <Download size={14} />
                    </BlueprintButton>
                  </div>
                </div>
              </BlueprintCard>
            ) : (
              <BlueprintCard className="p-6 text-center">
                <Users size={48} className="mx-auto text-[var(--ink-muted)] mb-4" />
                <p className="text-[var(--ink-muted)]">Select a segment to view details</p>
              </BlueprintCard>
            )}

            {/* Quick Actions */}
            <BlueprintCard className="p-6">
              <h3 className="font-semibold text-[var(--ink)] mb-4">Quick Actions</h3>
              <div className="space-y-2">
                <BlueprintButton variant="secondary" size="sm" className="w-full justify-start" onClick={() => setShowLookalakeModal(true)}>
                  <Target size={16} />
                  Create Lookalike
                </BlueprintButton>
                <BlueprintButton variant="secondary" size="sm" className="w-full justify-start">
                  <Brain size={16} />
                  AI Insights
                </BlueprintButton>
                <BlueprintButton variant="secondary" size="sm" className="w-full justify-start">
                  <BarChart3 size={16} />
                  Performance Analysis
                </BlueprintButton>
                <BlueprintButton variant="secondary" size="sm" className="w-full justify-start">
                  <FileText size={16} />
                  Export Report
                </BlueprintButton>
              </div>
            </BlueprintCard>
          </div>
        </div>
      )}

      {/* Behavioral Patterns Tab */}
      {activeTab === 'patterns' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {mockBehavioralPatterns.map(pattern => (
            <BlueprintCard key={pattern.id} className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Activity size={20} className="text-purple-600" />
                  <h3 className="font-semibold text-[var(--ink)]">{pattern.name}</h3>
                </div>
                <BlueprintBadge variant="blueprint" size="sm">
                  Behavioral
                </BlueprintBadge>
              </div>

              <p className="text-sm text-[var(--ink-muted)] mb-4">{pattern.pattern}</p>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-xs text-[var(--ink-muted)]">Conversion</p>
                  <p className="font-semibold text-[var(--ink)]">{pattern.conversion}%</p>
                </div>
                <div>
                  <p className="text-xs text-[var(--ink-muted)]">Last Seen</p>
                  <p className="font-semibold text-[var(--ink)]">
                    {formatDistanceToNow(pattern.lastSeen, { addSuffix: true })}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <BlueprintButton variant="blueprint" size="sm" className="flex-1">
                  <Target size={14} />
                  Create Segment
                </BlueprintButton>
                <BlueprintButton variant="secondary" size="sm">
                  <Eye size={14} />
                </BlueprintButton>
              </div>
            </BlueprintCard>
          ))}
        </div>
      )}

      {/* Lookalike Audiences Tab */}
      {activeTab === 'lookalike' && (
        <div className="text-center py-12">
          <Target size={48} className="mx-auto text-[var(--ink-muted)] mb-4" />
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-2">Lookalike Audience Builder</h3>
          <p className="text-[var(--ink-muted)] mb-6">
            Create high-converting lookalike audiences based on your best customers
          </p>
          <BlueprintButton variant="blueprint" onClick={() => setShowLookalakeModal(true)}>
            <Plus size={16} />
            Create Lookalike Audience
          </BlueprintButton>
        </div>
      )}

      {/* Targeting Rules Tab */}
      {activeTab === 'targeting' && (
        <div className="space-y-4">
          {mockTargetingRules.map(rule => (
            <BlueprintCard key={rule.id} className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-4">
                    <h3 className="font-semibold text-[var(--ink)]">{rule.name}</h3>
                    <BlueprintBadge variant={rule.active ? 'success' : 'default'}>
                      {rule.active ? 'Active' : 'Inactive'}
                    </BlueprintBadge>
                    <BlueprintBadge variant="default" size="sm">
                      Priority {rule.priority}
                    </BlueprintBadge>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <p className="text-sm font-medium text-[var(--ink)] mb-2">Conditions</p>
                      <div className="space-y-1">
                        {rule.conditions.map(condition => (
                          <div key={condition.id} className="text-sm text-[var(--ink-muted)]">
                            {condition.field} {condition.operator} {condition.value}
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <p className="text-sm font-medium text-[var(--ink)] mb-2">Actions</p>
                      <div className="space-y-1">
                        {rule.actions.map((action, index) => (
                          <div key={index} className="text-sm text-[var(--ink-muted)]">
                            {action.type}: {JSON.stringify(action.parameters)}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 ml-4">
                  <BlueprintButton variant="secondary" size="sm">
                    {rule.active ? <Pause size={14} /> : <Play size={14} />}
                  </BlueprintButton>
                  <BlueprintButton variant="secondary" size="sm">
                    <Edit size={14} />
                  </BlueprintButton>
                </div>
              </div>
            </BlueprintCard>
          ))}
        </div>
      )}
    </div>
  );
}
