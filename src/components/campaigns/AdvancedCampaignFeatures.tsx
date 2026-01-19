"use client";

import { useState, useEffect } from 'react';
import {
  Copy,
  Edit,
  Trash2,
  Plus,
  Search,
  Filter,
  Download,
  Upload,
  Star,
  Clock,
  Users,
  TrendingUp,
  Zap,
  Globe,
  Target,
  BarChart3,
  Calendar,
  ChevronDown,
  ChevronRight,
  Eye,
  Play,
  Pause,
  Settings,
  MoreVertical,
  X
} from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { useEnhancedCampaignStore } from '@/stores/enhancedCampaignStore';
import { Campaign } from '@/types/campaign';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';
import { formatDistanceToNow } from 'date-fns/formatDistanceToNow';

interface CampaignTemplate {
  id: string;
  name: string;
  description: string;
  category: 'product-launch' | 'lead-generation' | 'brand-awareness' | 'event-promotion' | 'content-marketing';
  objective: string;
  targetAudience: string;
  estimatedDuration: string;
  budget: {
    min: number;
    max: number;
    currency: string;
  };
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  components: {
    moves: number;
    plays: number;
    automations: number;
  };
  preview: {
    thumbnail?: string;
    steps: string[];
  };
  usage: {
    downloads: number;
    rating: number;
    reviews: number;
    lastUpdated: Date;
  };
  tags: string[];
  isPremium: boolean;
  createdBy: string;
}

interface CampaignVersion {
  id: string;
  version: string;
  name: string;
  description: string;
  changes: string[];
  createdAt: Date;
  createdBy: string;
  isActive: boolean;
}

interface CampaignClone {
  id: string;
  originalCampaignId: string;
  name: string;
  description: string;
  cloneType: 'exact' | 'template' | 'custom';
  customizations: {
    budget?: number;
    timeline?: string;
    audience?: string;
    moves?: string[];
  };
  createdAt: Date;
  status: 'draft' | 'active' | 'archived';
}

export function AdvancedCampaignFeatures() {
  const campaigns = useEnhancedCampaignStore(state => state.campaigns);
  const createCampaign = useEnhancedCampaignStore(state => state.createCampaign);
  const duplicateCampaign = useEnhancedCampaignStore(state => state.duplicateCampaign);

  const [activeTab, setActiveTab] = useState<'templates' | 'cloning' | 'versioning' | 'orchestration'>('templates');
  const [selectedTemplate, setSelectedTemplate] = useState<CampaignTemplate | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showPreview, setShowPreview] = useState(false);

  // Mock templates data
  const templates: CampaignTemplate[] = [
    {
      id: 'template-1',
      name: 'SaaS Product Launch',
      description: 'Complete product launch sequence with pre-launch buzz, launch day coordination, and post-launch optimization',
      category: 'product-launch',
      objective: 'Launch new software product',
      targetAudience: 'B2B SaaS companies',
      estimatedDuration: '6 weeks',
      budget: { min: 5000, max: 50000, currency: 'USD' },
      difficulty: 'intermediate',
      components: { moves: 12, plays: 4, automations: 8 },
      preview: {
        steps: ['Pre-launch', 'Launch Day', 'Post-launch', 'Optimization']
      },
      usage: {
        downloads: 1250,
        rating: 4.8,
        reviews: 89,
        lastUpdated: new Date('2024-01-15')
      },
      tags: ['saas', 'product-launch', 'b2b'],
      isPremium: false,
      createdBy: 'Marketing Team'
    },
    {
      id: 'template-2',
      name: 'E-commerce Holiday Campaign',
      description: 'Multi-channel holiday shopping campaign with email, social, and paid advertising coordination',
      category: 'lead-generation',
      objective: 'Drive holiday sales',
      targetAudience: 'E-commerce retailers',
      estimatedDuration: '8 weeks',
      budget: { min: 10000, max: 100000, currency: 'USD' },
      difficulty: 'advanced',
      components: { moves: 18, plays: 6, automations: 12 },
      preview: {
        steps: ['Black Friday', 'Cyber Monday', 'Holiday Weekend', 'New Year']
      },
      usage: {
        downloads: 890,
        rating: 4.6,
        reviews: 67,
        lastUpdated: new Date('2024-01-10')
      },
      tags: ['ecommerce', 'holiday', 'retail'],
      isPremium: true,
      createdBy: 'Premium Templates'
    },
    {
      id: 'template-3',
      name: 'B2B Lead Nurturing Flow',
      description: 'Sophisticated lead nurturing sequence with multi-touch points and scoring automation',
      category: 'brand-awareness',
      objective: 'Nurture B2B leads',
      targetAudience: 'Enterprise sales teams',
      estimatedDuration: '12 weeks',
      budget: { min: 3000, max: 25000, currency: 'USD' },
      difficulty: 'intermediate',
      components: { moves: 15, plays: 5, automations: 10 },
      preview: {
        steps: ['Initial Contact', 'Education', 'Consideration', 'Decision', 'Onboarding']
      },
      usage: {
        downloads: 2100,
        rating: 4.9,
        reviews: 156,
        lastUpdated: new Date('2024-01-20')
      },
      tags: ['b2b', 'lead-nurturing', 'automation'],
      isPremium: false,
      createdBy: 'Sales Enablement'
    }
  ];

  // Mock campaign versions
  const campaignVersions: CampaignVersion[] = [
    {
      id: 'v1',
      version: '1.0.0',
      name: 'Initial Launch',
      description: 'First version of the campaign with basic email sequence',
      changes: ['Created initial campaign', 'Set up welcome sequence'],
      createdAt: new Date('2024-01-01'),
      createdBy: 'John Doe',
      isActive: false
    },
    {
      id: 'v2',
      version: '1.1.0',
      name: 'Social Media Integration',
      description: 'Added social media components and improved targeting',
      changes: ['Added social media moves', 'Enhanced audience segmentation', 'Improved analytics'],
      createdAt: new Date('2024-01-15'),
      createdBy: 'Jane Smith',
      isActive: false
    },
    {
      id: 'v3',
      version: '1.2.0',
      name: 'Automation Enhancement',
      description: 'Advanced automation with AI-powered optimization',
      changes: ['Added AI optimization', 'Enhanced automation rules', 'Improved reporting'],
      createdAt: new Date('2024-02-01'),
      createdBy: 'Mike Johnson',
      isActive: true
    }
  ];

  // Filter templates
  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  // Handle template selection
  const handleSelectTemplate = (template: CampaignTemplate) => {
    setSelectedTemplate(template);
    setShowPreview(true);
  };

  // Handle template usage
  const handleUseTemplate = async (template: CampaignTemplate) => {
    try {
      const campaignId = await createCampaign({
        name: `${template.name} - ${format(new Date(), 'MMM d, yyyy')}`,
        description: template.description,
        objective: template.objective as any,
        targetAudience: {
          id: 'audience-1',
          name: template.targetAudience,
          criteria: {},
          size: 1000,
          estimatedReach: 5000,
          customProperties: {}
        },
        budget: {
          total: template.budget.max,
          currency: template.budget.currency,
          allocated: {},
          spent: 0,
          remaining: template.budget.max
        },
        timeline: {
          startDate: new Date(),
          endDate: new Date(Date.now() + (6 * 7 * 24 * 60 * 60 * 1000)), // 6 weeks
          phases: [],
          milestones: []
        },
        // moves: [],
        // plays: [],
        // analytics: ...,
        // team: ...,
        settings: {
          autoOptimization: true,
          abTesting: false,
          notifications: {
            email: true,
            push: false,
            slack: false,
            frequency: 'daily',
            events: []
          },
          integrations: {},
          branding: {} as any
        }
        // tags: template.tags,
        // createdBy: 'current-user'
      });

      console.log('Campaign created from template:', campaignId);
      setShowPreview(false);
    } catch (error) {
      console.error('Failed to create campaign from template:', error);
    }
  };

  // Render templates marketplace
  const renderTemplatesMarketplace = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Campaign Templates</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Professional templates to accelerate your campaign creation
          </p>
        </div>

        <BlueprintButton className="flex items-center gap-2">
          <Plus size={16} />
          Create Template
        </BlueprintButton>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center gap-4 p-4 bg-[var(--surface)] rounded-lg">
        <div className="flex-1 relative">
          <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--ink-ghost)]" />
          <input
            type="text"
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
          />
        </div>

        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-4 py-2 bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
        >
          <option value="all">All Categories</option>
          <option value="product-launch">Product Launch</option>
          <option value="lead-generation">Lead Generation</option>
          <option value="brand-awareness">Brand Awareness</option>
          <option value="event-promotion">Event Promotion</option>
          <option value="content-marketing">Content Marketing</option>
        </select>

        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              className="rounded border-[var(--structure-subtle)] text-[var(--blueprint)]"
            />
            Premium only
          </label>
        </div>
      </div>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTemplates.map((template) => (
          <BlueprintCard key={template.id} className="overflow-hidden hover:border-[var(--blueprint)] transition-colors cursor-pointer">
            {/* Template Header */}
            <div className="p-4 border-b border-[var(--structure-subtle)]">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-sm font-semibold text-[var(--ink)]">{template.name}</h3>
                    {template.isPremium && (
                      <BlueprintBadge variant="default" size="sm" className="bg-[var(--warning)] text-white">
                        Premium
                      </BlueprintBadge>
                    )}
                  </div>
                  <p className="text-xs text-[var(--ink-muted)] line-clamp-2">
                    {template.description}
                  </p>
                </div>

                <button className="p-1 text-[var(--ink-ghost)] hover:text-[var(--ink)]">
                  <MoreVertical size={16} />
                </button>
              </div>

              {/* Template Metadata */}
              <div className="flex items-center gap-4 text-xs text-[var(--ink-muted)]">
                <div className="flex items-center gap-1">
                  <Clock size={12} />
                  {template.estimatedDuration}
                </div>
                <div className="flex items-center gap-1">
                  <Users size={12} />
                  {template.targetAudience}
                </div>
                <div className="flex items-center gap-1">
                  <BarChart3 size={12} />
                  {template.difficulty}
                </div>
              </div>
            </div>

            {/* Template Content */}
            <div className="p-4">
              {/* Components */}
              <div className="grid grid-cols-3 gap-2 mb-4">
                <div className="text-center p-2 bg-[var(--surface)] rounded">
                  <div className="text-lg font-semibold text-[var(--ink)]">{template.components.moves}</div>
                  <div className="text-xs text-[var(--ink-muted)]">Moves</div>
                </div>
                <div className="text-center p-2 bg-[var(--surface)] rounded">
                  <div className="text-lg font-semibold text-[var(--ink)]">{template.components.plays}</div>
                  <div className="text-xs text-[var(--ink-muted)]">Plays</div>
                </div>
                <div className="text-center p-2 bg-[var(--surface)] rounded">
                  <div className="text-lg font-semibold text-[var(--ink)]">{template.components.automations}</div>
                  <div className="text-xs text-[var(--ink-muted)]">Automations</div>
                </div>
              </div>

              {/* Budget Range */}
              <div className="mb-4">
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-[var(--ink-muted)]">Budget Range</span>
                  <span className="text-[var(--ink)]">
                    ${template.budget.min.toLocaleString()} - ${template.budget.max.toLocaleString()}
                  </span>
                </div>
                <div className="w-full bg-[var(--structure-subtle)] rounded-full h-2">
                  <div
                    className="bg-[var(--blueprint)] h-2 rounded-full"
                    style={{ width: '60%' }}
                  />
                </div>
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-1 mb-4">
                {template.tags.map((tag) => (
                  <span key={tag} className="px-2 py-1 text-xs bg-[var(--surface)] text-[var(--ink-muted)] rounded">
                    {tag}
                  </span>
                ))}
              </div>

              {/* Usage Stats */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3 text-xs">
                  <div className="flex items-center gap-1">
                    <Download size={12} />
                    <span>{template.usage.downloads}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Star size={12} className="text-[var(--warning)]" />
                    <span>{template.usage.rating}</span>
                  </div>
                </div>
                <span className="text-xs text-[var(--ink-muted)]">
                  {formatDistanceToNow(template.usage.lastUpdated, { addSuffix: true })}
                </span>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2">
                <BlueprintButton
                  variant="secondary"
                  size="sm"
                  onClick={() => handleSelectTemplate(template)}
                  className="flex items-center gap-2"
                >
                  <Eye size={14} />
                  Preview
                </BlueprintButton>

                <BlueprintButton
                  size="sm"
                  onClick={() => handleUseTemplate(template)}
                  className="flex items-center gap-2"
                >
                  <Play size={14} />
                  Use Template
                </BlueprintButton>
              </div>
            </div>
          </BlueprintCard>
        ))}
      </div>
    </div>
  );

  // Render campaign cloning
  const renderCampaignCloning = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Campaign Cloning</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Clone and customize existing campaigns for rapid deployment
          </p>
        </div>
      </div>

      <BlueprintCard className="p-6">
        <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Clone Existing Campaign</h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-[var(--ink)] mb-2">
              Select Campaign to Clone
            </label>
            <select className="w-full px-3 py-2 bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]">
              <option value="">Choose a campaign...</option>
              {Object.values(campaigns).map((campaign) => (
                <option key={campaign.id} value={campaign.id}>
                  {campaign.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--ink)] mb-2">
              Clone Type
            </label>
            <div className="grid grid-cols-3 gap-4">
              {[
                { value: 'exact', label: 'Exact Clone', description: 'Copy everything exactly as is' },
                { value: 'template', label: 'Template Clone', description: 'Copy structure, reset data' },
                { value: 'custom', label: 'Custom Clone', description: 'Choose what to copy' }
              ].map((type) => (
                <label key={type.value} className="flex items-center gap-3 p-3 border border-[var(--structure-subtle)] rounded-lg cursor-pointer hover:border-[var(--blueprint)]">
                  <input
                    type="radio"
                    name="cloneType"
                    value={type.value}
                    className="text-[var(--blueprint)]"
                  />
                  <div>
                    <div className="text-sm font-medium text-[var(--ink)]">{type.label}</div>
                    <div className="text-xs text-[var(--ink-muted)]">{type.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--ink)] mb-2">
              New Campaign Name
            </label>
            <input
              type="text"
              placeholder="Enter campaign name..."
              className="w-full px-3 py-2 bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
            />
          </div>

          <div className="flex items-center gap-4">
            <BlueprintButton className="flex items-center gap-2">
              <Copy size={16} />
              Clone Campaign
            </BlueprintButton>

            <BlueprintButton variant="secondary" className="flex items-center gap-2">
              <Settings size={16} />
              Advanced Options
            </BlueprintButton>
          </div>
        </div>
      </BlueprintCard>
    </div>
  );

  // Render version control
  const renderVersionControl = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Version Control</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Track and manage campaign versions with full history
          </p>
        </div>

        <BlueprintButton className="flex items-center gap-2">
          <Plus size={16} />
          Create Version
        </BlueprintButton>
      </div>

      <BlueprintCard className="p-6">
        <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Version History</h3>

        <div className="space-y-4">
          {campaignVersions.map((version, index) => (
            <div key={version.id} className="flex items-start gap-4 p-4 border border-[var(--structure-subtle)] rounded-lg">
              <div className="flex-shrink-0">
                <div className={cn(
                  "w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold",
                  version.isActive
                    ? "bg-[var(--success)] text-white"
                    : "bg-[var(--surface)] text-[var(--ink-muted)]"
                )}>
                  {version.version.split('.').map(v => v[0]).join('')}
                </div>
              </div>

              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-semibold text-[var(--ink)]">{version.name}</h4>
                  <div className="flex items-center gap-2">
                    {version.isActive && (
                      <BlueprintBadge variant="default" size="sm" className="bg-[var(--success)]">
                        Active
                      </BlueprintBadge>
                    )}
                    <span className="text-xs text-[var(--ink-muted)]">
                      {formatDistanceToNow(version.createdAt, { addSuffix: true })}
                    </span>
                  </div>
                </div>

                <p className="text-sm text-[var(--ink-muted)] mb-3">{version.description}</p>

                <div className="space-y-2">
                  <div className="text-xs font-medium text-[var(--ink)]">Changes:</div>
                  <ul className="space-y-1">
                    {version.changes.map((change, idx) => (
                      <li key={idx} className="text-xs text-[var(--ink-muted)] flex items-center gap-2">
                        <ChevronRight size={12} />
                        {change}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="flex items-center justify-between mt-4 pt-3 border-t border-[var(--structure-subtle)]">
                  <div className="text-xs text-[var(--ink-muted)]">
                    Created by {version.createdBy}
                  </div>

                  <div className="flex items-center gap-2">
                    {!version.isActive && (
                      <BlueprintButton variant="secondary" size="sm">
                        Restore
                      </BlueprintButton>
                    )}
                    {/* Assuming 'feature' is a placeholder for some dynamic content */}
                    <BlueprintBadge variant="blueprint" size="sm">
                      Feature
                    </BlueprintBadge>
                    <BlueprintButton variant="secondary" size="sm">
                      Compare
                    </BlueprintButton>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </BlueprintCard>
    </div>
  );

  // Render multi-campaign orchestration
  const renderMultiCampaignOrchestration = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Multi-Campaign Orchestration</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Coordinate multiple campaigns with shared objectives and resources
          </p>
        </div>

        <BlueprintButton className="flex items-center gap-2">
          <Plus size={16} />
          Create Orchestration
        </BlueprintButton>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Orchestrations */}
        <BlueprintCard className="p-6">
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Active Orchestrations</h3>

          <div className="space-y-3">
            {[
              {
                name: 'Q1 Product Launch Suite',
                campaigns: 3,
                status: 'active',
                progress: 65,
                nextAction: 'Review social media assets'
              },
              {
                name: 'Holiday Sales Campaign',
                campaigns: 5,
                status: 'active',
                progress: 40,
                nextAction: 'Approve email creative'
              },
              {
                name: 'Brand Awareness Initiative',
                campaigns: 2,
                status: 'planning',
                progress: 15,
                nextAction: 'Set up tracking parameters'
              }
            ].map((orchestration, index) => (
              <div key={index} className="p-4 bg-[var(--surface)] rounded-lg">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="text-sm font-semibold text-[var(--ink)]">{orchestration.name}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <BlueprintBadge variant="default" size="sm">
                        {orchestration.campaigns} campaigns
                      </BlueprintBadge>
                      <BlueprintBadge
                        variant={orchestration.status === 'active' ? 'success' : 'default'}
                        size="sm"
                      >
                        {orchestration.status}
                      </BlueprintBadge>
                    </div>
                  </div>

                  <button className="p-1 text-[var(--ink-ghost)] hover:text-[var(--ink)]">
                    <MoreVertical size={16} />
                  </button>
                </div>

                <div className="mb-3">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-[var(--ink-muted)]">Progress</span>
                    <span className="text-[var(--ink)]">{orchestration.progress}%</span>
                  </div>
                  <div className="w-full bg-[var(--structure-subtle)] rounded-full h-2">
                    <div
                      className="bg-[var(--blueprint)] h-2 rounded-full transition-all"
                      style={{ width: `${orchestration.progress}%` }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="text-xs text-[var(--ink-muted)]">
                    Next: {orchestration.nextAction}
                  </div>

                  <BlueprintButton variant="secondary" size="sm">
                    Manage
                  </BlueprintButton>
                </div>
              </div>
            ))}
          </div>
        </BlueprintCard>

        {/* Orchestration Tools */}
        <BlueprintCard className="p-6">
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Orchestration Tools</h3>

          <div className="space-y-4">
            {[
              {
                icon: Target,
                title: 'Cross-Campaign Analytics',
                description: 'View combined performance across all campaigns',
                action: 'View Analytics'
              },
              {
                icon: Users,
                title: 'Audience Segmentation',
                description: 'Share and sync audience segments across campaigns',
                action: 'Manage Segments'
              },
              {
                icon: Calendar,
                title: 'Timeline Coordination',
                description: 'Coordinate campaign schedules and avoid conflicts',
                action: 'View Timeline'
              },
              {
                icon: Zap,
                title: 'Resource Optimization',
                description: 'Optimize budget and resource allocation',
                action: 'Optimize'
              }
            ].map((tool, index) => {
              const Icon = tool.icon;
              return (
                <div key={index} className="flex items-center gap-4 p-4 bg-[var(--surface)] rounded-lg hover:bg-[var(--surface)]/80 transition-colors cursor-pointer">
                  <div className="w-10 h-10 rounded-lg bg-[var(--blueprint-light)]/10 flex items-center justify-center">
                    <Icon size={20} className="text-[var(--blueprint)]" />
                  </div>

                  <div className="flex-1">
                    <h4 className="text-sm font-medium text-[var(--ink)]">{tool.title}</h4>
                    <p className="text-xs text-[var(--ink-muted)]">{tool.description}</p>
                  </div>

                  <BlueprintButton variant="secondary" size="sm">
                    {tool.action}
                  </BlueprintButton>
                </div>
              );
            })}
          </div>
        </BlueprintCard>
      </div>
    </div>
  );

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-[var(--structure-subtle)]">
        <div>
          <h1 className="text-2xl font-bold text-[var(--ink)]">Advanced Campaign Features</h1>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Professional tools for sophisticated campaign management
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-6 px-6 border-b border-[var(--structure-subtle)]">
        {[
          { id: 'templates', label: 'Templates Marketplace', icon: Globe },
          { id: 'cloning', label: 'Campaign Cloning', icon: Copy },
          { id: 'versioning', label: 'Version Control', icon: Clock },
          { id: 'orchestration', label: 'Multi-Campaign', icon: Zap }
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
        {activeTab === 'templates' && renderTemplatesMarketplace()}
        {activeTab === 'cloning' && renderCampaignCloning()}
        {activeTab === 'versioning' && renderVersionControl()}
        {activeTab === 'orchestration' && renderMultiCampaignOrchestration()}
      </div>

      {/* Template Preview Modal */}
      {showPreview && selectedTemplate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <BlueprintCard className="w-full max-w-4xl max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-[var(--structure-subtle)]">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-[var(--ink)]">{selectedTemplate.name}</h3>
                <button
                  onClick={() => setShowPreview(false)}
                  className="p-1 text-[var(--ink-ghost)] hover:text-[var(--ink)]"
                >
                  <X size={20} />
                </button>
              </div>
            </div>

            <div className="p-6 overflow-y-auto max-h-96">
              <div className="space-y-6">
                <div>
                  <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Description</h4>
                  <p className="text-sm text-[var(--ink-muted)]">{selectedTemplate.description}</p>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Campaign Steps</h4>
                  <div className="space-y-2">
                    {selectedTemplate.preview.steps.map((step, index) => (
                      <div key={index} className="flex items-center gap-3 p-3 bg-[var(--surface)] rounded-lg">
                        <div className="w-8 h-8 rounded-full bg-[var(--blueprint-light)]/10 flex items-center justify-center text-sm font-semibold text-[var(--blueprint)]">
                          {index + 1}
                        </div>
                        <span className="text-sm text-[var(--ink)]">{step}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Components Included</h4>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-3 bg-[var(--surface)] rounded-lg">
                      <div className="text-2xl font-bold text-[var(--blueprint)]">{selectedTemplate.components.moves}</div>
                      <div className="text-xs text-[var(--ink-muted)]">Moves</div>
                    </div>
                    <div className="text-center p-3 bg-[var(--surface)] rounded-lg">
                      <div className="text-2xl font-bold text-[var(--blueprint)]">{selectedTemplate.components.plays}</div>
                      <div className="text-xs text-[var(--ink-muted)]">Plays</div>
                    </div>
                    <div className="text-center p-3 bg-[var(--surface)] rounded-lg">
                      <div className="text-2xl font-bold text-[var(--blueprint)]">{selectedTemplate.components.automations}</div>
                      <div className="text-xs text-[var(--ink-muted)]">Automations</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-[var(--structure-subtle)] flex justify-end gap-3">
              <BlueprintButton
                variant="secondary"
                onClick={() => setShowPreview(false)}
              >
                Close
              </BlueprintButton>
              <BlueprintButton onClick={() => handleUseTemplate(selectedTemplate)}>
                Use This Template
              </BlueprintButton>
            </div>
          </BlueprintCard>
        </div>
      )}
    </div>
  );
}
