/**
 * API Client for RaptorFlow Backend
 * Centralized HTTP client for all API requests
 */

const API_BASE_URL = '/api/v1';

class APIClient {
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;

        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
                ...options,
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }

    // Dashboard
    async getDashboardStats() {
        return this.request('/analytics/dashboard');
    }

    // Campaigns
    async getCampaigns() {
        return this.request('/campaigns');
    }

    async getCampaign(id) {
        return this.request(`/campaigns/${id}`);
    }

    // Matrix/Strategy
    async getMatrixData() {
        return this.request('/strategy/matrix');
    }
}

export const apiClient = new APIClient();
export default apiClient;
