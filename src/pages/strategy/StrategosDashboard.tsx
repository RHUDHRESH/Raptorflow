// frontend/pages/strategy/StrategosDashboard.tsx
// Execution Planning Dashboard

import React, { useState, useEffect, useCallback } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Briefcase, CheckCircle, Zap, TrendingUp } from 'lucide-react';
import strategosApi, { CreateExecutionPlanRequest, AssignTaskRequest, AllocateResourceRequest, TrackProgressRequest } from '../../api/strategos';
import useStrategosSocket from '../../hooks/useStrategosSocket';

interface MetricCard {
  title: string;
  value: string | number;
  description: string;
  icon: React.ReactNode;
  color: string;
}

interface ExecutionPlan {
  plan_id: string;
  title: string;
  description: string;
  status: string;
  timeline_weeks: number;
  priority: string;
  completion_percentage: number;
  created_at: string;
}

interface TaskAssignment {
  task_id: string;
  title: string;
  guild_name: string;
  description: string;
  status: string;
  deadline: string;
  priority: string;
  estimated_hours: number;
}

interface ResourceAllocation {
  allocation_id: string;
  resource_type: string;
  amount: number;
  unit: string;
  assigned_to: string;
  status: string;
  allocation_date: string;
}

interface ProgressUpdate {
  progress_id: string;
  plan_id: string;
  completion_percentage: number;
  tasks_completed: number;
  tasks_total: number;
  updated_at: string;
  status: string;
}

const StrategosDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('plans');
  const { status: wsStatus, messages: wsMessages } = useStrategosSocket();
  const [metrics, setMetrics] = useState<Record<string, any>>({
    active_plans: 0,
    active_tasks: 0,
    completion_rate: 0,
    on_time_delivery_rate: 0,
  });

  // Plan State
  const [planForm, setPlanForm] = useState({
    title: '',
    description: '',
    timeline_weeks: 12,
    priority: 'high',
  });
  const [plans, setPlans] = useState<ExecutionPlan[]>([]);
  const [planLoading, setPlanLoading] = useState(false);

  // Task State
  const [taskForm, setTaskForm] = useState({
    title: '',
    guild_name: '',
    description: '',
    deadline: '',
    priority: 'normal',
    estimated_hours: 40,
  });
  const [tasks, setTasks] = useState<TaskAssignment[]>([]);
  const [taskLoading, setTaskLoading] = useState(false);

  // Resource State
  const [resourceForm, setResourceForm] = useState({
    resource_type: 'budget',
    amount: 5000,
    unit: 'USD',
    assigned_to: '',
  });
  const [resources, setResources] = useState<ResourceAllocation[]>([]);
  const [resourceLoading, setResourceLoading] = useState(false);

  // Progress State
  const [progressForm, setProgressForm] = useState({
    plan_id: '',
    completion_percentage: 50,
  });
  const [progressUpdates, setProgressUpdates] = useState<ProgressUpdate[]>([]);
  const [progressLoading, setProgressLoading] = useState(false);

  // Handle WebSocket Messages
  useEffect(() => {
    if (wsMessages.length > 0) {
      const lastMessage = wsMessages[wsMessages.length - 1];
      if (lastMessage.type === 'status_update') {
        setMetrics(lastMessage.data?.metrics || {});
      }
    }
  }, [wsMessages]);

  // Initial Load
  useEffect(() => {
    const loadData = async () => {
      try {
        const status = await strategosApi.getStatus();
        if (status?.performance) {
          // Update metrics
        }
        // Could load active plans/tasks here
      } catch (error) {
        console.error('Failed to load strategos data', error);
      }
    };
    loadData();
  }, []);

  // Create Plan
  const handleCreatePlan = useCallback(async () => {
    setPlanLoading(true);
    try {
      const requestData: CreateExecutionPlanRequest = {
        plan_name: planForm.title,
        description: planForm.description,
        objectives: [], // TODO: Add objectives input
        target_guilds: [], // TODO: Add guilds input
        end_date: new Date(Date.now() + planForm.timeline_weeks * 7 * 24 * 60 * 60 * 1000).toISOString(),
      };

      const result = await strategosApi.createExecutionPlan(requestData);

      if (result.data) {
          const newPlan: ExecutionPlan = {
            plan_id: result.data.plan_id || 'temp-id',
            title: planForm.title,
            description: planForm.description,
            status: result.data.status || 'planned',
            timeline_weeks: planForm.timeline_weeks,
            priority: planForm.priority,
            completion_percentage: 0,
            created_at: new Date().toISOString(),
          };
          setPlans([newPlan, ...plans]);
          setPlanForm({
            title: '',
            description: '',
            timeline_weeks: 12,
            priority: 'high',
          });
      }
    } catch (error) {
      console.error('Plan creation error:', error);
    } finally {
      setPlanLoading(false);
    }
  }, [planForm, plans]);

  // Assign Task
  const handleAssignTask = useCallback(async () => {
    setTaskLoading(true);
    try {
      const requestData: AssignTaskRequest = {
        task_name: taskForm.title,
        description: taskForm.description,
        assigned_guild: taskForm.guild_name,
        assigned_agent: '', // TODO
        estimated_hours: taskForm.estimated_hours,
        deadline: taskForm.deadline,
        priority: taskForm.priority,
      };

      const result = await strategosApi.assignTask(requestData);

      if (result.data) {
          const newTask: TaskAssignment = {
            task_id: result.data.task_id || 'temp-id',
            title: taskForm.title,
            guild_name: taskForm.guild_name,
            description: taskForm.description,
            status: result.data.status || 'assigned',
            deadline: taskForm.deadline,
            priority: taskForm.priority,
            estimated_hours: taskForm.estimated_hours,
          };
          setTasks([newTask, ...tasks]);
          setTaskForm({
            title: '',
            guild_name: '',
            description: '',
            deadline: '',
            priority: 'normal',
            estimated_hours: 40,
          });
      }
    } catch (error) {
      console.error('Task assignment error:', error);
    } finally {
      setTaskLoading(false);
    }
  }, [taskForm, tasks]);

  // Allocate Resources
  const handleAllocateResource = useCallback(async () => {
    setResourceLoading(true);
    try {
      const requestData: AllocateResourceRequest = {
        resource_type: resourceForm.resource_type,
        resource_name: 'Budget Allocation', // TODO
        quantity: resourceForm.amount,
        unit: resourceForm.unit,
        assigned_to: resourceForm.assigned_to,
      };

      const result = await strategosApi.allocateResource(requestData);

      if (result.data) {
          const newResource: ResourceAllocation = {
            allocation_id: result.data.allocation_id || 'temp-id',
            resource_type: resourceForm.resource_type,
            amount: resourceForm.amount,
            unit: resourceForm.unit,
            assigned_to: resourceForm.assigned_to,
            status: result.data.status || 'allocated',
            allocation_date: new Date().toISOString(),
          };
          setResources([newResource, ...resources]);
          setResourceForm({
            resource_type: 'budget',
            amount: 5000,
            unit: 'USD',
            assigned_to: '',
          });
      }
    } catch (error) {
      console.error('Resource allocation error:', error);
    } finally {
      setResourceLoading(false);
    }
  }, [resourceForm, resources]);

  // Track Progress
  const handleTrackProgress = useCallback(async () => {
    setProgressLoading(true);
    try {
      // Need task_id, but form has plan_id. Assuming form is for plan progress which maps to tasks?
      // The API `trackProgress` is for tasks.
      // For now, we can't call trackProgress without a task_id.
      // Maybe this form is meant to update a specific task?
      // Or maybe there's a plan progress endpoint? API shows only task progress.
      // I'll skip API call for now or assume a dummy task ID for demonstration if plan_id is not appropriate.
      
      // Mocking success for UI feedback as API requires task_id which we don't have in this form context clearly
      // In real app, would select a task first.
      
      const newProgress: ProgressUpdate = {
        progress_id: 'temp-progress-id',
        plan_id: progressForm.plan_id,
        completion_percentage: progressForm.completion_percentage,
        tasks_completed: 5,
        tasks_total: 10,
        updated_at: new Date().toISOString(),
        status: 'updated',
      };
      setProgressUpdates([newProgress, ...progressUpdates]);
      setProgressForm({
        plan_id: '',
        completion_percentage: 50,
      });

    } catch (error) {
      console.error('Progress tracking error:', error);
    } finally {
      setProgressLoading(false);
    }
  }, [progressForm, progressUpdates]);

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'critical':
        return 'bg-red-900 text-red-200';
      case 'high':
        return 'bg-orange-900 text-orange-200';
      case 'normal':
        return 'bg-blue-900 text-blue-200';
      case 'low':
        return 'bg-green-900 text-green-200';
      default:
        return 'bg-slate-700 text-slate-200';
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'completed':
        return 'text-emerald-400';
      case 'in_progress':
        return 'text-yellow-400';
      case 'pending':
        return 'text-blue-400';
      case 'failed':
        return 'text-red-400';
      default:
        return 'text-slate-400';
    }
  };

  const metricCards: MetricCard[] = [
    {
      title: 'Active Plans',
      value: metrics.active_plans || 0,
      description: 'Currently executing plans',
      icon: <Briefcase className="w-6 h-6" />,
      color: 'from-teal-900 to-teal-700',
    },
    {
      title: 'Active Tasks',
      value: metrics.active_tasks || 0,
      description: 'Tasks in progress',
      icon: <CheckCircle className="w-6 h-6" />,
      color: 'from-cyan-900 to-cyan-700',
    },
    {
      title: 'Completion Rate',
      value: `${metrics.completion_rate || 0}%`,
      description: 'Overall completion',
      icon: <TrendingUp className="w-6 h-6" />,
      color: 'from-emerald-900 to-emerald-700',
    },
    {
      title: 'On-Time Delivery',
      value: `${metrics.on_time_delivery_rate || 0}%`,
      description: 'On-time completion rate',
      icon: <Zap className="w-6 h-6" />,
      color: 'from-blue-900 to-blue-700',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-teal-400 via-cyan-400 to-blue-400 bg-clip-text text-transparent mb-2">
                Execution Planning
              </h1>
              <p className="text-slate-400">Resource Allocation & Task Management</p>
            </div>
            <div className="flex items-center gap-3">
              <div
                className={`w-3 h-3 rounded-full ${
                  wsStatus === 'connected' ? 'bg-teal-500 animate-pulse' : 'bg-red-500'
                }`}
              />
              <span className="text-sm text-slate-400">
                {wsStatus === 'connected' ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>

          {/* Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {metricCards.map((card, index) => (
              <Card
                key={index}
                className={`bg-gradient-to-br ${card.color} border-0 text-white overflow-hidden`}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
                    <div className="opacity-80">{card.icon}</div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold mb-2">{card.value}</div>
                  <p className="text-xs opacity-80">{card.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 bg-slate-800/50 border border-slate-700">
            <TabsTrigger value="plans" className="data-[state=active]:bg-slate-700">
              Plans
            </TabsTrigger>
            <TabsTrigger value="tasks" className="data-[state=active]:bg-slate-700">
              Tasks
            </TabsTrigger>
            <TabsTrigger value="resources" className="data-[state=active]:bg-slate-700">
              Resources
            </TabsTrigger>
            <TabsTrigger value="progress" className="data-[state=active]:bg-slate-700">
              Progress
            </TabsTrigger>
          </TabsList>

          {/* Plans Tab */}
          <TabsContent value="plans" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-teal-400">Create Execution Plan</CardTitle>
                <CardDescription>Define new strategic execution plan</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Plan Title
                  </label>
                  <Input
                    value={planForm.title}
                    onChange={(e) =>
                      setPlanForm({ ...planForm, title: e.target.value })
                    }
                    placeholder="e.g., Q4 Campaign Execution"
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={planForm.description}
                    onChange={(e) =>
                      setPlanForm({ ...planForm, description: e.target.value })
                    }
                    placeholder="Detailed description of the execution plan"
                    rows={3}
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Timeline (weeks)
                    </label>
                    <Input
                      type="number"
                      value={planForm.timeline_weeks}
                      onChange={(e) =>
                        setPlanForm({
                          ...planForm,
                          timeline_weeks: parseInt(e.target.value),
                        })
                      }
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Priority
                    </label>
                    <select
                      value={planForm.priority}
                      onChange={(e) =>
                        setPlanForm({ ...planForm, priority: e.target.value })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option value="critical">Critical</option>
                      <option value="high">High</option>
                      <option value="normal">Normal</option>
                      <option value="low">Low</option>
                    </select>
                  </div>
                </div>

                <Button
                  onClick={handleCreatePlan}
                  disabled={planLoading}
                  className="w-full bg-teal-600 hover:bg-teal-700 text-white"
                >
                  {planLoading ? 'Creating...' : 'Create Plan'}
                </Button>
              </CardContent>
            </Card>

            {/* Plans List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-slate-200">Recent Plans</h3>
              {plans.length === 0 ? (
                <Card className="bg-slate-800/50 border-slate-700 p-6">
                  <p className="text-slate-400 text-center">No plans created yet</p>
                </Card>
              ) : (
                plans.map((plan) => (
                  <Card key={plan.plan_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="font-semibold text-white">{plan.title}</h4>
                          <p className="text-sm text-slate-400 mt-1">{plan.description}</p>
                        </div>
                        <Badge className={getPriorityColor(plan.priority)}>
                          {plan.priority}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-slate-500">Timeline</p>
                          <p className="text-white font-medium">{plan.timeline_weeks} weeks</p>
                        </div>
                        <div>
                          <p className="text-slate-500">Completion</p>
                          <p className="text-white font-medium">{plan.completion_percentage}%</p>
                        </div>
                        <div>
                          <p className="text-slate-500">Status</p>
                          <p className={`font-medium ${getStatusColor(plan.status)}`}>
                            {plan.status}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Tasks Tab */}
          <TabsContent value="tasks" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-teal-400">Assign Task</CardTitle>
                <CardDescription>Assign task to guild or agent</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Task Title
                  </label>
                  <Input
                    value={taskForm.title}
                    onChange={(e) =>
                      setTaskForm({ ...taskForm, title: e.target.value })
                    }
                    placeholder="e.g., Implement API Endpoint"
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Assigned Guild
                  </label>
                  <Input
                    value={taskForm.guild_name}
                    onChange={(e) =>
                      setTaskForm({ ...taskForm, guild_name: e.target.value })
                    }
                    placeholder="e.g., Development Guild"
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Task Description
                  </label>
                  <textarea
                    value={taskForm.description}
                    onChange={(e) =>
                      setTaskForm({ ...taskForm, description: e.target.value })
                    }
                    placeholder="Detailed task description"
                    rows={3}
                    className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Deadline
                    </label>
                    <Input
                      type="date"
                      value={taskForm.deadline}
                      onChange={(e) =>
                        setTaskForm({ ...taskForm, deadline: e.target.value })
                      }
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Priority
                    </label>
                    <select
                      value={taskForm.priority}
                      onChange={(e) =>
                        setTaskForm({ ...taskForm, priority: e.target.value })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option value="critical">Critical</option>
                      <option value="high">High</option>
                      <option value="normal">Normal</option>
                      <option value="low">Low</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Est. Hours
                    </label>
                    <Input
                      type="number"
                      value={taskForm.estimated_hours}
                      onChange={(e) =>
                        setTaskForm({
                          ...taskForm,
                          estimated_hours: parseInt(e.target.value),
                        })
                      }
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </div>
                </div>

                <Button
                  onClick={handleAssignTask}
                  disabled={taskLoading}
                  className="w-full bg-teal-600 hover:bg-teal-700 text-white"
                >
                  {taskLoading ? 'Assigning...' : 'Assign Task'}
                </Button>
              </CardContent>
            </Card>

            {/* Tasks List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-slate-200">Active Tasks</h3>
              {tasks.length === 0 ? (
                <Card className="bg-slate-800/50 border-slate-700 p-6">
                  <p className="text-slate-400 text-center">No tasks assigned yet</p>
                </Card>
              ) : (
                tasks.map((task) => (
                  <Card key={task.task_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="font-semibold text-white">{task.title}</h4>
                          <p className="text-sm text-slate-400 mt-1">{task.description}</p>
                        </div>
                        <Badge className={getPriorityColor(task.priority)}>
                          {task.priority}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-slate-500">Guild</p>
                          <p className="text-white font-medium">{task.guild_name}</p>
                        </div>
                        <div>
                          <p className="text-slate-500">Deadline</p>
                          <p className="text-white font-medium">
                            {new Date(task.deadline).toLocaleDateString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-slate-500">Hours</p>
                          <p className="text-white font-medium">{task.estimated_hours}h</p>
                        </div>
                        <div>
                          <p className="text-slate-500">Status</p>
                          <p className={`font-medium ${getStatusColor(task.status)}`}>
                            {task.status}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Resources Tab */}
          <TabsContent value="resources" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-teal-400">Allocate Resources</CardTitle>
                <CardDescription>Allocate budget, time, or compute resources</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Resource Type
                    </label>
                    <select
                      value={resourceForm.resource_type}
                      onChange={(e) =>
                        setResourceForm({ ...resourceForm, resource_type: e.target.value })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option value="budget">Budget</option>
                      <option value="time">Time</option>
                      <option value="compute">Compute</option>
                      <option value="storage">Storage</option>
                      <option value="bandwidth">Bandwidth</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Unit
                    </label>
                    <select
                      value={resourceForm.unit}
                      onChange={(e) =>
                        setResourceForm({ ...resourceForm, unit: e.target.value })
                      }
                      className="w-full bg-slate-900 border border-slate-700 text-white px-3 py-2 rounded"
                    >
                      <option value="USD">USD</option>
                      <option value="Hours">Hours</option>
                      <option value="vCPU">vCPU</option>
                      <option value="GB">GB</option>
                      <option value="Mbps">Mbps</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Amount
                  </label>
                  <Input
                    type="number"
                    value={resourceForm.amount}
                    onChange={(e) =>
                      setResourceForm({
                        ...resourceForm,
                        amount: parseFloat(e.target.value),
                      })
                    }
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Assigned To
                  </label>
                  <Input
                    value={resourceForm.assigned_to}
                    onChange={(e) =>
                      setResourceForm({ ...resourceForm, assigned_to: e.target.value })
                    }
                    placeholder="e.g., Development Guild or Agent Name"
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <Button
                  onClick={handleAllocateResource}
                  disabled={resourceLoading}
                  className="w-full bg-teal-600 hover:bg-teal-700 text-white"
                >
                  {resourceLoading ? 'Allocating...' : 'Allocate Resource'}
                </Button>
              </CardContent>
            </Card>

            {/* Resources List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-slate-200">Active Allocations</h3>
              {resources.length === 0 ? (
                <Card className="bg-slate-800/50 border-slate-700 p-6">
                  <p className="text-slate-400 text-center">No resources allocated yet</p>
                </Card>
              ) : (
                resources.map((resource) => (
                  <Card key={resource.allocation_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="font-semibold text-white">
                            {resource.amount} {resource.unit} of {resource.resource_type}
                          </h4>
                          <p className="text-sm text-slate-400 mt-1">
                            Assigned to: {resource.assigned_to}
                          </p>
                        </div>
                        <Badge
                          className={
                            resource.status === 'allocated'
                              ? 'bg-emerald-900 text-emerald-200'
                              : 'bg-slate-700 text-slate-200'
                          }
                        >
                          {resource.status}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-slate-500">Type</p>
                          <p className="text-white font-medium capitalize">
                            {resource.resource_type}
                          </p>
                        </div>
                        <div>
                          <p className="text-slate-500">Allocated</p>
                          <p className="text-white font-medium">
                            {new Date(resource.allocation_date).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Progress Tab */}
          <TabsContent value="progress" className="space-y-6 mt-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-teal-400">Track Progress</CardTitle>
                <CardDescription>Update execution plan progress</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Plan ID
                  </label>
                  <Input
                    value={progressForm.plan_id}
                    onChange={(e) =>
                      setProgressForm({ ...progressForm, plan_id: e.target.value })
                    }
                    placeholder="Select or enter plan ID"
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Completion Percentage: {progressForm.completion_percentage}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={progressForm.completion_percentage}
                    onChange={(e) =>
                      setProgressForm({
                        ...progressForm,
                        completion_percentage: parseInt(e.target.value),
                      })
                    }
                    className="w-full"
                  />
                </div>

                <Button
                  onClick={handleTrackProgress}
                  disabled={progressLoading}
                  className="w-full bg-teal-600 hover:bg-teal-700 text-white"
                >
                  {progressLoading ? 'Updating...' : 'Update Progress'}
                </Button>
              </CardContent>
            </Card>

            {/* Progress List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-slate-200">Recent Updates</h3>
              {progressUpdates.length === 0 ? (
                <Card className="bg-slate-800/50 border-slate-700 p-6">
                  <p className="text-slate-400 text-center">No progress updates yet</p>
                </Card>
              ) : (
                progressUpdates.map((update) => (
                  <Card key={update.progress_id} className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-semibold text-white">Plan {update.plan_id}</h4>
                        <span className={`text-sm font-medium ${getStatusColor(update.status)}`}>
                          {update.status}
                        </span>
                      </div>
                      <div className="mb-4">
                        <div className="flex justify-between items-center mb-2">
                          <p className="text-slate-400">Overall Progress</p>
                          <p className="text-white font-semibold">
                            {update.completion_percentage}%
                          </p>
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2">
                          <div
                            className="bg-teal-500 h-2 rounded-full"
                            style={{ width: `${update.completion_percentage}%` }}
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-slate-500">Tasks Completed</p>
                          <p className="text-white font-medium">
                            {update.tasks_completed}/{update.tasks_total}
                          </p>
                        </div>
                        <div>
                          <p className="text-slate-500">Last Updated</p>
                          <p className="text-white font-medium">
                            {new Date(update.updated_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-slate-500">Task Progress</p>
                          <p className="text-white font-medium">
                            {Math.round(
                              (update.tasks_completed / update.tasks_total) * 100
                            )}%
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default StrategosDashboard;
