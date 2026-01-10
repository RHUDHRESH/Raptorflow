import { createClient } from '@supabase/supabase-js';
import { AI_CONFIG, validateModelUsage, getUniversalModel } from './ai-config';

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
  private directAPIKey: string;

  constructor() {
    this.backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
    this.directAPIKey = process.env.NEXT_PUBLIC_VERTEX_AI_API_KEY || '';
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

    if (request.useDirectAPI && this.directAPIKey) {
      return this.generateContentDirect({ ...request, model: universalModel });
    }

    try {
      const response = await fetch(`${this.backendUrl}/ai/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await this.getAuthToken()}`
        },
        body: JSON.stringify({
          prompt: request.prompt,
          model: universalModel, // ALWAYS use universal model
          max_tokens: request.max_tokens || AI_CONFIG.DEFAULT_MAX_TOKENS,
          temperature: request.temperature || AI_CONFIG.DEFAULT_TEMPERATURE,
          user_id: await this.getCurrentUserId()
        })
      });

      if (!response.ok) {
        throw new Error(`AI generation failed: ${response.statusText}`);
      }

      const result = await response.json();
      return {
        content: result.content,
        model: universalModel, // Ensure response uses universal model
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

  private async generateContentDirect(request: AIRequest): Promise<AIResponse> {
    // ENFORCE UNIVERSAL MODEL USAGE
    const universalModel = validateModelUsage(request.model || getUniversalModel());

    try {
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${universalModel}:generateContent?key=${this.directAPIKey}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: request.prompt
            }]
          }],
          generationConfig: {
            temperature: request.temperature || AI_CONFIG.DEFAULT_TEMPERATURE,
            maxOutputTokens: request.max_tokens || AI_CONFIG.DEFAULT_MAX_TOKENS,
          }
        })
      });

      if (!response.ok) {
        throw new Error(`Direct API call failed: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.candidates && result.candidates.length > 0) {
        const content = result.candidates[0].content.parts[0].text;
        return {
          content,
          model: universalModel, // ALWAYS return universal model
          usage: {
            prompt_tokens: result.usageMetadata?.promptTokenCount || 0,
            completion_tokens: result.usageMetadata?.candidatesTokenCount || 0,
            total_tokens: result.usageMetadata?.totalTokenCount || 0
          }
        };
      } else {
        throw new Error('No content generated');
      }
    } catch (error) {
      console.error('Direct Gemini API error:', error);
      throw error;
    }
  }

  async generateMarketingCopy(product: string, targetAudience: string): Promise<string> {
    const prompt = `Generate compelling marketing copy for a product called "${product}" targeting ${targetAudience}.
    Include a headline, subheadline, and call-to-action. Keep it under 200 words.`;

    const response = await this.generateContent({
      prompt,
      model: getUniversalModel(), // ALWAYS use universal model
      temperature: 0.8
    });

    return response.content;
  }

  async generateSEOKeywords(content: string): Promise<string[]> {
    const prompt = `Extract 10 relevant SEO keywords from this content: "${content}".
    Return only the keywords as a comma-separated list.`;

    const response = await this.generateContent({
      prompt,
      model: getUniversalModel(), // ALWAYS use universal model
      temperature: 0.3
    });

    return response.content.split(',').map(k => k.trim()).filter(k => k.length > 0);
  }

  async generateEmailSubject(content: string): Promise<string> {
    const prompt = `Write an engaging email subject line for this content: "${content}".
    Make it compelling and under 50 characters.`;

    const response = await this.generateContent({
      prompt,
      model: getUniversalModel(), // ALWAYS use universal model
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
      model: getUniversalModel(), // ALWAYS use universal model
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
      model: getUniversalModel(), // ALWAYS use universal model
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

  private async getAuthToken(): Promise<string> {
    // In a real implementation, this would get a JWT token
    // For now, return a placeholder
    return 'Bearer your-jwt-token';
  }

  private async getCurrentUserId(): Promise<string> {
    // Get current user from Supabase auth
    const { data: { session } } = await supabase.auth.getSession();
    return session?.user?.id || 'anonymous';
  }
}

export const vertexAI = VertexAIService.getInstance();
