import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/Button';
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  DollarSign, 
  ShoppingCart, 
  Activity,
  Target,
  Calendar,
  Download,
  Filter,
  Plus,
  Eye,
  BarChart3
} from 'lucide-react';

import { DashboardLayout } from './DashboardSidebar';
import { 
  RevenueChart, 
  UserActivityChart, 
  TrafficSourcesChart, 
  ConversionRateChart 
} from './InteractiveCharts';
import { ActivityFeed, ActivityFilters } from './ActivityFeed';
import EnhancedStatCard from './EnhancedStatCard';
import QuickActions from './QuickAction';

const generateMockStats = () => [
  {
    title: 'Total Revenue',
    value: '$45,231',
    change: 12.5,
    changeType: 'increase',
    icon: DollarSign,
    description: 'Revenue from all sources'
  },
  {
    title: 'Active Users',
    value: '2,341',
    change: 8.2,
    changeType: 'increase',
    icon: Users,
    description: 'Users active this month'
  },
  {
    title: 'Conversion Rate',
    value: '3.24%',
    change: -2.1,
    changeType: 'decrease',
    icon: Target,
    description: 'Average conversion rate'
  },
  {
    title: 'Total Orders',
    value: '1,423',
    change: 15.3,
    changeType: 'increase',
    icon: ShoppingCart,
    description: 'Orders this month'
  }
];

const generateQuickActions = () => [
  {
    id: 1,
    icon: Plus,
    title: 'Create Campaign',
    description: 'Launch a new marketing campaign',
    highlight: true,
    onClick: () => console.log('Create campaign')
  },
  {
    id: 2,
    icon: Users,
    title: 'Add Customer',
    description: 'Register a new customer',
    onClick: () => console.log('Add customer')
  },
  {
    id: 3,
    icon: ShoppingCart,
    title: 'New Order',
    description: 'Create a manual order',
    onClick: () => console.log('New order')
  },
  {
    id: 4,
    icon: BarChart3,
    title: 'View Analytics',
    description: 'Deep dive into metrics',
    onClick: () => console.log('View analytics')
  }
];

const generateKPIs = () => [
  {
    title: 'Monthly Goal',
    current: 75,
    target: 100,
    unit: '%',
    description: 'Revenue target progress'
  },
  {
    title: 'Customer Satisfaction',
    current: 4.8,
    target: 5,
    unit: '/5',
    description: 'Average rating'
  },
  {
    title: 'Response Time',
    current: 2.3,
    target: 1,
    unit: 'hrs',
    description: 'Average support response',
    inverse: true
  },
  {
    title: 'Product Quality',
    current: 98,
    target: 100,
    unit: '%',
    description: 'Quality score'
  }
];

export default function EnhancedDashboard() {
  const [activeItem, setActiveItem] = useState('dashboard');
  const [expandedItems, setExpandedItems] = useState(['analytics', 'customers']);
  const [period, setPeriod] = useState('7d');
  const [activityFilter, setActivityFilter] = useState('all');
  const [stats, setStats] = useState([]);
  const [quickActions, setQuickActions] = useState([]);
  const [kpis, setKpis] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading data
    setTimeout(() => {
      setStats(generateMockStats());
      setQuickActions(generateQuickActions());
      setKpis(generateKPIs());
      setIsLoading(false);
    }, 1000);
  }, []);

  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => {
      setStats(generateMockStats());
      setKpis(generateKPIs());
      setIsLoading(false);
    }, 500);
  };

  return (
    <DashboardLayout
      activeItem={activeItem}
      setActiveItem={setActiveItem}
      expandedItems={expandedItems}
      setExpandedItems={setExpandedItems}
    >
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="space-y-6"
      >
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Analytics Dashboard
            </h1>
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              Real-time insights and performance metrics
            </p>
          </div>
          <div className="flex items-center gap-3 mt-4 md:mt-0">
            <Button variant="outline" size="sm" onClick={handleRefresh}>
              <Activity className="w-4 h-4 mr-2" />
              Refresh
            </Button>
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
            <Button size="sm">
              <Plus className="w-4 h-4 mr-2" />
              New Report
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="activity">Activity</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {stats.map((stat, index) => (
                <EnhancedStatCard
                  key={index}
                  {...stat}
                  loading={isLoading}
                  delay={index * 0.1}
                />
              ))}
            </div>

            {/* KPI Progress */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
              {kpis.map((kpi, index) => (
                <Card key={index}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-sm font-medium text-gray-600">{kpi.title}</h3>
                      <Badge variant="outline" className="text-xs">
                        {kpi.current}{kpi.unit}
                      </Badge>
                    </div>
                    <Progress 
                      value={kpi.inverse ? ((kpi.target - kpi.current) / kpi.target) * 100 : (kpi.current / kpi.target) * 100} 
                      className="mb-2"
                    />
                    <p className="text-xs text-gray-500">{kpi.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <RevenueChart period={period} setPeriod={setPeriod} />
              <UserActivityChart />
              <TrafficSourcesChart />
            </div>

            {/* Quick Actions */}
            <div>
              <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
              <QuickActions actions={quickActions} loading={isLoading} />
            </div>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <RevenueChart period={period} setPeriod={setPeriod} />
              <ConversionRateChart />
              <UserActivityChart />
              <TrafficSourcesChart />
            </div>
            
            <Card>
              <CardHeader>
                <CardTitle>Performance Metrics</CardTitle>
                <CardDescription>Detailed breakdown of key performance indicators</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { metric: 'Page Load Time', value: '1.2s', change: -15, status: 'good' },
                    { metric: 'Bounce Rate', value: '32.4%', change: -8, status: 'good' },
                    { metric: 'Session Duration', value: '4m 32s', change: 12, status: 'good' },
                    { metric: 'Error Rate', value: '0.2%', change: -25, status: 'excellent' }
                  ].map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium">{item.metric}</p>
                        <p className="text-sm text-gray-500">{item.value}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-sm font-medium ${
                          item.change > 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {item.change > 0 ? '+' : ''}{item.change}%
                        </span>
                        <Badge variant={item.status === 'excellent' ? 'default' : 'secondary'}>
                          {item.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Activity Tab */}
          <TabsContent value="activity" className="space-y-6">
            <ActivityFilters activeFilter={activityFilter} onFilterChange={setActivityFilter} />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <ActivityFeed filter={activityFilter} onRefresh={handleRefresh} />
              </div>
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Activity Summary</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {[
                        { label: 'Total Activities', value: '156', change: 12 },
                        { label: 'High Priority', value: '23', change: -5 },
                        { label: 'Resolved Today', value: '45', change: 18 },
                        { label: 'Pending', value: '12', change: -8 }
                      ].map((item, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">{item.label}</span>
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{item.value}</span>
                            <span className={`text-xs ${
                              item.change > 0 ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {item.change > 0 ? '↑' : '↓'} {Math.abs(item.change)}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Recent Alerts</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {[
                        { type: 'warning', message: 'Server load high' },
                        { type: 'error', message: 'Payment gateway issue' },
                        { type: 'info', message: 'Backup completed' }
                      ].map((alert, index) => (
                        <div key={index} className={`p-2 rounded text-sm ${
                          alert.type === 'error' ? 'bg-red-50 text-red-700' :
                          alert.type === 'warning' ? 'bg-yellow-50 text-yellow-700' :
                          'bg-orange-50 text-orange-700'
                        }`}>
                          {alert.message}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Reports Tab */}
          <TabsContent value="reports" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Reports</CardTitle>
                  <CardDescription>Your latest generated reports</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {[
                      { name: 'Monthly Revenue Report', date: '2024-01-15', status: 'completed' },
                      { name: 'Customer Analytics', date: '2024-01-14', status: 'completed' },
                      { name: 'Product Performance', date: '2024-01-13', status: 'processing' }
                    ].map((report, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <p className="font-medium">{report.name}</p>
                          <p className="text-sm text-gray-500">{report.date}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant={report.status === 'completed' ? 'default' : 'secondary'}>
                            {report.status}
                          </Badge>
                          <Button variant="ghost" size="sm">
                            <Eye className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Scheduled Reports</CardTitle>
                  <CardDescription>Automated report generation</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {[
                      { name: 'Weekly Summary', frequency: 'Every Monday', next: '2024-01-22' },
                      { name: 'Monthly Analytics', frequency: '1st of month', next: '2024-02-01' },
                      { name: 'Quarterly Review', frequency: 'Every quarter', next: '2024-04-01' }
                    ].map((report, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <p className="font-medium">{report.name}</p>
                          <p className="text-sm text-gray-500">{report.frequency}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium">Next: {report.next}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </motion.div>
    </DashboardLayout>
  );
}
