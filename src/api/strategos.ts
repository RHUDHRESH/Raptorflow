import apiClient from '../lib/api';

export interface CreateExecutionPlanRequest {
  plan_name: string;
  description?: string;
  objectives: string[];
  target_guilds: string[];
  start_date?: string;
  end_date: string;
}

export interface AssignTaskRequest {
  task_name: string;
  description: string;
  assigned_guild: string;
  assigned_agent: string;
  estimated_hours: number;
  deadline: string;
  priority: string; // critical, high, normal, low, deferred
  plan_id?: string;
  dependencies?: string[];
}

export interface AllocateResourceRequest {
  resource_type: string; // agent, budget, time, compute, storage, bandwidth
  resource_name: string;
  quantity: number;
  unit: string;
  assigned_to: string;
  duration_hours?: number;
}

export interface TrackProgressRequest {
  task_id: string;
  progress_percent: number;
  actual_hours: number;
  status: string; // planned, ready, active, in_progress, paused, blocked, completed, failed, cancelled
  blockers?: string[];
}

export const strategosApi = {
  // Execution Plans
  createExecutionPlan: (data: CreateExecutionPlanRequest) => 
    apiClient.request('/lords/strategos/plans/create', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  listExecutionPlans: (status?: string) => 
    apiClient.request(`/lords/strategos/plans${status ? `?status=${status}` : ''}`),

  getExecutionPlan: (id: string) => 
    apiClient.request(`/lords/strategos/plans/${id}`),

  getActivePlans: () => 
    apiClient.request('/lords/strategos/active-plans'),

  optimizeTimeline: (planId: string) => 
    apiClient.request(`/lords/strategos/plans/${planId}/optimize-timeline`, {
      method: 'POST'
    }),

  // Tasks
  assignTask: (data: AssignTaskRequest) => 
    apiClient.request('/lords/strategos/tasks/assign', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  listTasks: (status?: string) => 
    apiClient.request(`/lords/strategos/tasks${status ? `?status=${status}` : ''}`),

  getTask: (id: string) => 
    apiClient.request(`/lords/strategos/tasks/${id}`),

  getActiveTasks: () => 
    apiClient.request('/lords/strategos/active-tasks'),

  trackProgress: (taskId: string, data: Omit<TrackProgressRequest, 'task_id'>) => 
    apiClient.request(`/lords/strategos/tasks/${taskId}/progress`, {
      method: 'POST',
      body: JSON.stringify({ ...data, task_id: taskId })
    }),

  // Resources
  allocateResource: (data: AllocateResourceRequest) => 
    apiClient.request('/lords/strategos/resources/allocate', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getResourceUtilization: () => 
    apiClient.request('/lords/strategos/resources/utilization'),

  // Status
  getStatus: () => 
    apiClient.request('/lords/strategos/status')
};

export default strategosApi;
