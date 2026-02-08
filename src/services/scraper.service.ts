import { apiRequest } from "./http";

export type ScrapingStrategy = 
  | "conservative" 
  | "balanced" 
  | "aggressive" 
  | "adaptive"
  | "turbo"
  | "optimized"
  | "parallel"
  | "async";

export interface ScrapeRequest {
  url: string;
  user_id: string;
  strategy?: ScrapingStrategy;
  legal_basis?: string;
}

export interface ScrapeResult {
  url: string;
  user_id: string;
  title?: string;
  content?: string;
  readable_text?: string;
  structured_data?: Record<string, unknown>;
  screenshot?: boolean;
  content_length?: number;
  status: "success" | "error";
  error?: string;
  processing_time: number;
  strategy: string;
  timestamp: string;
}

export interface ScraperStrategy {
  name: string;
  description: string;
}

export interface ScraperStats {
  total_scrapes: number;
  cache_size: number;
  current_strategy: string;
  available_strategies: string[];
  timestamp: string;
}

export interface ScraperAnalytics {
  period_days: number;
  total_scrapes: number;
  avg_processing_time: number;
  strategy_performance: Record<string, {
    count: number;
    avg_processing_time: number;
  }>;
  current_strategy: string;
}

export const scraperService = {
  async scrape(workspaceId: string, request: ScrapeRequest): Promise<ScrapeResult> {
    return apiRequest<ScrapeResult>("/scraper/", {
      method: "POST",
      workspaceId,
      body: JSON.stringify(request),
    });
  },

  async getHealth(workspaceId: string): Promise<{ status: string; timestamp: string; current_strategy: string; cache_size: number }> {
    return apiRequest("/scraper/health", {
      method: "GET",
      workspaceId,
    });
  },

  async getStats(workspaceId: string): Promise<ScraperStats> {
    return apiRequest<ScraperStats>("/scraper/stats", {
      method: "GET",
      workspaceId,
    });
  },

  async getAnalytics(workspaceId: string, days: number = 7): Promise<ScraperAnalytics> {
    return apiRequest<ScraperAnalytics>(`/scraper/analytics?days=${days}`, {
      method: "GET",
      workspaceId,
    });
  },

  async getStrategies(workspaceId: string): Promise<{ strategies: ScraperStrategy[]; current_strategy: string }> {
    return apiRequest("/scraper/strategies", {
      method: "GET",
      workspaceId,
    });
  },

  async updateStrategy(workspaceId: string, strategy: ScrapingStrategy): Promise<{ status: string; previous_strategy: string; new_strategy: string }> {
    return apiRequest("/scraper/strategy", {
      method: "POST",
      workspaceId,
      body: JSON.stringify({ strategy }),
    });
  },
};
