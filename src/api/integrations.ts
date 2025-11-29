import apiClient from '../lib/api';

export interface Integration {
  id: string;
  workspace_id: string;
  platform: string;
  status: string;
  connected_at: string;
  account_id?: string;
}

export interface IntegrationStatusResponse {
  integrations: Integration[];
  total: number;
  correlation_id: string;
}

export interface PlatformStatusResponse {
  platform: string;
  connected: boolean;
  message?: string;
  id?: string;
  workspace_id?: string;
  status?: string;
  connected_at?: string;
  account_id?: string;
  correlation_id: string;
}

export const integrationsApi = {
  // OAuth
  startOAuthFlow: (platform: string) =>
    apiClient.request(`/integrations/oauth/${platform}/authorize`),

  // Connect manually (e.g. via API key)
  connectPlatform: (platform: string, data: { access_token: string; refresh_token?: string; account_id?: string; metadata?: any }) =>
    apiClient.request(`/integrations/connect/${platform}`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Disconnect
  disconnectPlatform: (platform: string) =>
    apiClient.request(`/integrations/disconnect/${platform}`, { method: 'DELETE' }),

  // Status
  getStatus: () =>
    apiClient.request('/integrations/status'),

  getPlatformStatus: (platform: string) =>
    apiClient.request(`/integrations/${platform}/status`)
};

export default integrationsApi;
