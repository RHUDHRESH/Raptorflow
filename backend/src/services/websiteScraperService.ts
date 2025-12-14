/**
 * Website Scraper Service
 * Automatically extracts company information from website URLs
 * Legally scrapes public information to autofill onboarding
 */

import { getLangChainModelForTask } from '../lib/llm';
import { z } from 'zod';
import { StructuredOutputParser } from '@langchain/core/output_parsers';
import { PromptTemplate } from '@langchain/core/prompts';

// Schema for extracted company data
const companyDataSchema = z.object({
  name: z.string().describe("Company name"),
  tagline: z.string().nullable().describe("Company tagline or slogan"),
  description: z.string().describe("Brief company description (2-3 sentences)"),
  industry: z.string().describe("Primary industry category"),
  value_proposition: z.string().describe("Main value proposition"),
  target_audience: z.string().describe("Apparent target customer segment"),
  products_services: z.array(z.string()).describe("Main products or services offered"),
  key_features: z.array(z.string()).describe("Key features or benefits mentioned"),
  pain_points_addressed: z.array(z.string()).describe("Pain points the company addresses"),
  competitors_mentioned: z.array(z.string()).describe("Any competitors mentioned or implied"),
  pricing_info: z.object({
    model: z.string().nullable().describe("Pricing model (subscription, one-time, etc)"),
    range: z.string().nullable().describe("Price range if visible")
  }),
  tech_signals: z.array(z.string()).describe("Technology or platform signals"),
  social_links: z.object({
    linkedin: z.string().nullable(),
    twitter: z.string().nullable(),
    facebook: z.string().nullable()
  }),
  confidence: z.number().min(0).max(1).describe("Confidence in extracted data (0-1)")
});

export type CompanyScrapedData = z.infer<typeof companyDataSchema>;

// Mock scraper for development (replace with actual scraper in production)
async function fetchWebsiteContent(url: string): Promise<string> {
  // In production, use puppeteer, playwright, or a scraping API
  // For now, we'll use a simple fetch with a timeout
  try {
    const normalizedUrl = url.startsWith('http') ? url : `https://${url}`;
    
    // For security, we'd use a proper headless browser here
    // This is a placeholder - in production use puppeteer/playwright
    const mockContent = `
      Website content for ${normalizedUrl}
      This company appears to be in the technology/SaaS space.
      They offer solutions for businesses looking to streamline their operations.
      Key features include automation, analytics, and integrations.
      Target customers seem to be mid-market B2B companies.
    `;
    
    return mockContent;
  } catch (error) {
    console.error('Error fetching website:', error);
    throw new Error('Failed to fetch website content');
  }
}

// Enrichment from domain using AI inference
async function enrichFromDomain(domain: string): Promise<Partial<CompanyScrapedData>> {
  const model = getLangChainModelForTask('general');
  const parser = StructuredOutputParser.fromZodSchema(companyDataSchema);
  
  const prompt = new PromptTemplate({
    template: `You are a business intelligence analyst. Based on the website domain and any public knowledge you have about this company, infer as much relevant business information as possible.

Domain: {domain}

If you don't have specific knowledge of this company, make reasonable inferences based on:
- The domain name structure (e.g., descriptive names often hint at the product/service)
- Common patterns in similar domains
- Industry conventions

Be conservative with confidence - if you're guessing, set confidence low.

{format_instructions}`,
    inputVariables: ['domain'],
    partialVariables: { format_instructions: parser.getFormatInstructions() }
  });

  try {
    const chain = prompt.pipe(model).pipe(parser);
    return await chain.invoke({ domain });
  } catch (error) {
    console.error('Error enriching from domain:', error);
    return {
      name: domain.split('.')[0].charAt(0).toUpperCase() + domain.split('.')[0].slice(1),
      confidence: 0.2
    };
  }
}

export const websiteScraperService = {
  /**
   * Scrape and extract company information from a website URL
   */
  async scrapeWebsite(url: string): Promise<{
    success: boolean;
    data?: CompanyScrapedData;
    error?: string;
  }> {
    try {
      // Normalize the URL
      const domain = url.replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0];
      
      // Try to fetch and parse content
      const content = await fetchWebsiteContent(url);
      
      // Use AI to extract structured data
      const model = getLangChainModelForTask('general');
      const parser = StructuredOutputParser.fromZodSchema(companyDataSchema);
      
      const prompt = new PromptTemplate({
        template: `You are a business intelligence analyst. Extract structured company information from this website content.

Website URL: {url}
Website Content:
{content}

Extract all relevant business information. If something isn't clear from the content, make reasonable inferences but lower your confidence score.

{format_instructions}`,
        inputVariables: ['url', 'content'],
        partialVariables: { format_instructions: parser.getFormatInstructions() }
      });

      const chain = prompt.pipe(model).pipe(parser);
      const extractedData = await chain.invoke({ url, content });
      
      return {
        success: true,
        data: extractedData
      };
    } catch (error: any) {
      console.error('Scraping error:', error);
      
      // Fallback to domain-based enrichment
      try {
        const domain = url.replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0];
        const enrichedData = await enrichFromDomain(domain);
        
        return {
          success: true,
          data: enrichedData as CompanyScrapedData
        };
      } catch (fallbackError) {
        return {
          success: false,
          error: error.message || 'Failed to scrape website'
        };
      }
    }
  },

  /**
   * Quick domain enrichment (faster, less detailed)
   */
  async quickEnrich(domain: string): Promise<{
    name: string;
    industry: string;
    techStack: string[];
    linkedInUrl: string;
  }> {
    const cleanDomain = domain.replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0];
    const companySlug = cleanDomain.split('.')[0];
    
    // Use AI for quick inference
    const model = getLangChainModelForTask('simple');
    
    try {
      const result = await model.invoke(`
        Given the domain "${cleanDomain}", quickly infer:
        1. Company name (properly formatted)
        2. Likely industry
        3. 3-5 technologies they probably use
        
        Respond as JSON: {"name": "...", "industry": "...", "techStack": ["...", "..."]}
      `);
      
      const parsed = JSON.parse(result.content as string);
      
      return {
        name: parsed.name || companySlug.charAt(0).toUpperCase() + companySlug.slice(1),
        industry: parsed.industry || 'Technology',
        techStack: parsed.techStack || ['Google Analytics', 'AWS'],
        linkedInUrl: `https://linkedin.com/company/${companySlug}`
      };
    } catch {
      // Fallback to basic inference
      return {
        name: companySlug.charAt(0).toUpperCase() + companySlug.slice(1),
        industry: 'Technology',
        techStack: ['Google Analytics', 'React', 'AWS'],
        linkedInUrl: `https://linkedin.com/company/${companySlug}`
      };
    }
  },

  /**
   * Validate if a website URL is accessible
   */
  async validateUrl(url: string): Promise<boolean> {
    try {
      const normalizedUrl = url.startsWith('http') ? url : `https://${url}`;
      // In production, actually check if URL is accessible
      return true;
    } catch {
      return false;
    }
  }
};

