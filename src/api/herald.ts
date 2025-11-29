import apiClient from '../lib/api';

export interface SendMessageRequest {
  channel: string;
  recipient: string;
  subject: string;
  content: string;
  priority?: string; // normal, high, critical
  metadata?: Record<string, any>;
}

export interface ScheduleAnnouncementRequest {
  title: string;
  content: string;
  scope: string; // organization, guild, campaign
  scope_id: string;
  channels: string[];
  scheduled_at: string;
  recipients_count?: number;
}

export interface CreateTemplateRequest {
  name: string;
  template_type: string;
  subject_template: string;
  content_template: string;
  variables?: string[];
}

export interface TrackDeliveryRequest {
  message_id?: string;
  announcement_id?: string;
  period_days?: number;
}

export interface GetReportRequest {
  period_days?: number;
}

export const heraldApi = {
  // Messages
  sendMessage: (data: SendMessageRequest) => 
    apiClient.request('/lords/herald/messages/send', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getMessages: (limit: number = 10) => 
    apiClient.request(`/lords/herald/messages?limit=${limit}`),

  getMessage: (id: string) => 
    apiClient.request(`/lords/herald/messages/${id}`),

  // Announcements
  scheduleAnnouncement: (data: ScheduleAnnouncementRequest) => 
    apiClient.request('/lords/herald/announcements/schedule', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getAnnouncements: (limit: number = 10) => 
    apiClient.request(`/lords/herald/announcements?limit=${limit}`),

  getAnnouncement: (id: string) => 
    apiClient.request(`/lords/herald/announcements/${id}`),

  // Templates
  createTemplate: (data: CreateTemplateRequest) => 
    apiClient.request('/lords/herald/templates/create', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getTemplates: () => 
    apiClient.request('/lords/herald/templates'),

  getTemplate: (id: string) => 
    apiClient.request(`/lords/herald/templates/${id}`),

  // Delivery Tracking
  trackDelivery: (data: TrackDeliveryRequest) => 
    apiClient.request('/lords/herald/delivery/track', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Reporting
  getCommunicationReport: (data: GetReportRequest) => 
    apiClient.request('/lords/herald/reporting/communication-report', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  getReports: (limit: number = 10) => 
    apiClient.request(`/lords/herald/reports?limit=${limit}`),

  // Status
  getStatus: () => 
    apiClient.request('/lords/herald/status')
};

export default heraldApi;
