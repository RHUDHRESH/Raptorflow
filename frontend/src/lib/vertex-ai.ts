import { createClient } from '@supabase/supabase-js';
import { AI_CONFIG, validateModelUsage, getUniversalModel } from './ai-config';
import { costTracker, calculateCost } from './cost-tracker';

interface AIRequest {
  prompt: string;
  model?: string;
  max_tokens?: number;
  temperature?: number;
  useDirectAPI?: boolean;
}

interface AIResponse {
  content: string;
  model: string;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export class VertexAIService {
  private static instance: VertexAIService;
  private backendUrl: string;

  constructor() {
    this.backendUrl = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  }

  static getInstance(): VertexAIService {
    if (!VertexAIService.instance) {
      VertexAIService.instance = new VertexAIService();
    }
    return VertexAIService.instance;
  }

  async generateContent(request: AIRequest): Promise<AIResponse> {
    // ENFORCE UNIVERSAL MODEL USAGE
    const universalModel = validateModelUsage(request.model || getUniversalModel());

    try {
      // Get auth token
      const token = await this.getAuthToken();
      
      const response = await fetch(`${this.backendUrl}/api/v1/ai/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          prompt: request.prompt,
          model: universalModel,
          max_tokens: request.max_tokens || AI_CONFIG.DEFAULT_MAX_TOKENS,
          temperature: request.temperature || AI_CONFIG.DEFAULT_TEMPERATURE,
        })
      });

      if (!response.ok) {
        throw new Error(`AI generation failed: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Track cost
      const tokens = result.usage?.total_tokens || 0;
      const cost = calculateCost(tokens, universalModel);
      costTracker.trackUsage({
        model: universalModel,
        tokens,
        cost,
        operation: 'ai_generate'
      });
      
      return {
        content: result.content,
        model: universalModel,
        usage: result.usage || {
          prompt_tokens: 0,
          completion_tokens: 0,
          total_tokens: 0
        }
      };
    } catch (error) {
      console.error('Vertex AI error:', error);
      throw error;
    }
  }

  private async getAuthToken(): Promise<string> {
    // Get Supabase session token
    const { data: { session } } = await supabase.auth.getSession();
    if (!session?.access_token) {
      throw new Error('No authentication token available');
    }
    return session.access_token;
  }

  async generateMarketingCopy(product: string, targetAudience: string): Promise<string> {
    const prompt = `Generate compelling marketing copy for a product called "${product}" targeting ${targetAudience}.
    Include a headline, subheadline, and call-to-action. Keep it under 200 words.`;

    const response = await this.generateContent({
      prompt,
      model: getUniversalModel(),
      temperature: 0.8
    });

    return response.content;
  }

  async generateSEOKeywords(content: string): Promise<string[]> {
    const prompt = `Extract 10 relevant SEO keywords from this content: "${content}".
    Return only the keywords as a comma-separated list.`;

    const response = await this.generateContent({
      prompt,
      model: getUniversalModel(),
      temperature: 0.3
    });

    return response.content.split(',').map(k => k.trim()).filter(k => k.length > 0);
  }

  async generateEmailSubject(content: string): Promise<string> {
    const prompt = `Write an engaging email subject line for this content: "${content}".
    Make it compelling and under 50 characters.`;

    const response = await this.generateContent({
      prompt,
      model: getUniversalModel(),
      temperature: 0.9
    });

    return response.content;
  }

  async generateSocialMediaPost(content: string, platform: 'twitter' | 'linkedin' | 'instagram'): Promise<string> {
    const platformConstraints = {
      twitter: '280 characters max, include hashtags',
      linkedin: 'Professional tone, 1300 characters max',
      instagram: 'Visual-first approach, engaging and casual'
    };

    const prompt = `Create a ${platform} post for this content: "${content}".
    Constraints: ${platformConstraints[platform]}`;

    const response = await this.generateContent({
      prompt,
      model: getUniversalModel(),
      temperature: 0.8
    });

    return response.content;
  }

  async analyzeContentPerformance(content: string): Promise<{
    sentiment: 'positive' | 'negative' | 'neutral';
    engagement_score: number;
    suggestions: string[];
  }> {
    const prompt = `Analyze this content for marketing effectiveness: "${content}".
    Provide:
    1. Sentiment (positive/negative/neutral)
    2. Engagement score (0-100)
    3. 3 specific suggestions for improvement
    Return as JSON format.`;

    const response = await this.generateContent({
      prompt,
      model: getUniversalModel(),
      temperature: 0.2
    });

    try {
      return JSON.parse(response.content);
    } catch {
      return {
        sentiment: 'neutral',
        engagement_score: 50,
        suggestions: ['Consider adding more compelling language', 'Include a clear call-to-action', 'Add relevant hashtags']
      };
    }
  }

  private async getCurrentUserId(): Promise<string> {
    // Get current user from Supabase auth
    const { data: { session } } = await supabase.auth.getSession();
    return session?.user?.id || 'anonymous';
  }
}

export const vertexAI = VertexAIService.getInstance();
