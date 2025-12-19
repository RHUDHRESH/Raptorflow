/**
 * Image Generator Agent
 *
 * Creates AI-generated images for various marketing and branding needs.
 */

import { z } from 'zod';
import { BaseOrchestratorAgent } from './base';

const ImageGeneratorInputSchema = z.object({
  prompt: z.string().min(10, "Prompt must be at least 10 characters"),
  style: z.enum(['realistic', 'illustrative', 'minimalist', 'bold', 'vibrant', 'monochrome']).optional(),
  dimensions: z.enum(['square', 'landscape', 'portrait', 'banner']).optional(),
  brandColors: z.array(z.string()).optional(),
  targetAudience: z.string().optional(),
  mood: z.string().optional(),
  additionalContext: z.record(z.unknown()).optional(),
});

const ImageGeneratorOutputSchema = z.object({
  imageUrl: z.string(),
  imageKey: z.string(),
  prompt: z.string(),
  style: z.string(),
  dimensions: z.object({
    width: z.number(),
    height: z.number(),
  }),
  metadata: z.object({
    generationTime: z.number(),
    model: z.string(),
    cost: z.number(),
  }),
  variations: z.array(z.object({
    url: z.string(),
    key: z.string(),
    style: z.string(),
  })).optional(),
});

export class ImageGeneratorAgent extends BaseOrchestratorAgent {
  constructor() {
    super({
      name: 'ImageGenerator',
      description: 'Creates AI-generated images for marketing and branding needs',
      category: 'creative',
      capabilities: [
        'AI image generation',
        'Brand-aligned visuals',
        'Multiple style options',
        'Responsive dimensions',
        'Image variations'
      ],
      inputSchema: ImageGeneratorInputSchema,
      outputSchema: ImageGeneratorOutputSchema,
      estimatedDuration: 45, // Image generation takes longer
      costEstimate: {
        minTokens: 100,
        maxTokens: 500,
        estimatedCost: 0.02,
      },
      metadata: {
        complexity: 'medium',
        platforms: ['marketing', 'social', 'web'],
        imageGeneration: true,
      }
    });
  }

  async generate(input: z.infer<typeof ImageGeneratorInputSchema>): Promise<z.infer<typeof ImageGeneratorOutputSchema>> {
    // Validate input
    const validatedInput = this.validateInput(input);
    if (!validatedInput.valid) {
      throw new Error(`Invalid input: ${validatedInput.errors.join(', ')}`);
    }

    // Get LLM to enhance the prompt for better image generation
    const enhancedPrompt = await this.enhancePrompt(input);

    // Generate image using image generation service
    const imageResult = await this.generateImage(enhancedPrompt, input);

    // Validate output
    const validatedOutput = this.validateOutput(imageResult);
    if (!validatedOutput.valid) {
      throw new Error(`Invalid output: ${validatedOutput.errors.join(', ')}`);
    }

    return validatedOutput.data;
  }

  private async enhancePrompt(input: z.infer<typeof ImageGeneratorInputSchema>): Promise<string> {
    // Get the appropriate prompt template based on the asset type
    let promptTemplate;
    switch (input.additionalContext?.assetType || 'social_media_image') {
      case 'social_media_image':
        promptTemplate = await this.getPromptTemplate('Social Media Image Generator');
        break;
      case 'hero_banner':
        promptTemplate = await this.getPromptTemplate('Hero Banner Generator');
        break;
      case 'product_image':
        promptTemplate = await this.getPromptTemplate('Product Image Generator');
        break;
      default:
        promptTemplate = await this.getPromptTemplate('Social Media Image Generator');
    }

    if (!promptTemplate) {
      // Fallback to basic prompt enhancement
      return this.createBasicPrompt(input);
    }

    // Fill in the template with input data
    let filledPrompt = promptTemplate.template;
    const variables = {
      brandName: 'RaptorFlow', // TODO: Get from brand profile
      industry: 'Marketing Technology', // TODO: Get from brand profile
      brandColors: input.brandColors?.join(', ') || '#6366f1, #8b5cf6',
      targetAudience: input.targetAudience || 'marketers and business owners',
      brandPersonality: 'innovative, professional, growth-focused', // TODO: Get from brand profile
      platform: this.getPlatformFromAssetType(input.additionalContext?.assetType),
      message: input.prompt,
      style: input.style || 'realistic',
      mood: input.mood || 'professional',
      context: input.additionalContext?.context || '',
      productName: input.additionalContext?.productName || '',
      productDescription: input.additionalContext?.productDescription || '',
      category: input.additionalContext?.category || '',
      features: input.additionalContext?.features || '',
      section: input.additionalContext?.section || 'hero',
      lighting: 'professional studio',
      background: 'clean white'
    };

    // Replace variables in template
    for (const [key, value] of Object.entries(variables)) {
      filledPrompt = filledPrompt.replace(new RegExp(`{{${key}}}`, 'g'), value);
    }

    return filledPrompt;
  }

  private async getPromptTemplate(templateName: string) {
    const { promptStore } = await import('../prompts');
    return await promptStore.getPrompt(templateName);
  }

  private getPlatformFromAssetType(assetType?: string): string {
    const platformMap: Record<string, string> = {
      'social_media_image': 'Instagram/LinkedIn',
      'hero_banner': 'Website',
      'product_image': 'E-commerce',
      'brand_logo_concept': 'Brand Identity',
      'infographic': 'Content Marketing',
      'website_hero': 'Website'
    };
    return platformMap[assetType || 'social_media_image'] || 'Social Media';
  }

  private createBasicPrompt(input: z.infer<typeof ImageGeneratorInputSchema>): string {
    const styleDescriptions = {
      realistic: 'photorealistic, highly detailed, professional photography style',
      illustrative: 'clean illustration, vector art style, modern and minimal',
      minimalist: 'extremely simple, clean lines, negative space, monochromatic',
      bold: 'vibrant colors, strong contrasts, eye-catching, dynamic composition',
      vibrant: 'colorful, energetic, bright and cheerful, playful design',
      monochrome: 'black and white, grayscale, sophisticated, timeless'
    };

    const dimensionSpecs = {
      square: '1:1 aspect ratio, 1024x1024 pixels',
      landscape: '16:9 aspect ratio, 1792x1024 pixels',
      portrait: '9:16 aspect ratio, 1024x1792 pixels',
      banner: '3:1 aspect ratio, 1536x512 pixels'
    };

    let enhancedPrompt = input.prompt;

    // Add style description
    if (input.style && styleDescriptions[input.style]) {
      enhancedPrompt += `, ${styleDescriptions[input.style]}`;
    }

    // Add brand colors if provided
    if (input.brandColors && input.brandColors.length > 0) {
      enhancedPrompt += `, incorporating brand colors: ${input.brandColors.join(', ')}`;
    }

    // Add target audience context
    if (input.targetAudience) {
      enhancedPrompt += `, designed for ${input.targetAudience} audience`;
    }

    // Add mood/tone
    if (input.mood) {
      enhancedPrompt += `, ${input.mood} mood and atmosphere`;
    }

    // Add technical specifications
    const dimensions = input.dimensions || 'square';
    enhancedPrompt += `, ${dimensionSpecs[dimensions]}, high quality, professional, marketing material`;

    return enhancedPrompt;
  }

  private async generateImage(prompt: string, input: z.infer<typeof ImageGeneratorInputSchema>) {
    // Use OpenAI DALL-E for image generation (fallback to other services if needed)
    const { llmAdapter } = await import('../llm/adapter');

    try {
      // Generate image using DALL-E
      const imageResponse = await llmAdapter.generateImage({
        prompt,
        size: this.getImageSize(input.dimensions || 'square'),
        quality: 'standard',
        n: 1,
      });

      // Upload to GCS (Google Cloud Storage)
      const { gcsConnector } = await import('../../services/gcsConnector');
      const timestamp = Date.now();
      const filename = `generated-image-${timestamp}.png`;
      const gcsKey = `images/generated/${filename}`;

      const uploadResult = await gcsConnector.uploadFile(gcsKey, imageResponse.imageBuffer, {
        contentType: 'image/png',
        metadata: {
          prompt,
          style: input.style || 'realistic',
          dimensions: input.dimensions || 'square',
          generatedAt: new Date().toISOString(),
          source: 'muse_image_generator',
        },
      });

      // Generate variations if requested
      const variations = [];
      if (input.additionalContext?.generateVariations) {
        // Generate 2-3 variations with slight prompt modifications
        for (let i = 1; i <= 3; i++) {
          const variationPrompt = `${prompt}, variation ${i}, different composition`;
          try {
            const variationResponse = await llmAdapter.generateImage({
              prompt: variationPrompt,
              size: this.getImageSize(input.dimensions || 'square'),
              quality: 'standard',
              n: 1,
            });

            const variationFilename = `generated-image-${timestamp}-var${i}.png`;
            const variationKey = `images/generated/${variationFilename}`;

            await gcsConnector.uploadFile(variationKey, variationResponse.imageBuffer, {
              contentType: 'image/png',
              metadata: {
                prompt: variationPrompt,
                style: input.style || 'realistic',
                dimensions: input.dimensions || 'square',
                generatedAt: new Date().toISOString(),
                source: 'muse_image_generator',
                variation: i.toString(),
              },
            });

            const signedUrl = await gcsConnector.getSignedUrl(variationKey, 3600); // 1 hour expiry
            variations.push({
              url: signedUrl,
              key: variationKey,
              style: `variation-${i}`,
            });
          } catch (error) {
            console.warn(`Failed to generate variation ${i}:`, error);
          }
        }
      }

      const dimensions = this.getDimensions(input.dimensions || 'square');

      return {
        imageUrl: uploadResult.location,
        imageKey: gcsKey,
        prompt: input.prompt,
        style: input.style || 'realistic',
        dimensions,
        metadata: {
          generationTime: Date.now(),
          model: 'dall-e-3',
          cost: 0.04, // DALL-E 3 cost
        },
        variations: variations.length > 0 ? variations : undefined,
      };

    } catch (error) {
      console.error('Image generation failed:', error);
      throw new Error(`Failed to generate image: ${error.message}`);
    }
  }

  private getImageSize(dimension: string): string {
    const sizes = {
      square: '1024x1024',
      landscape: '1792x1024',
      portrait: '1024x1792',
      banner: '1536x512',
    };
    return sizes[dimension] || '1024x1024';
  }

  private getDimensions(dimension: string): { width: number; height: number } {
    const dimensions = {
      square: { width: 1024, height: 1024 },
      landscape: { width: 1792, height: 1024 },
      portrait: { width: 1024, height: 1792 },
      banner: { width: 1536, height: 512 },
    };
    return dimensions[dimension] || dimensions.square;
  }
}

// Export singleton instance
export const imageGeneratorAgent = new ImageGeneratorAgent();

// Export types
export type ImageGeneratorInput = z.infer<typeof ImageGeneratorInputSchema>;
export type ImageGeneratorOutput = z.infer<typeof ImageGeneratorOutputSchema>;
