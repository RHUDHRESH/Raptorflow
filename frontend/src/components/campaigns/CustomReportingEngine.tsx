"use client";

import { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  Calendar,
  Filter,
  Settings,
  Plus,
  Edit,
  Trash2,
  Copy,
  Eye,
  Share2,
  Clock,
  TrendingUp,
  BarChart3,
  PieChart,
  LineChart,
  Grid,
  List,
  Maximize2,
  Minimize2,
  RefreshCw,
  Save,
  Play,
  Pause,
  MoreVertical,
  ChevronDown,
  ChevronUp,
  ChevronRight,
  ChevronLeft,
  Search,
  Database,
  Mail,
  Users,
  DollarSign,
  Target,
  Activity
} from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { useEnhancedCampaignStore } from '@/stores/enhancedCampaignStore';
import { cn } from '@/lib/utils';
import { format, formatDistanceToNow, addDays, subDays } from 'date-fns';

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  category: 'campaign' | 'audience' | 'revenue' | 'performance' | 'custom';
  type: 'summary' | 'detailed' | 'comparison' | 'trend' | 'custom';
  metrics: string[];
  filters: {
    dateRange: boolean;
    campaigns: boolean;
    channels: boolean;
    segments: boolean;
  };
  visualization: {
    chartTypes: string[];
    layout: 'grid' | 'list' | 'dashboard';
  };
  schedule: {
    enabled: boolean;
    frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
    recipients: string[];
    format: 'pdf' | 'excel' | 'csv' | 'json';
  };
  createdBy: string;
  createdAt: Date;
  lastModified: Date;
  isPublic: boolean;
  usage: {
    views: number;
    exports: number;
    shares: number;
  };
}

interface CustomReport {
  id: string;
  name: string;
  description: string;
  templateId: string;
  parameters: {
    dateRange: {
      start: Date;
      end: Date;
    };
    campaigns: string[];
    channels: string[];
    segments: string[];
    metrics: string[];
  };
  status: 'draft' | 'generating' | 'ready' | 'error';
  generatedAt?: Date;
  expiresAt?: Date;
  data: {
    summary: Record<string, number>;
    charts: {
      type: string;
      data: any[];
      config: Record<string, any>;
    }[];
    tables: {
      headers: string[];
      rows: any[][];
    }[];
  };
  shareSettings: {
    isPublic: boolean;
    allowedUsers: string[];
    shareLink?: string;
  };
}

interface ScheduledReport {
  id: string;
  name: string;
  templateId: string;
  schedule: {
    frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
    dayOfWeek?: number;
    dayOfMonth?: number;
    time: string;
    timezone: string;
  };
  recipients: {
    emails: string[];
    roles: string[];
  };
  format: 'pdf' | 'excel' | 'csv' | 'json';
  delivery: {
    email: boolean;
    dashboard: boolean;
    webhook?: string;
  };
  lastRun?: Date;
  nextRun: Date;
  isActive: boolean;
  status: 'active' | 'paused' | 'error';
}

interface DashboardWidget {
  id: string;
  type: 'metric' | 'chart' | 'table' | 'text';
  title: string;
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  config: {
    metric?: string;
    chartType?: string;
    dataSource?: string;
    filters?: Record<string, any>;
  };
  data?: any;
}

export function CustomReportingEngine() {
  const [activeTab, setActiveTab] = useState<'templates' | 'reports' | 'scheduled' | 'dashboards'>('templates');
  const [selectedTemplate, setSelectedTemplate] = useState<ReportTemplate | null>(null);
  const [isCreatingReport, setIsCreatingReport] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // Mock report templates
  const [templates, setTemplates] = useState<ReportTemplate[]>([
    {
      id: '1',
      name: 'Campaign Performance Summary',
      description: 'Comprehensive overview of campaign performance metrics',
      category: 'campaign',
      type: 'summary',
      metrics: ['reach', 'engagement', 'conversions', 'revenue', 'roi'],
      filters: {
        dateRange: true,
        campaigns: true,
        channels: true,
        segments: false
      },
      visualization: {
        chartTypes: ['line', 'bar', 'pie'],
        layout: 'dashboard'
      },
      schedule: {
        enabled: false,
        frequency: 'weekly',
        recipients: [],
        format: 'pdf'
      },
      createdBy: 'John Doe',
      createdAt: subDays(new Date(), 30),
      lastModified: subDays(new Date(), 5),
      isPublic: true,
      usage: {
        views: 156,
        exports: 42,
        shares: 8
      }
    },
    {
      id: '2',
      name: 'Revenue Analysis Report',
      description: 'Detailed revenue breakdown by channel and campaign',
      category: 'revenue',
      type: 'detailed',
      metrics: ['revenue', 'cost', 'profit', 'roi', 'cac', 'ltv'],
      filters: {
        dateRange: true,
        campaigns: true,
        channels: true,
        segments: true
      },
      visualization: {
        chartTypes: ['bar', 'line', 'heatmap'],
        layout: 'grid'
      },
      schedule: {
        enabled: true,
        frequency: 'monthly',
        recipients: ['finance@company.com'],
        format: 'excel'
      },
      createdBy: 'Jane Smith',
      createdAt: subDays(new Date(), 45),
      lastModified: subDays(new Date(), 10),
      isPublic: false,
      usage: {
        views: 89,
        exports: 23,
        shares: 3
      }
    },
    {
      id: '3',
      name: 'Audience Engagement Trends',
      description: 'Track audience engagement patterns over time',
      category: 'audience',
      type: 'trend',
      metrics: ['engagement', 'retention', 'churn', 'satisfaction'],
      filters: {
        dateRange: true,
        campaigns: false,
        channels: true,
        segments: true
      },
      visualization: {
        chartTypes: ['line', 'area', 'scatter'],
        layout: 'list'
      },
      schedule: {
        enabled: false,
        frequency: 'weekly',
        recipients: [],
        format: 'pdf'
      },
      createdBy: 'Mike Johnson',
      createdAt: subDays(new Date(), 60),
      lastModified: subDays(new Date(), 15),
      isPublic: true,
      usage: {
        views: 234,
        exports: 67,
        shares: 12
      }
    }
  ]);

  // Mock custom reports
  const [customReports, setCustomReports] = useState<CustomReport[]>([
    {
      id: '1',
      name: 'Q1 2024 Campaign Review',
      description: 'Quarterly review of all Q1 campaigns',
      templateId: '1',
      parameters: {
        dateRange: {
          start: new Date('2024-01-01'),
          end: new Date('2024-03-31')
        },
        campaigns: ['1', '2', '3'],
        channels: ['email', 'social', 'paid'],
        segments: [],
        metrics: ['reach', 'engagement', 'conversions', 'revenue']
      },
      status: 'ready',
      generatedAt: subDays(new Date(), 2),
      expiresAt: addDays(new Date(), 28),
      data: {
        summary: {
          totalReach: 125000,
          totalEngagement: 15.2,
          totalConversions: 1920,
          totalRevenue: 96000
        },
        charts: [],
        tables: []
      },
      shareSettings: {
        isPublic: false,
        allowedUsers: ['john@company.com', 'jane@company.com']
      }
    },
    {
      id: '2',
      name: 'Email Channel Performance',
      description: 'Deep dive into email marketing performance',
      templateId: '2',
      parameters: {
        dateRange: {
          start: subDays(new Date(), 30),
          end: new Date()
        },
        campaigns: ['1', '3'],
        channels: ['email'],
        segments: ['premium', 'new_users'],
        metrics: ['revenue', 'cost', 'roi']
      },
      status: 'generating',
      data: {
        summary: {},
        charts: [],
        tables: []
      },
      shareSettings: {
        isPublic: true,
        allowedUsers: [],
        shareLink: 'https://reports.company.com/share/abc123'
      }
    }
  ]);

  // Mock scheduled reports
  const [scheduledReports, setScheduledReports] = useState<ScheduledReport[]>([
    {
      id: '1',
      name: 'Weekly Performance Report',
      templateId: '1',
      schedule: {
        frequency: 'weekly',
        dayOfWeek: 1, // Monday
        time: '09:00',
        timezone: 'UTC'
      },
      recipients: {
        emails: ['team@company.com'],
        roles: ['marketing_manager']
      },
      format: 'pdf',
      delivery: {
        email: true,
        dashboard: true
      },
      lastRun: subDays(new Date(), 3),
      nextRun: addDays(new Date(), 4),
      isActive: true,
      status: 'active'
    },
    {
      id: '2',
      name: 'Monthly Revenue Report',
      templateId: '2',
      schedule: {
        frequency: 'monthly',
        dayOfMonth: 1,
        time: '08:00',
        timezone: 'UTC'
      },
      recipients: {
        emails: ['finance@company.com', 'ceo@company.com'],
        roles: []
      },
      format: 'excel',
      delivery: {
        email: true,
        dashboard: false
      },
      lastRun: subDays(new Date(), 15),
      nextRun: addDays(new Date(), 16),
      isActive: true,
      status: 'active'
    }
  ]);

  // Mock dashboard widgets
  const [dashboardWidgets, setDashboardWidgets] = useState<DashboardWidget[]>([
    {
      id: '1',
      type: 'metric',
      title: 'Total Revenue',
      position: { x: 0, y: 0, width: 3, height: 2 },
      config: {
        metric: 'revenue'
      },
      data: { value: 125000, change: 12.5 }
    },
    {
      id: '2',
      type: 'chart',
      title: 'Campaign Performance',
      position: { x: 3, y: 0, width: 6, height: 4 },
      config: {
        chartType: 'line',
        dataSource: 'campaigns'
      },
      data: { labels: ['Jan', 'Feb', 'Mar'], datasets: [] }
    },
    {
      id: '3',
      type: 'table',
      title: 'Top Campaigns',
      position: { x: 9, y: 0, width: 3, height: 4 },
      config: {
        dataSource: 'campaigns'
      },
      data: { headers: ['Name', 'Revenue', 'ROI'], rows: [] }
    }
  ]);

  // Handle template selection
  const handleSelectTemplate = (template: ReportTemplate) => {
    setSelectedTemplate(template);
    setIsCreatingReport(true);
  };

  // Handle report generation
  const handleGenerateReport = async (templateId: string, parameters: any) => {
    const newReport: CustomReport = {
      id: Date.now().toString(),
      name: `Report from ${templates.find(t => t.id === templateId)?.name}`,
      description: 'Generated report',
      templateId,
      parameters,
      status: 'generating',
      data: { summary: {}, charts: [], tables: [] },
      shareSettings: { isPublic: false, allowedUsers: [] }
    };

    setCustomReports(prev => [newReport, ...prev]);

    // Simulate report generation
    setTimeout(() => {
      setCustomReports(prev => prev.map(report =>
        report.id === newReport.id
          ? {
              ...report,
              status: 'ready',
              generatedAt: new Date(),
              expiresAt: addDays(new Date(), 30),
              data: {
                summary: { totalRevenue: 45000, totalConversions: 890 },
                charts: [],
                tables: []
              }
            }
          : report
      ));
    }, 3000);
  };

  // Get category icon
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'campaign': return Target;
      case 'audience': return Users;
      case 'revenue': return DollarSign;
      case 'performance': return Activity;
      default: return FileText;
    }
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready':
      case 'active': return 'text-[var(--success)]';
      case 'generating': return 'text-[var(--warning)]';
      case 'draft':
      case 'paused': return 'text-[var(--ink-ghost)]';
      case 'error': return 'text-[var(--destructive)]';
      default: return 'text-[var(--ink-muted)]';
    }
  };

  // Render report templates
  const renderReportTemplates = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Report Templates</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Pre-built templates for common reporting needs
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1">
            <button
              onClick={() => setViewMode('grid')}
              className={cn(
                "p-2 rounded",
                viewMode === 'grid' && "bg-[var(--blueprint-light)]/10 text-[var(--blueprint)]"
              )}
            >
              <Grid size={16} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                "p-2 rounded",
                viewMode === 'list' && "bg-[var(--blueprint-light)]/10 text-[var(--blueprint)]"
              )}
            >
              <List size={16} />
            </button>
          </div>

          <BlueprintButton className="flex items-center gap-2">
            <Plus size={16} />
            Create Template
          </BlueprintButton>
        </div>
      </div>

      <div className={cn(
        viewMode === 'grid' ? "grid grid-cols-1 lg:grid-cols-2 gap-6" : "space-y-4"
      )}>
        {templates.map((template) => {
          const Icon = getCategoryIcon(template.category);
          return (
            <BlueprintCard key={template.id} className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-[var(--blueprint-light)]/10 rounded-lg flex items-center justify-center">
                    <Icon size={20} className="text-[var(--blueprint)]" />
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-[var(--ink)]">{template.name}</h3>
                    <p className="text-sm text-[var(--ink-muted)] mt-1">{template.description}</p>

                    <div className="flex items-center gap-2 mt-2">
                      <BlueprintBadge variant="default" size="sm">
                        {template.category}
                      </BlueprintBadge>
                      <BlueprintBadge variant="default" size="sm">
                        {template.type}
                      </BlueprintBadge>
                      {template.isPublic && (
                        <BlueprintBadge variant="success" size="sm">
                          Public
                        </BlueprintBadge>
                      )}
                    </div>
                  </div>
                </div>

                <button className="p-1 text-[var(--ink-ghost)] hover:text-[var(--ink)]">
                  <MoreVertical size={16} />
                </button>
              </div>

              {/* Metrics */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Metrics</h4>
                <div className="flex flex-wrap gap-1">
                  {template.metrics.map((metric) => (
                    <span key={metric} className="px-2 py-1 text-xs bg-[var(--surface)] text-[var(--ink)] rounded capitalize">
                      {metric}
                    </span>
                  ))}
                </div>
              </div>

              {/* Usage stats */}
              <div className="grid grid-cols-3 gap-4 mb-4 text-center">
                <div>
                  <div className="text-lg font-bold text-[var(--ink)]">{template.usage.views}</div>
                  <div className="text-xs text-[var(--ink-muted)]">Views</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-[var(--ink)]">{template.usage.exports}</div>
                  <div className="text-xs text-[var(--ink-muted)]">Exports</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-[var(--ink)]">{template.usage.shares}</div>
                  <div className="text-xs text-[var(--ink-muted)]">Shares</div>
                </div>
              </div>

              {/* Schedule indicator */}
              {template.schedule.enabled && (
                <div className="mb-4">
                  <div className="flex items-center gap-2 text-sm text-[var(--success)]">
                    <Clock size={14} />
                    <span>Scheduled {template.schedule.frequency}</span>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t border-[var(--structure-subtle)]">
                <div className="text-xs text-[var(--ink-muted)]">
                  Created {formatDistanceToNow(template.createdAt, { addSuffix: true })} •
                  Modified {formatDistanceToNow(template.lastModified, { addSuffix: true })}
                </div>

                <div className="flex items-center gap-2">
                  <BlueprintButton variant="secondary" size="sm">
                    <Eye size={14} />
                    Preview
                  </BlueprintButton>

                  <BlueprintButton
                    size="sm"
                    onClick={() => handleSelectTemplate(template)}
                  >
                    <FileText size={14} />
                    Use Template
                  </BlueprintButton>
                </div>
              </div>
            </BlueprintCard>
          );
        })}
      </div>
    </div>
  );

  // Render custom reports
  const renderCustomReports = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Custom Reports</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Your generated reports and analyses
          </p>
        </div>

        <BlueprintButton className="flex items-center gap-2">
          <Plus size={16} />
          New Report
        </BlueprintButton>
      </div>

      <div className="space-y-4">
        {customReports.map((report) => (
          <BlueprintCard key={report.id} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-[var(--ink)]">{report.name}</h3>
                <p className="text-sm text-[var(--ink-muted)]">{report.description}</p>

                <div className="flex items-center gap-2 mt-2">
                  <BlueprintBadge
                    variant={report.status === 'ready' ? 'success' : report.status === 'generating' ? 'warning' : 'default'}
                    size="sm"
                  >
                    {report.status}
                  </BlueprintBadge>

                  <span className="text-xs text-[var(--ink-muted)]">
                    Template: {templates.find(t => t.id === report.templateId)?.name}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {report.shareSettings.isPublic && (
                  <BlueprintBadge variant="success" size="sm">
                    <Share2 size={12} />
                    Shared
                  </BlueprintBadge>
                )}

                <button className="p-1 text-[var(--ink-ghost)] hover:text-[var(--ink)]">
                  <MoreVertical size={16} />
                </button>
              </div>
            </div>

            {/* Report parameters */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Parameters</h4>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-[var(--ink-muted)]">Date Range</span>
                  <div className="text-[var(--ink)]">
                    {format(report.parameters.dateRange.start, 'MMM d')} - {format(report.parameters.dateRange.end, 'MMM d')}
                  </div>
                </div>
                <div>
                  <span className="text-[var(--ink-muted)]">Campaigns</span>
                  <div className="text-[var(--ink)]">{report.parameters.campaigns.length} selected</div>
                </div>
                <div>
                  <span className="text-[var(--ink-muted)]">Channels</span>
                  <div className="text-[var(--ink)]">{report.parameters.channels.length} selected</div>
                </div>
                <div>
                  <span className="text-[var(--ink-muted)]">Metrics</span>
                  <div className="text-[var(--ink)]">{report.parameters.metrics.length} selected</div>
                </div>
              </div>
            </div>

            {/* Report data summary */}
            {report.status === 'ready' && report.data.summary && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Summary</h4>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  {Object.entries(report.data.summary).map(([key, value]) => (
                    <div key={key} className="text-center p-2 bg-[var(--surface)] rounded">
                      <div className="text-lg font-bold text-[var(--ink)]">
                        {typeof value === 'number' ? value.toLocaleString() : value}
                      </div>
                      <div className="text-xs text-[var(--ink-muted)] capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-[var(--structure-subtle)]">
              <div className="text-sm text-[var(--ink-muted)]">
                {report.generatedAt && (
                  <>Generated {formatDistanceToNow(report.generatedAt, { addSuffix: true })}</>
                )}
                {report.expiresAt && (
                  <> • Expires {formatDistanceToNow(report.expiresAt, { addSuffix: true })}</>
                )}
              </div>

              <div className="flex items-center gap-2">
                {report.status === 'ready' && (
                  <>
                    <BlueprintButton variant="secondary" size="sm">
                      <Eye size={14} />
                      View
                    </BlueprintButton>

                    <BlueprintButton variant="secondary" size="sm">
                      <Download size={14} />
                      Export
                    </BlueprintButton>

                    <BlueprintButton variant="secondary" size="sm">
                      <Share2 size={14} />
                      Share
                    </BlueprintButton>
                  </>
                )}

                {report.status === 'generating' && (
                  <BlueprintButton variant="secondary" size="sm" disabled>
                    <RefreshCw size={14} className="animate-spin" />
                    Generating...
                  </BlueprintButton>
                )}
              </div>
            </div>
          </BlueprintCard>
        ))}
      </div>
    </div>
  );

  // Render scheduled reports
  const renderScheduledReports = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Scheduled Reports</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Automated report generation and delivery
          </p>
        </div>

        <BlueprintButton className="flex items-center gap-2">
          <Plus size={16} />
          Schedule Report
        </BlueprintButton>
      </div>

      <div className="space-y-4">
        {scheduledReports.map((scheduled) => (
          <BlueprintCard key={scheduled.id} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-[var(--ink)]">{scheduled.name}</h3>
                <div className="flex items-center gap-2 mt-1">
                  <BlueprintBadge
                    variant={scheduled.status === 'active' ? 'success' : scheduled.status === 'paused' ? 'warning' : 'error'}
                    size="sm"
                  >
                    {scheduled.status}
                  </BlueprintBadge>

                  <span className="text-xs text-[var(--ink-muted)]">
                    Template: {templates.find(t => t.id === scheduled.templateId)?.name}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <BlueprintButton
                  variant={scheduled.isActive ? 'secondary' : 'primary'}
                  size="sm"
                >
                  {scheduled.isActive ? <Pause size={14} /> : <Play size={14} />}
                  {scheduled.isActive ? 'Pause' : 'Resume'}
                </BlueprintButton>

                <button className="p-1 text-[var(--ink-ghost)] hover:text-[var(--ink)]">
                  <MoreVertical size={16} />
                </button>
              </div>
            </div>

            {/* Schedule details */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Schedule</h4>
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <Clock size={16} className="text-[var(--ink-ghost)]" />
                  <span className="capitalize">{scheduled.schedule.frequency}</span>
                  {scheduled.schedule.dayOfWeek && (
                    <span> • Day {scheduled.schedule.dayOfWeek}</span>
                  )}
                  {scheduled.schedule.dayOfMonth && (
                    <span> • Day {scheduled.schedule.dayOfMonth}</span>
                  )}
                  <span> • {scheduled.schedule.time}</span>
                </div>
              </div>
            </div>

            {/* Recipients */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Recipients</h4>
              <div className="flex flex-wrap gap-1">
                {scheduled.recipients.emails.map((email) => (
                  <span key={email} className="px-2 py-1 text-xs bg-[var(--surface)] text-[var(--ink)] rounded">
                    {email}
                  </span>
                ))}
                {scheduled.recipients.roles.map((role) => (
                  <span key={role} className="px-2 py-1 text-xs bg-[var(--blueprint-light)]/10 text-[var(--blueprint)] rounded">
                    {role}
                  </span>
                ))}
              </div>
            </div>

            {/* Delivery settings */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Delivery</h4>
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <Mail size={16} className={scheduled.delivery.email ? "text-[var(--ink)]" : "text-[var(--ink-ghost)]"} />
                  <span>Email</span>
                </div>
                <div className="flex items-center gap-2">
                  <Database size={16} className={scheduled.delivery.dashboard ? "text-[var(--ink)]" : "text-[var(--ink-ghost)]"} />
                  <span>Dashboard</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[var(--ink-muted)]">Format:</span>
                  <BlueprintBadge variant="default" size="sm">
                    {scheduled.format.toUpperCase()}
                  </BlueprintBadge>
                </div>
              </div>
            </div>

            {/* Timing */}
            <div className="flex items-center justify-between pt-4 border-t border-[var(--structure-subtle)]">
              <div className="text-sm text-[var(--ink-muted)]">
                {scheduled.lastRun && (
                  <span>Last run {formatDistanceToNow(scheduled.lastRun, { addSuffix: true })} • </span>
                )}
                Next run {formatDistanceToNow(scheduled.nextRun, { addSuffix: true })}
              </div>

              <div className="flex items-center gap-2">
                <BlueprintButton variant="secondary" size="sm">
                  <Edit size={14} />
                  Edit
                </BlueprintButton>

                <BlueprintButton variant="secondary" size="sm">
                  <Play size={14} />
                  Run Now
                </BlueprintButton>
              </div>
            </div>
          </BlueprintCard>
        ))}
      </div>
    </div>
  );

  // Render custom dashboards
  const renderCustomDashboards = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[var(--ink)]">Custom Dashboards</h2>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Build and customize your own dashboards
          </p>
        </div>

        <div className="flex items-center gap-2">
          <BlueprintButton variant="secondary" className="flex items-center gap-2">
            <Settings size={16} />
            Layout
          </BlueprintButton>

          <BlueprintButton className="flex items-center gap-2">
            <Plus size={16} />
            Add Widget
          </BlueprintButton>
        </div>
      </div>

      <BlueprintCard className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-[var(--ink)]">Marketing Overview Dashboard</h3>
          <div className="flex items-center gap-2">
            <BlueprintButton variant="secondary" size="sm">
              <RefreshCw size={14} />
              Refresh
            </BlueprintButton>

            <BlueprintButton variant="secondary" size="sm">
              <Save size={14} />
              Save
            </BlueprintButton>
          </div>
        </div>

        <div className="grid grid-cols-12 gap-4 min-h-96">
          {dashboardWidgets.map((widget) => (
            <div
              key={widget.id}
              className={cn(
                "bg-[var(--surface)] rounded-lg p-4 border border-[var(--structure-subtle)]"
              )}
              style={{
                gridColumn: `span ${widget.position.width}`,
                gridRow: `span ${widget.position.height}`
              }}
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-medium text-[var(--ink)]">{widget.title}</h4>
                <button className="p-1 text-[var(--ink-ghost)] hover:text-[var(--ink)]">
                  <MoreVertical size={12} />
                </button>
              </div>

              <div className="h-full flex items-center justify-center">
                {widget.type === 'metric' && widget.data && (
                  <div className="text-center">
                    <div className="text-2xl font-bold text-[var(--ink)]">
                      {typeof widget.data.value === 'number' ? widget.data.value.toLocaleString() : widget.data.value}
                    </div>
                    <div className="text-sm text-[var(--success)]">
                      {widget.data.change > 0 ? '+' : ''}{widget.data.change}%
                    </div>
                  </div>
                )}

                {widget.type === 'chart' && (
                  <div className="text-center">
                    <BarChart3 size={48} className="text-[var(--blueprint)] mx-auto mb-2" />
                    <p className="text-sm text-[var(--ink)]">Chart visualization</p>
                  </div>
                )}

                {widget.type === 'table' && (
                  <div className="text-center">
                    <Grid size={48} className="text-[var(--blueprint)] mx-auto mb-2" />
                    <p className="text-sm text-[var(--ink)]">Data table</p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </BlueprintCard>
    </div>
  );

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-[var(--structure-subtle)]">
        <div>
          <h1 className="text-2xl font-bold text-[var(--ink)]">Custom Reporting Engine</h1>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Create, schedule, and manage custom reports and dashboards
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
          { id: 'templates', label: 'Templates', icon: FileText },
          { id: 'reports', label: 'Reports', icon: BarChart3 },
          { id: 'scheduled', label: 'Scheduled', icon: Clock },
          { id: 'dashboards', label: 'Dashboards', icon: Grid }
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
        {activeTab === 'templates' && renderReportTemplates()}
        {activeTab === 'reports' && renderCustomReports()}
        {activeTab === 'scheduled' && renderScheduledReports()}
        {activeTab === 'dashboards' && renderCustomDashboards()}
      </div>
    </div>
  );
}
