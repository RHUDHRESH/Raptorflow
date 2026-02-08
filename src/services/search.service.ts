import { apiRequest } from "./http";

export type SearchEngine = "duckduckgo" | "brave" | "searx" | "startpage" | "qwant";

export interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  source: string;
  timestamp: string;
  relevance_score: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total_results: number;
  engines_used: string[];
  engine_stats: Record<string, {
    status: string;
    results_count?: number;
    response_time?: number;
    error?: string;
  }>;
  response_time: number;
  timestamp: string;
}

export interface SearchEngineInfo {
  engines: string[];
  descriptions: Record<string, string>;
  features: {
    free: boolean;
    unlimited: boolean;
    no_api_keys_required: boolean;
    multi_engine: boolean;
    deduplication: boolean;
    ranking: boolean;
  };
}

export const searchService = {
  async search(
    workspaceId: string,
    query: string,
    engines: SearchEngine[] = ["duckduckgo", "brave"],
    maxResults: number = 20
  ): Promise<SearchResponse> {
    const enginesParam = engines.join(",");
    return apiRequest<SearchResponse>(
      `/search/?q=${encodeURIComponent(query)}&engines=${enginesParam}&max_results=${maxResults}`,
      {
        method: "GET",
        workspaceId,
      }
    );
  },

  async getHealth(workspaceId: string): Promise<{
    status: string;
    timestamp: string;
    engines: Record<string, { status: string; response_time?: number; error?: string }>;
  }> {
    return apiRequest("/search/health", {
      method: "GET",
      workspaceId,
    });
  },

  async getEngines(workspaceId: string): Promise<SearchEngineInfo> {
    return apiRequest<SearchEngineInfo>("/search/engines", {
      method: "GET",
      workspaceId,
    });
  },

  async getStatus(workspaceId: string): Promise<{
    service: string;
    version: string;
    status: string;
    timestamp: string;
    engines_available: number;
    features: string[];
  }> {
    return apiRequest("/search/status", {
      method: "GET",
      workspaceId,
    });
  },
};
