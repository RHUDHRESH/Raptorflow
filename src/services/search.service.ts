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
  summary?: {
    status: string;
    text?: string;
    detail?: string;
    model?: string;
    tokens_used?: number;
    cost_usd?: number;
  };
  intensity?: "low" | "medium" | "high";
  execution_mode?: "single" | "council" | "swarm";
  search_profile?: {
    intensity: "low" | "medium" | "high";
    execution_mode: "single" | "council" | "swarm";
    engines: string[];
    max_results: number;
  };
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
    engines?: SearchEngine[],
    maxResults?: number,
    opts: {
      intensity?: "low" | "medium" | "high";
      executionMode?: "single" | "council" | "swarm";
      summarize?: boolean;
    } = {}
  ): Promise<SearchResponse> {
    const params = new URLSearchParams();
    params.set("q", query);
    if (engines && engines.length > 0) {
      params.set("engines", engines.join(","));
    }
    if (typeof maxResults === "number") {
      params.set("max_results", String(maxResults));
    }
    const intensityParam = opts.intensity ? `&intensity=${opts.intensity}` : "";
    const executionModeParam = opts.executionMode ? `&execution_mode=${opts.executionMode}` : "";
    const summarizeParam = opts.summarize === false ? "&summarize=false" : "";
    return apiRequest<SearchResponse>(
      `/search/?${params.toString()}${intensityParam}${executionModeParam}${summarizeParam}`,
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
