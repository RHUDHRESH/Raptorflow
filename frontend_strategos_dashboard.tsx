// frontend/src/components/council/StrategosDashboard.tsx
// RaptorFlow Codex - Strategos Lord Dashboard
// Phase 2A Week 5 - Execution Management & Resource Allocation

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { AlertCircle, CheckCircle, Clock, Zap, Target, TrendingUp } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { api } from '@/services/api';

interface ExecutionPlan {
  id: string;
  name: string;
  description: string;
  objectives: string[];
  target_guilds: string[];
  status: string;
  progress_percent: number;
  total_hours: number;
  actual_hours: number;
  created_at: string;
}

interface ExecutionTask {
  id: string;
  name: string;
  assigned_guild: string;
  assigned_agent: string;
  estimated_hours: number;
  actual_hours: number;
  deadline: string;
  priority: string;
  status: string;
  progress_percent: number;
  blockers: string[];
  created_at: string;
}

interface StrategosMetrics {
  total_plans_created: number;
  total_tasks_assigned: number;
  total_resources_allocated: number;
  task_completion_rate: number;
  on_time_delivery_percent: number;
  active_plans: number;
  active_tasks: number;
}

export const StrategosDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<StrategosMetrics | null>(null);
  const [plans, setPlans] = useState<ExecutionPlan[]>([]);
  const [tasks, setTasks] = useState<ExecutionTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'plans' | 'tasks' | 'resources' | 'tracking'>('plans');
  const [showNewPlanForm, setShowNewPlanForm] = useState(false);
  const [showNewTaskForm, setShowNewTaskForm] = useState(false);

  const { data: wsData, send: wsSend, isConnected } = useWebSocket(
    'ws://localhost:8000/ws/lords/strategos',
    { reconnectInterval: 3000 }
  );

  // ========================================================================
  // DATA FETCHING
  // ========================================================================

  const fetchMetrics = useCallback(async () => {
    try {
      const response = await api.get('/lords/strategos/status');
      setMetrics(response.data.performance);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  }, []);

  const fetchPlans = useCallback(async () => {
    try {
      const response = await api.get('/lords/strategos/plans');
      setPlans(response.data);
    } catch (error) {
      console.error('Failed to fetch plans:', error);
    }
  }, []);

  const fetchTasks = useCallback(async () => {
    try {
      const response = await api.get('/lords/strategos/tasks');
      setTasks(response.data);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    }
  }, []);

  useEffect(() => {
    const initializeData = async () => {
      await Promise.all([fetchMetrics(), fetchPlans(), fetchTasks()]);
      setLoading(false);
    };

    initializeData();

    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, [fetchMetrics, fetchPlans, fetchTasks]);

  useEffect(() => {
    if (wsData?.type === 'plan_created' || wsData?.type === 'task_assigned') {
      fetchMetrics();
      if (activeTab === 'plans') fetchPlans();
      if (activeTab === 'tasks') fetchTasks();
    }
  }, [wsData, activeTab, fetchMetrics, fetchPlans, fetchTasks]);

  // ========================================================================
  // HANDLERS
  // ========================================================================

  const handleCreatePlan = async (name: string, description: string, objectives: string[], guilds: string[], endDate: string) => {
    try {
      await api.post('/lords/strategos/plans/create', {
        plan_name: name,
        description: description,
        objectives: objectives,
        target_guilds: guilds,
        end_date: endDate
      });
      setShowNewPlanForm(false);
      await fetchPlans();
      await fetchMetrics();
    } catch (error) {
      console.error('Failed to create plan:', error);
      alert('Failed to create plan');
    }
  };

  const handleAssignTask = async (taskName: string, guild: string, agent: string, hours: number, deadline: string, priority: string) => {
    try {
      await api.post('/lords/strategos/tasks/assign', {
        task_name: taskName,
        description: '',
        assigned_guild: guild,
        assigned_agent: agent,
        estimated_hours: hours,
        deadline: deadline,
        priority: priority
      });
      setShowNewTaskForm(false);
      await fetchTasks();
      await fetchMetrics();
    } catch (error) {
      console.error('Failed to assign task:', error);
      alert('Failed to assign task');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <Clock className="w-12 h-12 animate-spin mx-auto mb-4" />
          <p className="text-lg font-semibold">Strategos initializing...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 min-h-screen">
      {/* HEADER */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white flex items-center gap-3">
              <span className="text-5xl">⚔️</span>
              Strategos Lord
            </h1>
            <p className="text-slate-300 mt-2">Execution Management & Resource Allocation</p>
          </div>
          <div className="text-right">
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg ${isConnected ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
              {isConnected ? 'Connected' : 'Disconnected'}
            </div>
          </div>
        </div>
      </div>

      {/* METRICS CARDS */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard
          icon={<Target className="w-6 h-6 text-blue-400" />}
          label="Active Plans"
          value={metrics?.active_plans || 0}
          subtext={`${metrics?.total_plans_created || 0} total`}
          gradient="from-blue-600 to-blue-400"
        />
        <MetricCard
          icon={<Zap className="w-6 h-6 text-yellow-400" />}
          label="Active Tasks"
          value={metrics?.active_tasks || 0}
          subtext={`${metrics?.total_tasks_assigned || 0} total`}
          gradient="from-yellow-600 to-yellow-400"
        />
        <MetricCard
          icon={<CheckCircle className="w-6 h-6 text-green-400" />}
          label="Completion Rate"
          value={`${((metrics?.task_completion_rate || 0)).toFixed(1)}%`}
          subtext="Task success"
          gradient="from-green-600 to-green-400"
        />
        <MetricCard
          icon={<TrendingUp className="w-6 h-6 text-purple-400" />}
          label="On-Time Delivery"
          value={`${((metrics?.on_time_delivery_percent || 0)).toFixed(1)}%`}
          subtext="Meeting deadlines"
          gradient="from-purple-600 to-purple-400"
        />
      </div>

      {/* TAB NAVIGATION */}
      <div className="flex gap-4 border-b border-slate-700">
        <button
          onClick={() => setActiveTab('plans')}
          className={`px-4 py-3 font-semibold transition ${
            activeTab === 'plans'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-slate-400 hover:text-slate-300'
          }`}
        >
          📋 Execution Plans
        </button>
        <button
          onClick={() => setActiveTab('tasks')}
          className={`px-4 py-3 font-semibold transition ${
            activeTab === 'tasks'
              ? 'text-yellow-400 border-b-2 border-yellow-400'
              : 'text-slate-400 hover:text-slate-300'
          }`}
        >
          📌 Task Assignments
        </button>
        <button
          onClick={() => setActiveTab('resources')}
          className={`px-4 py-3 font-semibold transition ${
            activeTab === 'resources'
              ? 'text-green-400 border-b-2 border-green-400'
              : 'text-slate-400 hover:text-slate-300'
          }`}
        >
          💾 Resources
        </button>
        <button
          onClick={() => setActiveTab('tracking')}
          className={`px-4 py-3 font-semibold transition ${
            activeTab === 'tracking'
              ? 'text-purple-400 border-b-2 border-purple-400'
              : 'text-slate-400 hover:text-slate-300'
          }`}
        >
          📊 Progress Tracking
        </button>
      </div>

      {/* TAB CONTENT */}
      <div>
        {activeTab === 'plans' && <ExecutionPlansTab plans={plans} onCreatePlan={handleCreatePlan} />}
        {activeTab === 'tasks' && <TaskAssignmentsTab tasks={tasks} onAssignTask={handleAssignTask} />}
        {activeTab === 'resources' && <ResourcesTab />}
        {activeTab === 'tracking' && <ProgressTrackingTab tasks={tasks} />}
      </div>
    </div>
  );
};

// ============================================================================
// METRIC CARD COMPONENT
// ============================================================================

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subtext: string;
  gradient: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ icon, label, value, subtext, gradient }) => (
  <Card className={`bg-gradient-to-br ${gradient} bg-opacity-10 border-0`}>
    <CardContent className="p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-slate-400 text-sm">{label}</p>
          <p className="text-3xl font-bold text-white mt-2">{value}</p>
          <p className="text-slate-400 text-xs mt-2">{subtext}</p>
        </div>
        <div className="text-4xl opacity-20">{icon}</div>
      </div>
    </CardContent>
  </Card>
);

// ============================================================================
// EXECUTION PLANS TAB
// ============================================================================

interface ExecutionPlansTabProps {
  plans: ExecutionPlan[];
  onCreatePlan: (name: string, description: string, objectives: string[], guilds: string[], endDate: string) => void;
}

const ExecutionPlansTab: React.FC<ExecutionPlansTabProps> = ({ plans, onCreatePlan }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    objectives: [''],
    guilds: [''],
    endDate: ''
  });

  const handleCreateClick = () => {
    const validObjectives = formData.objectives.filter(o => o.trim());
    const validGuilds = formData.guilds.filter(g => g.trim());

    if (formData.name && validObjectives.length > 0 && validGuilds.length > 0 && formData.endDate) {
      onCreatePlan(formData.name, formData.description, validObjectives, validGuilds, formData.endDate);
    } else {
      alert('Please fill in all required fields');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'planned': return 'bg-gray-100 text-gray-800';
      case 'active': return 'bg-blue-100 text-blue-800';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-4">
      {/* Create Plan Form */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white text-lg">Create Execution Plan</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-slate-300 text-sm block mb-2">Plan Name</label>
            <Input
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Q2 Marketing Campaign"
              className="bg-slate-900 border-slate-600 text-white"
            />
          </div>
          <div>
            <label className="text-slate-300 text-sm block mb-2">End Date</label>
            <Input
              type="date"
              value={formData.endDate}
              onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
              className="bg-slate-900 border-slate-600 text-white"
            />
          </div>
          <Button
            onClick={handleCreateClick}
            disabled={!formData.name}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white"
          >
            Create Plan
          </Button>
        </CardContent>
      </Card>

      {/* Plans List */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white text-lg">Active Plans</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {plans.map((plan) => (
              <div key={plan.id} className="border border-slate-700 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="text-white font-semibold">{plan.name}</h4>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${getStatusColor(plan.status)}`}>
                    {plan.status}
                  </span>
                </div>
                <p className="text-slate-400 text-sm mb-3">{plan.description}</p>
                <div className="w-full bg-slate-700 rounded-full h-2 mb-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${plan.progress_percent}%` }}
                  />
                </div>
                <div className="flex gap-4 text-xs text-slate-400">
                  <span>Progress: {plan.progress_percent}%</span>
                  <span>Hours: {plan.actual_hours}/{plan.total_hours}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// ============================================================================
// TASK ASSIGNMENTS TAB
// ============================================================================

interface TaskAssignmentsTabProps {
  tasks: ExecutionTask[];
  onAssignTask: (name: string, guild: string, agent: string, hours: number, deadline: string, priority: string) => void;
}

const TaskAssignmentsTab: React.FC<TaskAssignmentsTabProps> = ({ tasks, onAssignTask }) => {
  const [formData, setFormData] = useState({
    name: '',
    guild: '',
    agent: '',
    hours: 8,
    deadline: '',
    priority: 'normal'
  });

  const handleAssignClick = () => {
    if (formData.name && formData.guild && formData.agent && formData.deadline) {
      onAssignTask(formData.name, formData.guild, formData.agent, formData.hours, formData.deadline, formData.priority);
    } else {
      alert('Please fill in all required fields');
    }
  };

  const priorityColors: Record<string, string> = {
    critical: 'bg-red-100 text-red-800',
    high: 'bg-orange-100 text-orange-800',
    normal: 'bg-yellow-100 text-yellow-800',
    low: 'bg-green-100 text-green-800',
    deferred: 'bg-blue-100 text-blue-800'
  };

  const statusColors: Record<string, string> = {
    planned: 'text-gray-400',
    ready: 'text-blue-400',
    active: 'text-yellow-400',
    in_progress: 'text-yellow-400',
    blocked: 'text-red-400',
    completed: 'text-green-400',
    failed: 'text-red-600'
  };

  return (
    <div className="space-y-4">
      {/* Assign Task Form */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white text-lg">Assign Task</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-slate-300 text-sm block mb-2">Task Name</label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Task name..."
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
            <div>
              <label className="text-slate-300 text-sm block mb-2">Priority</label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                className="w-full px-3 py-2 bg-slate-900 text-white rounded border border-slate-600"
              >
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="normal">Normal</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="text-slate-300 text-sm block mb-2">Guild</label>
              <Input
                value={formData.guild}
                onChange={(e) => setFormData({ ...formData, guild: e.target.value })}
                placeholder="Guild..."
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
            <div>
              <label className="text-slate-300 text-sm block mb-2">Agent</label>
              <Input
                value={formData.agent}
                onChange={(e) => setFormData({ ...formData, agent: e.target.value })}
                placeholder="Agent..."
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
            <div>
              <label className="text-slate-300 text-sm block mb-2">Hours</label>
              <Input
                type="number"
                value={formData.hours}
                onChange={(e) => setFormData({ ...formData, hours: Number(e.target.value) })}
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
          </div>
          <div>
            <label className="text-slate-300 text-sm block mb-2">Deadline</label>
            <Input
              type="date"
              value={formData.deadline}
              onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
              className="bg-slate-900 border-slate-600 text-white"
            />
          </div>
          <Button
            onClick={handleAssignClick}
            disabled={!formData.name}
            className="w-full bg-yellow-600 hover:bg-yellow-700 text-white"
          >
            Assign Task
          </Button>
        </CardContent>
      </Card>

      {/* Tasks List */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white text-lg">Active Tasks</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {tasks.map((task) => (
              <div key={task.id} className="border border-slate-700 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="text-white font-semibold">{task.name}</h4>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${priorityColors[task.priority] || 'bg-gray-100 text-gray-800'}`}>
                    {task.priority}
                  </span>
                </div>
                <p className="text-slate-400 text-sm mb-2">{task.assigned_guild} / {task.assigned_agent}</p>
                <div className="w-full bg-slate-700 rounded-full h-2 mb-2">
                  <div
                    className="bg-yellow-600 h-2 rounded-full"
                    style={{ width: `${task.progress_percent}%` }}
                  />
                </div>
                <div className="flex gap-4 text-xs text-slate-400">
                  <span className={`${statusColors[task.status] || 'text-gray-400'}`}>Status: {task.status}</span>
                  <span>Progress: {task.progress_percent}%</span>
                  <span>Hours: {task.actual_hours}/{task.estimated_hours}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// ============================================================================
// RESOURCES TAB
// ============================================================================

const ResourcesTab: React.FC = () => {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white text-lg">Resource Allocation</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-slate-400 py-8 text-center">
          <p className="text-lg">Resource allocation interface coming soon...</p>
          <p className="text-sm mt-2">Monitor agent allocation, budget utilization, and resource constraints</p>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================================================
// PROGRESS TRACKING TAB
// ============================================================================

interface ProgressTrackingTabProps {
  tasks: ExecutionTask[];
}

const ProgressTrackingTab: React.FC<ProgressTrackingTabProps> = ({ tasks }) => {
  const inProgressTasks = tasks.filter(t => t.status === 'in_progress' || t.status === 'blocked');

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white text-lg">Progress Tracking</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {inProgressTasks.length > 0 ? (
            inProgressTasks.map((task) => (
              <div key={task.id} className="border-l-4 border-purple-500 pl-4 py-2">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="text-white font-semibold">{task.name}</h4>
                  {task.blockers.length > 0 && (
                    <AlertCircle className="w-4 h-4 text-red-400" />
                  )}
                </div>
                <div className="w-full bg-slate-700 rounded-full h-3 mb-2">
                  <div
                    className="bg-purple-600 h-3 rounded-full transition-all"
                    style={{ width: `${task.progress_percent}%` }}
                  />
                </div>
                <div className="text-xs text-slate-400">
                  <p className="mb-1">Progress: {task.progress_percent}% | Hours: {task.actual_hours}/{task.estimated_hours}</p>
                  {task.blockers.length > 0 && (
                    <p className="text-red-400">Blockers: {task.blockers.join(', ')}</p>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="text-slate-400 py-8 text-center">
              <p>No tasks in progress</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
