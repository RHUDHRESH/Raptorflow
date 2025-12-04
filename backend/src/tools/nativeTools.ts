/**
 * Native Tools - No external API keys required
 * Uses web scraping + LLM analysis instead of paid APIs
 */

import { tool } from "@langchain/core/tools";
import { z } from "zod";
import { getLangChainModel } from "../lib/llm";

// Simple fetch wrapper with timeout
async function fetchWithTimeout(url: string, timeout = 10000): Promise<string> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      }
    });
    clearTimeout(timeoutId);
    return await response.text();
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}

// Parse HTML to extract text content
function extractTextFromHTML(html: string): { title: string; meta: string; headings: string[]; text: string } {
  // Basic HTML parsing without external libraries
  const titleMatch = html.match(/<title[^>]*>([^<]*)<\/title>/i);
  const title = titleMatch ? titleMatch[1].trim() : '';
  
  const metaMatch = html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']*)["']/i) ||
                    html.match(/<meta[^>]*content=["']([^"']*)["'][^>]*name=["']description["']/i);
  const meta = metaMatch ? metaMatch[1].trim() : '';
  
  // Extract headings
  const h1Matches = html.match(/<h1[^>]*>([^<]*)<\/h1>/gi) || [];
  const h2Matches = html.match(/<h2[^>]*>([^<]*)<\/h2>/gi) || [];
  const headings = [...h1Matches, ...h2Matches].map(h => 
    h.replace(/<[^>]*>/g, '').trim()
  ).filter(h => h.length > 0);
  
  // Extract body text (strip HTML tags)
  let bodyText = html
    .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
    .replace(/<nav[^>]*>[\s\S]*?<\/nav>/gi, '')
    .replace(/<footer[^>]*>[\s\S]*?<\/footer>/gi, '')
    .replace(/<header[^>]*>[\s\S]*?<\/header>/gi, '')
    .replace(/<[^>]*>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .substring(0, 5000);
  
  return { title, meta, headings, text: bodyText };
}

/**
 * Website Scraper Tool - Fetches and extracts info from a website
 */
export const websiteScraperTool = tool(
  async ({ url }): Promise<string> => {
    try {
      // Ensure URL has protocol
      const fullUrl = url.startsWith('http') ? url : `https://${url}`;
      const html = await fetchWithTimeout(fullUrl);
      const extracted = extractTextFromHTML(html);
      
      return JSON.stringify({
        success: true,
        url: fullUrl,
        title: extracted.title,
        metaDescription: extracted.meta,
        headings: extracted.headings.slice(0, 10),
        contentPreview: extracted.text.substring(0, 2000)
      });
    } catch (error: any) {
      return JSON.stringify({
        success: false,
        error: error.message,
        url
      });
    }
  },
  {
    name: "website_scraper",
    description: "Scrape a website to extract title, meta description, headings, and content. Use this to understand what a company does.",
    schema: z.object({
      url: z.string().describe("The website URL or domain to scrape (e.g., 'example.com' or 'https://example.com')")
    })
  }
);

/**
 * Company Analyzer Tool - Uses LLM to analyze scraped website content
 */
export const companyAnalyzerTool = tool(
  async ({ websiteContent, companyName }): Promise<string> => {
    try {
      const model = getLangChainModel("gemini-pro");
      
      const prompt = `Analyze this website content and extract company information.

Website Content:
${websiteContent}

Company Name (if known): ${companyName || 'Unknown'}

Extract and return a JSON object with:
{
  "companyName": "official company name",
  "tagline": "their main tagline or value proposition",
  "industry": "primary industry (SaaS, Fintech, E-commerce, etc.)",
  "productType": "what they sell (software, service, marketplace, etc.)",
  "targetAudience": "who they serve",
  "keyFeatures": ["feature 1", "feature 2", "feature 3"],
  "pricing_hints": "any pricing info found",
  "technology_hints": ["tech stack hints from content"],
  "competitors_mentioned": ["any competitors mentioned"],
  "company_size_hints": "any hints about company size"
}

Return ONLY valid JSON, no markdown or explanation.`;

      const response = await model.invoke(prompt);
      const content = typeof response.content === 'string' ? response.content : JSON.stringify(response.content);
      
      // Try to parse as JSON
      try {
        const parsed = JSON.parse(content.replace(/```json\n?|\n?```/g, '').trim());
        return JSON.stringify({ success: true, analysis: parsed });
      } catch {
        return JSON.stringify({ success: true, analysis: { raw: content } });
      }
    } catch (error: any) {
      return JSON.stringify({ success: false, error: error.message });
    }
  },
  {
    name: "company_analyzer",
    description: "Analyze website content using AI to extract company information like industry, product type, target audience, and features.",
    schema: z.object({
      websiteContent: z.string().describe("The scraped website content to analyze"),
      companyName: z.string().optional().describe("The company name if already known")
    })
  }
);

/**
 * Competitor Research Tool - Find and analyze competitors using web search simulation
 */
export const competitorResearchTool = tool(
  async ({ companyDescription, industry, knownCompetitors }): Promise<string> => {
    try {
      const model = getLangChainModel("gemini-pro");
      
      const prompt = `You are a market research expert. Based on the company description and industry, identify likely competitors.

Company Description: ${companyDescription}
Industry: ${industry}
Known Competitors: ${knownCompetitors?.join(', ') || 'None specified'}

Identify 3-5 likely competitors for this company. For each competitor, provide:
{
  "competitors": [
    {
      "name": "Competitor Name",
      "website": "likely website URL",
      "description": "what they do",
      "positioning": "how they position themselves",
      "strengths": ["strength 1", "strength 2"],
      "weaknesses": ["weakness 1", "weakness 2"],
      "price_position": "budget/mid-market/premium",
      "target_overlap": "high/medium/low - how much they target same audience"
    }
  ],
  "market_landscape": {
    "total_competitors": "estimated number in market",
    "market_maturity": "emerging/growing/mature/declining",
    "key_differentiators": ["what matters most in this market"]
  }
}

Return ONLY valid JSON.`;

      const response = await model.invoke(prompt);
      const content = typeof response.content === 'string' ? response.content : JSON.stringify(response.content);
      
      try {
        const parsed = JSON.parse(content.replace(/```json\n?|\n?```/g, '').trim());
        return JSON.stringify({ success: true, research: parsed });
      } catch {
        return JSON.stringify({ success: true, research: { raw: content } });
      }
    } catch (error: any) {
      return JSON.stringify({ success: false, error: error.message });
    }
  },
  {
    name: "competitor_research",
    description: "Research and identify competitors based on company description and industry.",
    schema: z.object({
      companyDescription: z.string().describe("Description of what the company does"),
      industry: z.string().describe("The industry or market"),
      knownCompetitors: z.array(z.string()).optional().describe("Already known competitor names")
    })
  }
);

/**
 * Tech Stack Detector Tool - Analyzes website HTML for technology hints
 */
export const techStackDetectorTool = tool(
  async ({ url }): Promise<string> => {
    try {
      const fullUrl = url.startsWith('http') ? url : `https://${url}`;
      const html = await fetchWithTimeout(fullUrl);
      
      const techSignatures: Record<string, string[]> = {
        'React': ['react', '_next', '__NEXT_DATA__', 'reactroot'],
        'Vue.js': ['vue', '__vue__', 'v-'],
        'Angular': ['ng-', 'angular'],
        'Next.js': ['_next', '__NEXT_DATA__'],
        'WordPress': ['wp-content', 'wp-includes', 'wordpress'],
        'Shopify': ['cdn.shopify', 'shopify'],
        'HubSpot': ['hubspot', 'hs-scripts', 'hbspt'],
        'Salesforce': ['salesforce', 'sfdc'],
        'Google Analytics': ['google-analytics', 'gtag', 'ga.js', 'analytics.js'],
        'Google Tag Manager': ['googletagmanager', 'gtm.js'],
        'Segment': ['segment', 'analytics.min.js'],
        'Intercom': ['intercom', 'intercomSettings'],
        'Drift': ['drift', 'driftt'],
        'Zendesk': ['zendesk', 'zdassets'],
        'Stripe': ['stripe', 'js.stripe.com'],
        'AWS': ['amazonaws', 'aws'],
        'Cloudflare': ['cloudflare', 'cf-'],
        'Vercel': ['vercel'],
        'Netlify': ['netlify'],
        'Mixpanel': ['mixpanel'],
        'Amplitude': ['amplitude'],
        'Hotjar': ['hotjar'],
        'FullStory': ['fullstory'],
        'Mailchimp': ['mailchimp'],
        'SendGrid': ['sendgrid'],
        'Twilio': ['twilio'],
        'Slack': ['slack'],
        'Zoom': ['zoom'],
      };
      
      const detectedTech: string[] = [];
      const htmlLower = html.toLowerCase();
      
      for (const [tech, signatures] of Object.entries(techSignatures)) {
        if (signatures.some(sig => htmlLower.includes(sig.toLowerCase()))) {
          detectedTech.push(tech);
        }
      }
      
      // Categorize technologies
      const categories: Record<string, string[]> = {
        'Frontend Framework': ['React', 'Vue.js', 'Angular', 'Next.js'],
        'CMS/Platform': ['WordPress', 'Shopify'],
        'CRM/Marketing': ['HubSpot', 'Salesforce', 'Mailchimp'],
        'Analytics': ['Google Analytics', 'Mixpanel', 'Amplitude', 'Segment'],
        'Support/Chat': ['Intercom', 'Drift', 'Zendesk'],
        'Infrastructure': ['AWS', 'Cloudflare', 'Vercel', 'Netlify'],
        'Payments': ['Stripe'],
        'Session Recording': ['Hotjar', 'FullStory'],
        'Communication': ['Twilio', 'SendGrid', 'Slack', 'Zoom'],
      };
      
      const categorizedTech: Record<string, string[]> = {};
      for (const [category, techs] of Object.entries(categories)) {
        const found = techs.filter(t => detectedTech.includes(t));
        if (found.length > 0) {
          categorizedTech[category] = found;
        }
      }
      
      return JSON.stringify({
        success: true,
        url: fullUrl,
        detectedTechnologies: detectedTech,
        categorized: categorizedTech,
        total: detectedTech.length
      });
    } catch (error: any) {
      return JSON.stringify({ success: false, error: error.message, url });
    }
  },
  {
    name: "tech_stack_detector",
    description: "Detect technologies used by a website by analyzing its HTML for known technology signatures.",
    schema: z.object({
      url: z.string().describe("The website URL or domain to analyze")
    })
  }
);

/**
 * ICP Generator Tool - Uses LLM to generate ICPs from company data
 */
export const icpGeneratorTool = tool(
  async ({ companyData, positioningData, productData, strategyData }): Promise<string> => {
    try {
      const model = getLangChainModel("gemini-pro");
      
      const prompt = `You are an expert B2B marketing strategist. Generate 3 Ideal Customer Profiles (ICPs) based on this data.

COMPANY DATA:
${JSON.stringify(companyData, null, 2)}

POSITIONING DATA:
${JSON.stringify(positioningData, null, 2)}

PRODUCT DATA:
${JSON.stringify(productData, null, 2)}

STRATEGY DATA:
${JSON.stringify(strategyData, null, 2)}

Generate 3 distinct ICPs following this framework:

1. **Desperate Scaler** - High urgency, immediate need, fast-growing
2. **Frustrated Optimizer** - Tried alternatives, ready to switch, seeking better solution
3. **Risk Mitigator** - Conservative, needs proof, values security/compliance

For each ICP, provide:
{
  "icps": [
    {
      "id": "desperate-scaler",
      "label": "Desperate Scaler",
      "summary": "2-sentence description",
      "firmographics": {
        "employee_range": "50-200",
        "revenue_range": "$5M-$50M",
        "industries": ["SaaS", "Tech"],
        "stages": ["series-a", "series-b"],
        "regions": ["North America"],
        "exclude": ["Enterprise", "Government"]
      },
      "technographics": {
        "must_have": ["CRM like Salesforce or HubSpot"],
        "nice_to_have": ["Marketing automation"],
        "red_flags": ["Legacy on-premise systems"]
      },
      "psychographics": {
        "pain_points": ["Growing too fast", "No clear process"],
        "motivations": ["Scale revenue", "Impress investors"],
        "internal_triggers": ["New funding round", "Hiring spree"],
        "buying_constraints": ["Speed matters more than price"]
      },
      "behavioral_triggers": [
        {"signal": "Just raised funding", "source": "News/LinkedIn", "urgency_boost": 90},
        {"signal": "Hiring SDRs/marketers", "source": "Job boards", "urgency_boost": 80}
      ],
      "buying_committee": [
        {"role": "Decision Maker", "typical_title": "VP Growth/CMO", "concerns": ["ROI", "Speed"], "success_criteria": ["Pipeline growth"]}
      ],
      "category_context": {
        "market_position": "challenger",
        "current_solution": "Manual/spreadsheets",
        "switching_triggers": ["Hit growth wall", "Competitor pressure"]
      },
      "fit_score": 92,
      "fit_reasoning": "Why this ICP is a good fit",
      "messaging_angle": "Core message for this ICP",
      "qualification_questions": ["Question to ask in discovery"]
    }
  ]
}

Return ONLY valid JSON with all 3 ICPs.`;

      const response = await model.invoke(prompt);
      const content = typeof response.content === 'string' ? response.content : JSON.stringify(response.content);
      
      try {
        const parsed = JSON.parse(content.replace(/```json\n?|\n?```/g, '').trim());
        return JSON.stringify({ success: true, ...parsed });
      } catch {
        return JSON.stringify({ success: false, error: 'Failed to parse ICP response', raw: content });
      }
    } catch (error: any) {
      return JSON.stringify({ success: false, error: error.message });
    }
  },
  {
    name: "icp_generator",
    description: "Generate Ideal Customer Profiles using AI based on company, positioning, product, and strategy data.",
    schema: z.object({
      companyData: z.any().describe("Company information"),
      positioningData: z.any().describe("Positioning information"),
      productData: z.any().describe("Product information"),
      strategyData: z.any().describe("Strategy choices")
    })
  }
);

/**
 * War Plan Generator Tool - Creates 90-day marketing war plan
 */
export const warPlanGeneratorTool = tool(
  async ({ icps, strategyData, companyData }): Promise<string> => {
    try {
      const model = getLangChainModel("gemini-pro");
      
      const prompt = `You are a B2B marketing strategist. Create a 90-day marketing war plan.

ICPs:
${JSON.stringify(icps, null, 2)}

STRATEGY:
${JSON.stringify(strategyData, null, 2)}

COMPANY:
${JSON.stringify(companyData, null, 2)}

Generate a war plan with:
{
  "generated": true,
  "summary": "One paragraph overview",
  "phases": [
    {
      "id": 1,
      "name": "Discovery & Authority",
      "days": "1-30",
      "objectives": ["Build thought leadership", "Establish content foundation"],
      "campaigns": ["Authority Blitz", "Content Waterfall"],
      "kpis": [
        {"name": "Content published", "target": "8-12 pieces"},
        {"name": "Website traffic", "target": "+30%"}
      ],
      "key_tasks": ["Create pillar content", "Set up tracking"]
    },
    {
      "id": 2,
      "name": "Launch & Validation",
      "days": "31-60",
      "objectives": ["Launch demand gen", "Build social proof"],
      "campaigns": ["Trust Anchor", "Spear Attack"],
      "kpis": [
        {"name": "Demo conversion", "target": "15%+"},
        {"name": "Pipeline", "target": "$100k+"}
      ],
      "key_tasks": ["Launch paid campaigns", "Start outbound"]
    },
    {
      "id": 3,
      "name": "Optimization & Scale",
      "days": "61-90",
      "objectives": ["Double down on winners", "Kill underperformers"],
      "campaigns": ["Expansion Plays", "Optimization"],
      "kpis": [
        {"name": "CAC payback", "target": "<12 months"},
        {"name": "Win rate", "target": "25%+"}
      ],
      "key_tasks": ["Analyze and optimize", "Plan Q2"]
    }
  ],
  "protocols": {
    "A": {"name": "Authority Blitz", "active": true, "description": "Build thought leadership"},
    "B": {"name": "Trust Anchor", "active": true, "description": "Social proof and validation"},
    "C": {"name": "Cost of Inaction", "active": false, "description": "Fear-based messaging"},
    "D": {"name": "Facilitator Nudge", "active": true, "description": "Help buyers buy"},
    "E": {"name": "Champions Armory", "active": false, "description": "Enable internal champions"},
    "F": {"name": "Churn Intercept", "active": false, "description": "Retention plays"}
  },
  "recommended_budget_split": {
    "content": "30%",
    "paid_media": "40%",
    "tools": "15%",
    "events": "15%"
  }
}

Return ONLY valid JSON.`;

      const response = await model.invoke(prompt);
      const content = typeof response.content === 'string' ? response.content : JSON.stringify(response.content);
      
      try {
        const parsed = JSON.parse(content.replace(/```json\n?|\n?```/g, '').trim());
        return JSON.stringify({ success: true, warPlan: parsed });
      } catch {
        return JSON.stringify({ success: false, error: 'Failed to parse war plan', raw: content });
      }
    } catch (error: any) {
      return JSON.stringify({ success: false, error: error.message });
    }
  },
  {
    name: "war_plan_generator",
    description: "Generate a 90-day marketing war plan based on ICPs and strategy.",
    schema: z.object({
      icps: z.array(z.any()).describe("The generated ICPs"),
      strategyData: z.any().describe("Strategy choices"),
      companyData: z.any().describe("Company information")
    })
  }
);

// Export all tools
export const nativeTools = [
  websiteScraperTool,
  companyAnalyzerTool,
  competitorResearchTool,
  techStackDetectorTool,
  icpGeneratorTool,
  warPlanGeneratorTool
];

export default nativeTools;

