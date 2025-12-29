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
    // FORCE RELATIVE PATH to use internal Next.js API (avoids hitting dead localhost:8000)
    this.baseUrl = '';
    // this.baseUrl = process.env.NEXT_PUBLIC_API_URL || '';
    this.apiKey = process.env.RF_INTERNAL_KEY || '';
  }

  private async request<T>(path: string, options: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Spine API Error: ${response.status} ${errorText}`);
    }

    return response.json();
  }

  async createAsset(
    prompt: string,
    workspaceId: string,
    userId: string,
    threadId?: string
  ): Promise<SpineResponse> {
    // Redirect to chat endpoint for now as it handles generation too
    return this.chat(prompt, threadId);
  }

  async chat(message: string, threadId?: string): Promise<SpineResponse> {
    // Use the internal Next.js API route
    const result = await this.request<{ response: string; threadId: string }>(
      '/api/muse/chat',
      {
        method: 'POST',
        body: JSON.stringify({
          message,
          threadId,
        }),
      }
    );

    // Map internal API result to SpineResponse contract
    return {
      thread_id: result.threadId,
      asset_content: result.response,
      quality_score: 1.0, // Mocked for internal agent
      status: 'completed',
      iterations: 1,
    };
  }

  async checkHealth(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health', { method: 'GET' });
  }
}

export const spine = new SpineClient();
