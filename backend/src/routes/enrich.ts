import { Router, Request, Response } from 'express';
import { supabase } from '../lib/supabase';
import { websiteScraperService } from '../services/websiteScraperService';
import { inputValidationService } from '../services/inputValidationService';

const router = Router();

// Middleware to verify JWT token
const verifyToken = async (req: Request, res: Response, next: Function) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or invalid authorization header' });
  }

  const token = authHeader.split(' ')[1];
  
  try {
    const { data: { user }, error } = await supabase.auth.getUser(token);
    
    if (error || !user) {
      return res.status(401).json({ error: 'Invalid token' });
    }

    (req as any).user = user;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Token verification failed' });
  }
};

/**
 * POST /api/enrich/website
 * Scrape website and extract company information
 */
router.post('/website', verifyToken, async (req: Request, res: Response) => {
  try {
    const { url } = req.body;

    if (!url) {
      return res.status(400).json({ error: 'URL is required' });
    }

    // Validate URL format
    const isValid = await websiteScraperService.validateUrl(url);
    if (!isValid) {
      return res.status(400).json({ error: 'Invalid or inaccessible URL' });
    }

    // Scrape website
    const result = await websiteScraperService.scrapeWebsite(url);

    if (result.success && result.data) {
      res.json({
        success: true,
        data: result.data,
        autofill: {
          // Map to onboarding fields
          name: result.data.name,
          industry: mapToIndustry(result.data.industry),
          description: result.data.description,
          valueProposition: result.data.value_proposition,
          targetAudience: result.data.target_audience,
          painPoints: result.data.pain_points_addressed,
          products: result.data.products_services,
          techStack: result.data.tech_signals,
          socialLinks: result.data.social_links
        }
      });
    } else {
      res.status(500).json({ 
        success: false, 
        error: result.error || 'Failed to scrape website' 
      });
    }
  } catch (err: any) {
    console.error('Website enrichment error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/enrich/quick
 * Quick domain enrichment (faster, less detailed)
 */
router.post('/quick', verifyToken, async (req: Request, res: Response) => {
  try {
    const { domain } = req.body;

    if (!domain) {
      return res.status(400).json({ error: 'Domain is required' });
    }

    const result = await websiteScraperService.quickEnrich(domain);
    res.json({ success: true, data: result });
  } catch (err: any) {
    console.error('Quick enrichment error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/enrich/validate
 * Validate user input and provide feedback
 */
router.post('/validate', verifyToken, async (req: Request, res: Response) => {
  try {
    const { input, fieldType, context } = req.body;

    if (!input || !fieldType) {
      return res.status(400).json({ error: 'Input and fieldType are required' });
    }

    const result = await inputValidationService.validateInput(input, fieldType, context);
    res.json(result);
  } catch (err: any) {
    console.error('Validation error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/enrich/validate-positioning
 * Validate entire positioning step
 */
router.post('/validate-positioning', verifyToken, async (req: Request, res: Response) => {
  try {
    const { danKennedy, dunford } = req.body;

    if (!danKennedy || !dunford) {
      return res.status(400).json({ error: 'Both danKennedy and dunford are required' });
    }

    const result = await inputValidationService.validatePositioning(danKennedy, dunford);
    res.json(result);
  } catch (err: any) {
    console.error('Positioning validation error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/enrich/check-bullshit
 * Quick check for generic/vague inputs
 */
router.post('/check-bullshit', verifyToken, async (req: Request, res: Response) => {
  try {
    const { input } = req.body;

    if (!input) {
      return res.status(400).json({ error: 'Input is required' });
    }

    const result = await inputValidationService.detectBullshit(input);
    res.json(result);
  } catch (err: any) {
    console.error('Bullshit detection error:', err);
    res.status(500).json({ error: err.message });
  }
});

// Helper function to map free-form industry to our categories
function mapToIndustry(industry: string): string {
  const industryMap: Record<string, string> = {
    'technology': 'Software / SaaS',
    'software': 'Software / SaaS',
    'saas': 'Software / SaaS',
    'fintech': 'Fintech',
    'financial': 'Fintech',
    'ecommerce': 'E-commerce / Retail',
    'retail': 'E-commerce / Retail',
    'healthcare': 'Healthcare / MedTech',
    'health': 'Healthcare / MedTech',
    'medical': 'Healthcare / MedTech',
    'education': 'EdTech',
    'edtech': 'EdTech',
    'manufacturing': 'Manufacturing',
    'consulting': 'Professional Services',
    'professional services': 'Professional Services',
    'marketing': 'Marketing / Advertising',
    'advertising': 'Marketing / Advertising',
    'real estate': 'Real Estate / PropTech',
    'proptech': 'Real Estate / PropTech',
    'logistics': 'Logistics / Supply Chain',
    'supply chain': 'Logistics / Supply Chain',
    'media': 'Media / Entertainment',
    'entertainment': 'Media / Entertainment',
    'travel': 'Travel / Hospitality',
    'hospitality': 'Travel / Hospitality'
  };

  const lowerIndustry = industry.toLowerCase();
  
  for (const [key, value] of Object.entries(industryMap)) {
    if (lowerIndustry.includes(key)) {
      return value;
    }
  }

  return 'Other';
}

export default router;

