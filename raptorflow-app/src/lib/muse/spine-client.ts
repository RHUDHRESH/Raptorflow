/**
 * RaptorFlow V2 Spine Client
 * Industrial-grade communication with the Python Creative Engine.
 */

export interface SpineResponse {
    thread_id: string;
    asset_content: string;
    quality_score: number;
    status: string;
    iterations: number;
}

export interface SpineError {
    error: string;
    code: string;
    detail: string;
}

class SpineClient {
    private baseUrl: string;
    private apiKey: string;

    constructor() {
        this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        this.apiKey = process.env.RF_INTERNAL_KEY || '';
    }

    private async request<T>(path: string, options: RequestInit): Promise<T> {
// ...
    async createAsset(prompt: string, workspaceId: string, userId: string, threadId?: string): Promise<SpineResponse> {
        // Implement exponential backoff retry for production
        let retries = 3;
        while (retries > 0) {
            try {
                return await this.request<SpineResponse>('/v1/muse/create', {
                    method: 'POST',
                    body: JSON.stringify({
                        prompt,
                        workspace_id: workspaceId,
                        tenant_id: userId, // Mapping userId to tenant_id for now
                        thread_id: threadId
                    }),
                });
            } catch (err) {
// ...


    async chat(message: string, threadId?: string): Promise<SpineResponse> {
        return await this.request<SpineResponse>('/v1/muse/create', {
            method: 'POST',
            body: JSON.stringify({
                prompt: message,
                workspace_id: 'default_ws',
                tenant_id: 'default_tenant',
                thread_id: threadId
            }),
        });
    }

    async checkHealth(): Promise<{ status: string }> {
        return this.request<{ status: string }>('/health', { method: 'GET' });
    }
}

export const spine = new SpineClient();
