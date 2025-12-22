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
        this.baseUrl = process.env.NEXT_PUBLIC_SPINE_URL || 'http://localhost:8080';
        this.apiKey = process.env.RF_INTERNAL_KEY || '';
    }

    private async request<T>(path: string, options: RequestInit): Promise<T> {
        const url = `${this.baseUrl}${path}`;
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'X-API-KEY': this.apiKey,
                ...options.headers,
            },
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw {
                error: `Spine Request Failed: ${response.statusText}`,
                code: errorData.code || 'UNKNOWN',
                detail: errorData.detail || 'No further details provided.',
            } as SpineError;
        }

        return response.json();
    }

    /**
     * Triggers the full Cognitive Spine (A00-A10)
     */
    async createAsset(prompt: string, workspaceId: string, userId: string, threadId?: string): Promise<SpineResponse> {
        // Implement exponential backoff retry for production
        let retries = 3;
        while (retries > 0) {
            try {
                return await this.request<SpineResponse>('/v2/muse/create', {
                    method: 'POST',
                    body: JSON.stringify({ prompt, workspace_id: workspaceId, user_id: userId, thread_id: threadId }),
                });
            } catch (err) {
                retries--;
                if (retries === 0) throw err;
                await new Promise(res => setTimeout(res, 1000 * (3 - retries)));
            }
        }
        throw new Error("Unreachable");
    }

    async checkHealth(): Promise<{ status: string }> {
        return this.request<{ status: string }>('/health', { method: 'GET' });
    }
}

export const spine = new SpineClient();
