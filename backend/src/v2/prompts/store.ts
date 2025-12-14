/**
 * Central Versioned Prompt Store for Orchestrator Agents
 *
 * Manages prompt templates with versioning, A/B testing, and retrieval APIs.
 */

import { redisMemory } from '../../services/redisMemory';

export interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  template: string;
  version: string;
  agentName: string;
  variables: string[];
  metadata: {
    author: string;
    createdAt: string;
    updatedAt: string;
    tags: string[];
    category: string;
    complexity: 'simple' | 'medium' | 'complex';
    estimatedTokens: number;
  };
  validation?: {
    requiredVariables: string[];
    outputFormat?: string;
    safetyChecks?: string[];
  };
  variants?: PromptVariant[];
}

export interface PromptVariant {
  id: string;
  name: string;
  template: string;
  weight: number; // For A/B testing (0-100)
  metrics: {
    usage: number;
    successRate: number;
    averageLatency: number;
  };
}

export interface PromptContext {
  agentName: string;
  brandProfile?: any;
  project?: any;
  inputOverrides?: Record<string, any>;
  contextSnapshot?: Record<string, any>;
}

class PromptStore {
  private readonly cachePrefix = 'prompts';
  private readonly cacheTTL = 3600; // 1 hour

  // In-memory prompt registry (would be loaded from database in production)
  private prompts: Map<string, PromptTemplate> = new Map();

  constructor() {
    this.initializePrompts();
  }

  /**
   * Get prompt template by ID
   */
  async getPrompt(promptId: string): Promise<PromptTemplate | null> {
    // Try cache first
    const cached = await redisMemory.retrieve<PromptTemplate>(`${this.cachePrefix}:${promptId}`);
    if (cached) return cached;

    // Try in-memory registry
    const prompt = this.prompts.get(promptId);
    if (prompt) {
      // Cache for future use
      await redisMemory.store(`${this.cachePrefix}:${promptId}`, prompt, this.cacheTTL);
      return prompt;
    }

    return null;
  }

  /**
   * Get prompt by agent name (latest version)
   */
  async getPromptForAgent(agentName: string): Promise<PromptTemplate | null> {
    // Try cache first
    const cacheKey = `${this.cachePrefix}:agent:${agentName}:latest`;
    const cached = await redisMemory.retrieve<PromptTemplate>(cacheKey);
    if (cached) return cached;

    // Find latest version for agent
    let latestPrompt: PromptTemplate | null = null;
    for (const prompt of this.prompts.values()) {
      if (prompt.agentName === agentName) {
        if (!latestPrompt || this.compareVersions(prompt.version, latestPrompt.version) > 0) {
          latestPrompt = prompt;
        }
      }
    }

    if (latestPrompt) {
      await redisMemory.store(cacheKey, latestPrompt, this.cacheTTL);
    }

    return latestPrompt;
  }

  /**
   * Get prompt by agent name and specific version
   */
  async getPromptForAgentVersion(agentName: string, version: string): Promise<PromptTemplate | null> {
    const cacheKey = `${this.cachePrefix}:agent:${agentName}:v${version}`;
    const cached = await redisMemory.retrieve<PromptTemplate>(cacheKey);
    if (cached) return cached;

    for (const prompt of this.prompts.values()) {
      if (prompt.agentName === agentName && prompt.version === version) {
        await redisMemory.store(cacheKey, prompt, this.cacheTTL);
        return prompt;
      }
    }

    return null;
  }

  /**
   * Render prompt template with variables
   */
  renderPrompt(template: PromptTemplate, context: PromptContext): string {
    let rendered = template.template;

    // Replace standard variables
    const variables = {
      ...context.brandProfile,
      ...context.project,
      ...context.inputOverrides,
      ...context.contextSnapshot,
    };

    // Replace {{variable}} placeholders
    for (const [key, value] of Object.entries(variables)) {
      if (value !== undefined && value !== null) {
        const placeholder = new RegExp(`{{${key}}}`, 'g');
        rendered = rendered.replace(placeholder, String(value));
      }
    }

    // Check for missing required variables
    const missingVars = template.validation?.requiredVariables?.filter(
      varName => !variables[varName]
    ) || [];

    if (missingVars.length > 0) {
      console.warn(`Missing required variables for prompt ${template.id}: ${missingVars.join(', ')}`);
    }

    return rendered;
  }

  /**
   * Get rendered prompt for agent with context
   */
  async getRenderedPromptForAgent(
    agentName: string,
    context: PromptContext,
    version?: string
  ): Promise<string | null> {
    const prompt = version
      ? await this.getPromptForAgentVersion(agentName, version)
      : await this.getPromptForAgent(agentName);

    if (!prompt) return null;

    return this.renderPrompt(prompt, context);
  }

  /**
   * Register new prompt template
   */
  async registerPrompt(prompt: Omit<PromptTemplate, 'id'>): Promise<string> {
    const id = this.generatePromptId(prompt.agentName, prompt.version);

    const fullPrompt: PromptTemplate = {
      ...prompt,
      id,
      metadata: {
        ...prompt.metadata,
        updatedAt: new Date().toISOString(),
      },
    };

    this.prompts.set(id, fullPrompt);

    // Invalidate related caches
    await this.invalidateAgentCache(prompt.agentName);

    return id;
  }

  /**
   * Update prompt template
   */
  async updatePrompt(id: string, updates: Partial<PromptTemplate>): Promise<boolean> {
    const existing = this.prompts.get(id);
    if (!existing) return false;

    const updated: PromptTemplate = {
      ...existing,
      ...updates,
      metadata: {
        ...existing.metadata,
        ...updates.metadata,
        updatedAt: new Date().toISOString(),
      },
    };

    this.prompts.set(id, updated);

    // Invalidate caches
    await this.invalidatePromptCache(id);
    await this.invalidateAgentCache(updated.agentName);

    return true;
  }

  /**
   * List prompts by agent
   */
  async listPromptsByAgent(agentName: string): Promise<PromptTemplate[]> {
    return Array.from(this.prompts.values())
      .filter(prompt => prompt.agentName === agentName)
      .sort((a, b) => this.compareVersions(b.version, a.version)); // Latest first
  }

  /**
   * List all prompts
   */
  async listAllPrompts(): Promise<PromptTemplate[]> {
    return Array.from(this.prompts.values());
  }

  /**
   * Get prompt statistics
   */
  async getPromptStats(): Promise<{
    totalPrompts: number;
    promptsByAgent: Record<string, number>;
    promptsByCategory: Record<string, number>;
  }> {
    const stats = {
      totalPrompts: this.prompts.size,
      promptsByAgent: {} as Record<string, number>,
      promptsByCategory: {} as Record<string, number>,
    };

    for (const prompt of this.prompts.values()) {
      stats.promptsByAgent[prompt.agentName] = (stats.promptsByAgent[prompt.agentName] || 0) + 1;
      stats.promptsByCategory[prompt.metadata.category] =
        (stats.promptsByCategory[prompt.metadata.category] || 0) + 1;
    }

    return stats;
  }

  /**
   * Validate prompt template
   */
  validatePrompt(prompt: Partial<PromptTemplate>): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!prompt.name) errors.push('Name is required');
    if (!prompt.agentName) errors.push('Agent name is required');
    if (!prompt.template) errors.push('Template is required');
    if (!prompt.version) errors.push('Version is required');

    // Validate version format (semver-like)
    if (prompt.version && !/^\d+\.\d+\.\d+$/.test(prompt.version)) {
      errors.push('Version must be in semver format (x.y.z)');
    }

    // Validate template variables
    if (prompt.template) {
      const templateVars = this.extractVariablesFromTemplate(prompt.template);
      const declaredVars = prompt.variables || [];

      const missingVars = templateVars.filter(v => !declaredVars.includes(v));
      if (missingVars.length > 0) {
        errors.push(`Template uses undeclared variables: ${missingVars.join(', ')}`);
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  // =====================================================
  // PRIVATE METHODS
  // =====================================================

  private initializePrompts(): void {
    // Initialize with default orchestrator agent prompts
    // These would typically be loaded from database/files in production
    this.registerDefaultPrompts();
  }

  private async registerDefaultPrompts(): Promise<void> {
    const defaultPrompts: Omit<PromptTemplate, 'id'>[] = [
      {
        name: 'Brand Script Generator',
        description: 'Generate compelling brand scripts for marketing campaigns',
        template: `You are a master brand storyteller creating compelling scripts for {{brandName}}.

BRAND CONTEXT:
- Industry: {{industry}}
- Target Audience: {{targetAudience}}
- Brand Values: {{brandValues}}
- Brand Personality: {{brandPersonality}}
- Key Messaging: {{keyMessaging}}
- Brand Voice: {{brandVoice}}

SCRIPT REQUIREMENTS:
Create a compelling brand script that includes:
1. A strong opening hook that captures attention
2. Emotional connection with the target audience
3. Clear communication of the brand's unique value proposition
4. Brand story elements that highlight authenticity
5. Strong call-to-action that inspires engagement
6. Memorable closing that reinforces brand identity

OUTPUT FORMAT (JSON):
{
  "title": "Script title",
  "script": "Full script content with proper formatting",
  "keyMessages": ["3-5 key messages"],
  "tone": "Overall tone description",
  "estimatedDuration": "Duration estimate (e.g., '2-3 minutes')",
  "targetAudience": "Specific audience segment this script targets"
}

Additional Context: {{context}}

Generate the brand script now:`,
        version: '1.0.0',
        agentName: 'BrandScript',
        variables: ['brandName', 'industry', 'targetAudience', 'brandValues', 'brandPersonality', 'keyMessaging', 'brandVoice', 'context'],
        metadata: {
          author: 'system',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          tags: ['brand', 'storytelling', 'marketing', 'campaigns'],
          category: 'brand',
          complexity: 'complex',
          estimatedTokens: 800,
        },
        validation: {
          requiredVariables: ['brandName'],
          outputFormat: 'Structured brand script with emotional hooks',
          safetyChecks: ['No misleading claims', 'Respect brand voice'],
        },
      },
      {
        name: 'Tagline Generator',
        description: 'Creates memorable, impactful taglines',
        template: `You are a branding expert creating memorable taglines for {{brandName}}.

BRAND CONTEXT:
- Industry: {{industry}}
- Target Audience: {{targetAudience}}
- Brand Values: {{brandValues}}
- Brand Personality: {{brandPersonality}}
- Key Messaging: {{keyMessaging}}

TAGLINE REQUIREMENTS:
Create taglines that are:
1. Concise (3-8 words maximum)
2. Memorable and catchy
3. Aligned with brand personality
4. Differentiated from competitors
5. Emotionally resonant
6. Versatile for multiple uses

OUTPUT FORMAT (JSON):
{
  "primaryTagline": "The main recommended tagline",
  "alternativeTaglines": ["2-3 alternative options"],
  "rationale": "Why this tagline works for the brand",
  "brandAlignment": "How well it aligns with brand values (1-10)",
  "memorability": "How memorable it is (1-10)",
  "uniqueness": "How unique/differentiated it is (1-10)"
}

Additional Context: {{context}}

Generate taglines now:`,
        version: '1.0.0',
        agentName: 'Tagline',
        variables: ['brandName', 'industry', 'targetAudience', 'brandValues', 'brandPersonality', 'keyMessaging', 'context'],
        metadata: {
          author: 'system',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          tags: ['brand', 'tagline', 'messaging', 'positioning'],
          category: 'brand',
          complexity: 'medium',
          estimatedTokens: 400,
        },
        validation: {
          requiredVariables: ['brandName'],
          outputFormat: 'JSON with primary tagline and alternatives',
          safetyChecks: ['No trademark violations', 'Brand-appropriate language'],
        },
      },
      {
        name: 'Product Description Writer',
        description: 'Creates compelling product descriptions',
        template: `You are a product marketing expert writing compelling descriptions for {{brandName}} products.

BRAND CONTEXT:
- Industry: {{industry}}
- Target Audience: {{targetAudience}}
- Brand Values: {{brandValues}}
- Brand Personality: {{brandPersonality}}

PRODUCT CONTEXT:
- Product Name: {{productName}}
- Key Features: {{keyFeatures}}
- Benefits: {{benefits}}
- Unique Selling Points: {{uniqueSellingPoints}}

DESCRIPTION REQUIREMENTS:
Write product descriptions that:
1. Start with a compelling hook
2. Highlight key benefits over features
3. Connect emotionally with the target audience
4. Include social proof elements
5. End with clear call-to-action
6. Are SEO-optimized where appropriate

OUTPUT FORMAT (JSON):
{
  "shortDescription": "50-100 word summary",
  "longDescription": "200-400 word detailed description",
  "keyFeatures": ["Top 3-5 features"],
  "benefits": ["Corresponding benefits"],
  "callToAction": "Clear CTA phrase",
  "seoKeywords": ["5-7 relevant SEO keywords"]
}

Additional Context: {{context}}

Write the product descriptions now:`,
        version: '1.0.0',
        agentName: 'ProductDescription',
        variables: ['brandName', 'industry', 'targetAudience', 'brandValues', 'brandPersonality', 'productName', 'keyFeatures', 'benefits', 'uniqueSellingPoints', 'context'],
        metadata: {
          author: 'system',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          tags: ['product', 'description', 'marketing', 'conversion'],
          category: 'content',
          complexity: 'medium',
          estimatedTokens: 600,
        },
        validation: {
          requiredVariables: ['brandName', 'productName'],
          outputFormat: 'JSON with short and long descriptions',
          safetyChecks: ['No exaggerated claims', 'Fact-based benefits'],
        },
      },
      {
        name: 'One-Liner Generator',
        description: 'Creates concise, impactful one-liner messages',
        template: `You are a copywriting expert creating powerful one-liners for {{brandName}}.

BRAND CONTEXT:
- Industry: {{industry}}
- Target Audience: {{targetAudience}}
- Brand Personality: {{brandPersonality}}
- Key Messaging: {{keyMessaging}}

ONE-LINER REQUIREMENTS:
Create one-liners that are:
1. Extremely concise (5-15 words)
2. High impact and memorable
3. Perfect for social media or ads
4. Aligned with brand voice
5. Emotionally engaging

CONTEXT: {{context}}
PURPOSE: {{purpose}}

OUTPUT FORMAT (JSON):
{
  "oneLiner": "The primary one-liner",
  "context": "Where this one-liner should be used",
  "tone": "Emotional tone (inspiring, urgent, humorous, etc.)",
  "impact": "Impact rating (1-10)",
  "variations": ["2-3 alternative versions"]
}

Generate the one-liner now:`,
        version: '1.0.0',
        agentName: 'OneLiner',
        variables: ['brandName', 'industry', 'targetAudience', 'brandPersonality', 'keyMessaging', 'context', 'purpose'],
        metadata: {
          author: 'system',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          tags: ['content', 'messaging', 'concise', 'impact'],
          category: 'content',
          complexity: 'simple',
          estimatedTokens: 300,
        },
        validation: {
          requiredVariables: ['brandName'],
          outputFormat: 'JSON with one-liner and variations',
          safetyChecks: ['Brand-appropriate messaging'],
        },
      },
      {
        name: 'Social Media Ideas Generator',
        description: 'Creates creative social media content ideas',
        template: `You are a social media strategist creating content ideas for {{brandName}}.

BRAND CONTEXT:
- Industry: {{industry}}
- Target Audience: {{targetAudience}}
- Brand Personality: {{brandPersonality}}
- Content Themes: {{contentThemes}}

CAMPAIGN GOAL: {{campaignGoal}}
TIMEFRAME: {{timeframe}}

SOCIAL MEDIA IDEAS REQUIREMENTS:
Generate ideas that:
1. Leverage platform-specific features
2. Align with brand personality
3. Drive engagement and reach
4. Include visual and copy elements
5. Have clear calls-to-action
6. Are optimized for each platform

OUTPUT FORMAT (JSON):
{
  "campaignTheme": "Overall campaign theme",
  "ideas": [
    {
      "platform": "Platform name",
      "contentType": "Type of content",
      "idea": "Detailed content idea",
      "caption": "Sample caption text",
      "hashtags": ["relevant", "hashtags"],
      "engagement": "Expected engagement rating (1-10)",
      "timing": "Best time to post"
    }
  ],
  "contentCalendar": [
    {
      "date": "YYYY-MM-DD",
      "platform": "platform",
      "content": "Brief content description"
    }
  ]
}

Generate social media ideas now:`,
        version: '1.0.0',
        agentName: 'SocialMediaIdeas',
        variables: ['brandName', 'industry', 'targetAudience', 'brandPersonality', 'contentThemes', 'campaignGoal', 'timeframe'],
        metadata: {
          author: 'system',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          tags: ['social', 'content', 'marketing', 'engagement'],
          category: 'marketing',
          complexity: 'medium',
          estimatedTokens: 700,
        },
        validation: {
          requiredVariables: ['brandName'],
          outputFormat: 'JSON with campaign ideas and calendar',
          safetyChecks: ['Platform-appropriate content'],
        },
      },
      {
        name: 'Sales Email Writer',
        description: 'Creates persuasive sales emails',
        template: `You are a sales copywriter creating persuasive emails for {{brandName}}.

BRAND CONTEXT:
- Industry: {{industry}}
- Target Audience: {{targetAudience}}
- Brand Personality: {{brandPersonality}}
- Unique Value Proposition: {{uniqueValueProposition}}

EMAIL CONTEXT:
- Funnel Stage: {{funnelStage}}
- Product/Service: {{productService}}
- Pain Points: {{painPoints}}
- Desired Outcome: {{desiredOutcome}}

EMAIL REQUIREMENTS:
Create emails that:
1. Have compelling subject lines
2. Build immediate rapport
3. Address specific pain points
4. Present clear value propositions
5. Include social proof elements
6. End with strong calls-to-action

OUTPUT FORMAT (JSON):
{
  "subject": "Compelling subject line",
  "preheader": "Email preheader text",
  "greeting": "Personalized greeting",
  "body": "Full email body with proper formatting",
  "callToAction": "Clear CTA",
  "closing": "Professional sign-off",
  "funnelStage": "awareness|consideration|decision|retention",
  "personalization": ["Personalization elements used"],
  "keyBenefits": ["Key benefits highlighted"]
}

Additional Context: {{context}}

Write the sales email now:`,
        version: '1.0.0',
        agentName: 'SalesEmail',
        variables: ['brandName', 'industry', 'targetAudience', 'brandPersonality', 'uniqueValueProposition', 'funnelStage', 'productService', 'painPoints', 'desiredOutcome', 'context'],
        metadata: {
          author: 'system',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          tags: ['email', 'sales', 'marketing', 'conversion'],
          category: 'marketing',
          complexity: 'medium',
          estimatedTokens: 600,
        },
        validation: {
          requiredVariables: ['brandName', 'funnelStage'],
          outputFormat: 'JSON with complete email structure',
          safetyChecks: ['No spam-like language', 'CAN-SPAM compliance'],
        },
      },
      {
        name: 'Website Wireframe Designer',
        description: 'Creates website wireframes and layouts',
        template: `You are a UX designer creating website wireframes for {{brandName}}.

BRAND CONTEXT:
- Industry: {{industry}}
- Target Audience: {{targetAudience}}
- Brand Personality: {{brandPersonality}}
- Key Goals: {{keyGoals}}

WEBSITE CONTEXT:
- Page Type: {{pageType}}
- Primary Purpose: {{primaryPurpose}}
- Key Sections: {{keySections}}
- Target Devices: {{targetDevices}}

WIREFRAME REQUIREMENTS:
Design wireframes that:
1. Follow UX best practices
2. Prioritize content hierarchy
3. Optimize for user flow
4. Include clear calls-to-action
5. Consider mobile responsiveness
6. Support brand identity

OUTPUT FORMAT (JSON):
{
  "pageType": "Type of page (landing, product, about, etc.)",
  "overallLayout": "Layout description (single-column, grid, etc.)",
  "sections": [
    {
      "name": "Section name",
      "type": "hero|content|features|testimonials|cta|footer",
      "content": "Content description",
      "layout": "Layout instructions",
      "priority": "Priority level (1-5)"
    }
  ],
  "navigation": ["Navigation items"],
  "callToActions": ["CTAs on the page"],
  "responsiveNotes": "Mobile/tablet considerations",
  "userFlow": ["Key user journey steps"]
}

Additional Context: {{context}}

Design the wireframe now:`,
        version: '1.0.0',
        agentName: 'WebsiteWireframe',
        variables: ['brandName', 'industry', 'targetAudience', 'brandPersonality', 'keyGoals', 'pageType', 'primaryPurpose', 'keySections', 'targetDevices', 'context'],
        metadata: {
          author: 'system',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          tags: ['website', 'wireframe', 'ux', 'design'],
          category: 'technical',
          complexity: 'complex',
          estimatedTokens: 800,
        },
        validation: {
          requiredVariables: ['brandName', 'pageType'],
          outputFormat: 'JSON with complete wireframe structure',
          safetyChecks: ['Accessibility considerations', 'UX best practices'],
        },
      },
      // Image Generation Prompts
      {
        name: 'Social Media Image Generator',
        description: 'Creates eye-catching visuals optimized for social media platforms',
        template: `You are a professional graphic designer creating stunning social media images for {{brandName}}.

BRAND CONTEXT:
- Industry: {{industry}}
- Brand Colors: {{brandColors}}
- Target Audience: {{targetAudience}}
- Brand Personality: {{brandPersonality}}
- Platform: {{platform}}

IMAGE REQUIREMENTS:
Create a compelling visual that:
1. Captures attention within the first 3 seconds
2. Incorporates brand colors and identity
3. Is optimized for {{platform}} dimensions and format
4. Communicates {{message}} clearly
5. Has strong visual hierarchy and composition
6. Includes relevant imagery, icons, or graphics
7. Has readable text with proper contrast

VISUAL STYLE:
- {{style}} aesthetic (photorealistic, illustrative, minimalist, etc.)
- {{mood}} mood and atmosphere
- Professional quality suitable for brand representation
- High contrast and visual impact

OUTPUT FORMAT (JSON):
{
  "imagePrompt": "Detailed DALL-E prompt for image generation",
  "designElements": ["Key visual elements included"],
  "colorPalette": ["Primary colors used"],
  "textElements": ["Text content suggestions"],
  "optimizationNotes": "Platform-specific optimization notes",
  "brandAlignment": "How well it represents the brand (1-10)"
}

Additional Context: {{context}}

Generate the image prompt now:`,
        version: '1.0.0',
        agentName: 'ImageGenerator',
        variables: ['brandName', 'industry', 'brandColors', 'targetAudience', 'brandPersonality', 'platform', 'message', 'style', 'mood', 'context'],
        metadata: {
          author: 'system',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          tags: ['image', 'social', 'design', 'visual', 'marketing'],
          category: 'creative',
          complexity: 'medium',
          estimatedTokens: 400,
        },
        validation: {
          requiredVariables: ['brandName', 'platform', 'message'],
          outputFormat: 'JSON with detailed image generation prompt',
          safetyChecks: ['Brand color compliance', 'Professional quality'],
        },
      },
      {
        name: 'Hero Banner Generator',
        description: 'Creates impactful website hero banners and headers',
        template: `You are a web designer creating powerful hero banner images for {{brandName}}.

BRAND CONTEXT:
- Industry: {{industry}}
- Brand Colors: {{brandColors}}
- Target Audience: {{targetAudience}}
- Brand Personality: {{brandPersonality}}
- Website Section: {{section}}

BANNER REQUIREMENTS:
Create a hero banner that:
1. Makes a strong first impression
2. Incorporates brand identity and colors
3. Is optimized for web display (1536x512 pixels, 3:1 ratio)
4. Includes compelling headline and call-to-action
5. Has professional, high-quality composition
6. Conveys {{mood}} mood and {{message}}
7. Works across desktop and mobile devices

DESIGN ELEMENTS:
- {{style}} visual style
- Strong focal point and visual hierarchy
- Brand-consistent typography and imagery
- High contrast for readability
- Conversion-focused design

OUTPUT FORMAT (JSON):
{
  "imagePrompt": "Comprehensive DALL-E prompt for banner generation",
  "layoutElements": ["Key layout components"],
  "textSuggestions": {
    "headline": "Suggested headline text",
    "subheadline": "Suggested subheadline",
    "cta": "Call-to-action text"
  },
  "colorScheme": ["Primary and secondary colors"],
  "responsiveNotes": "How it adapts to different screen sizes",
  "brandAlignment": "Brand representation score (1-10)"
}

Additional Context: {{context}}

Generate the hero banner prompt now:`,
        version: '1.0.0',
        agentName: 'ImageGenerator',
        variables: ['brandName', 'industry', 'brandColors', 'targetAudience', 'brandPersonality', 'section', 'mood', 'message', 'style', 'context'],
        metadata: {
          author: 'system',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          tags: ['image', 'banner', 'hero', 'website', 'design'],
          category: 'creative',
          complexity: 'high',
          estimatedTokens: 500,
        },
        validation: {
          requiredVariables: ['brandName', 'section'],
          outputFormat: 'JSON with banner design specifications',
          safetyChecks: ['Web optimization', 'Brand compliance'],
        },
      },
      {
        name: 'Product Image Generator',
        description: 'Creates professional product photography and illustrations',
        template: `You are a professional product photographer creating stunning visuals for {{productName}}.

PRODUCT DETAILS:
- Product Name: {{productName}}
- Product Description: {{productDescription}}
- Product Category: {{category}}
- Key Features: {{features}}

BRAND CONTEXT:
- Brand Colors: {{brandColors}}
- Brand Personality: {{brandPersonality}}
- Target Audience: {{targetAudience}}

PHOTOGRAPHY REQUIREMENTS:
Create professional product imagery that:
1. Showcases the product beautifully and realistically
2. Uses {{lighting}} lighting setup for optimal presentation
3. Has {{background}} background that doesn't distract
4. Includes lifestyle context if relevant
5. Demonstrates product usage and benefits
6. Is suitable for e-commerce and marketing materials
7. Has commercial-grade quality and appeal

TECHNICAL SPECIFICATIONS:
- High-resolution suitable for print and digital
- Multiple angles if needed (front, side, detail shots)
- Clean, professional composition
- Brand color integration where appropriate

OUTPUT FORMAT (JSON):
{
  "imagePrompt": "Detailed product photography prompt",
  "compositionNotes": ["Key composition elements"],
  "lightingSetup": "Recommended lighting configuration",
  "backgroundStyle": "Background specifications",
  "additionalAngles": ["Other recommended shots"],
  "usageContexts": ["Where this image works best"],
  "commercialQuality": "Quality assessment (1-10)"
}

Additional Context: {{context}}

Generate the product image prompt now:`,
        version: '1.0.0',
        agentName: 'ImageGenerator',
        variables: ['productName', 'productDescription', 'category', 'features', 'brandColors', 'brandPersonality', 'targetAudience', 'lighting', 'background', 'context'],
        metadata: {
          author: 'system',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          tags: ['image', 'product', 'photography', 'ecommerce', 'marketing'],
          category: 'commercial',
          complexity: 'high',
          estimatedTokens: 600,
        },
        validation: {
          requiredVariables: ['productName', 'productDescription'],
          outputFormat: 'JSON with product photography specifications',
          safetyChecks: ['Commercial quality standards', 'Product accuracy'],
        },
      },
    ];

    for (const prompt of defaultPrompts) {
      await this.registerPrompt(prompt);
    }
  }

  private generatePromptId(agentName: string, version: string): string {
    return `${agentName.toLowerCase()}_v${version.replace(/\./g, '_')}`;
  }

  private compareVersions(version1: string, version2: string): number {
    const v1Parts = version1.split('.').map(Number);
    const v2Parts = version2.split('.').map(Number);

    for (let i = 0; i < Math.max(v1Parts.length, v2Parts.length); i++) {
      const v1 = v1Parts[i] || 0;
      const v2 = v2Parts[i] || 0;

      if (v1 > v2) return 1;
      if (v1 < v2) return -1;
    }

    return 0;
  }

  private extractVariablesFromTemplate(template: string): string[] {
    const matches = template.match(/\{\{(\w+)\}\}/g);
    return matches ? [...new Set(matches.map(match => match.slice(2, -2)))] : [];
  }

  private async invalidatePromptCache(promptId: string): Promise<void> {
    await redisMemory.delete(`${this.cachePrefix}:${promptId}`);
  }

  private async invalidateAgentCache(agentName: string): Promise<void> {
    const keys = [
      `${this.cachePrefix}:agent:${agentName}:latest`,
    ];

    // Get all versions for this agent and invalidate their caches
    for (const prompt of this.prompts.values()) {
      if (prompt.agentName === agentName) {
        keys.push(`${this.cachePrefix}:agent:${agentName}:v${prompt.version}`);
      }
    }

    await Promise.all(keys.map(key => redisMemory.delete(key)));
  }
}

// Export singleton instance
export const promptStore = new PromptStore();

// Export types
export type { PromptTemplate, PromptVariant, PromptContext };
