import { Router, Request, Response } from 'express';
import { supabase } from '../lib/supabase';
import { RadarAgent } from '../agents/RadarAgent';
import { TrendScraperAgent } from '../agents/TrendScraperAgent';
import { ContentIdeaAgent } from '../agents/ContentIdeaAgent';
import { CohortTagGeneratorAgent } from '../agents/CohortTagGeneratorAgent';

const router = Router();

// Initialize agents
const radarAgent = new RadarAgent();
const trendScraperAgent = new TrendScraperAgent();
const contentIdeaAgent = new ContentIdeaAgent();
const cohortTagGeneratorAgent = new CohortTagGeneratorAgent();

// Middleware to verify JWT token
const verifyToken = async (req: Request, res: Response, next: Function) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing authorization' });
  }

  const token = authHeader.split(' ')[1];
  
  try {
    const { data: { user }, error } = await supabase.auth.getUser(token);
    if (error || !user) return res.status(401).json({ error: 'Invalid token' });
    (req as any).user = user;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Token verification failed' });
  }
};

/**
 * POST /api/radar/scan
 * Scan for opportunities matching a cohort's interests
 */
router.post('/scan', verifyToken, async (req: Request, res: Response) => {
  try {
    const { cohort_id, cohort_name, cohort_description, interest_tags, timeframe } = req.body;

    if (!cohort_id || !cohort_name || !interest_tags?.length) {
      return res.status(400).json({ error: 'cohort_id, cohort_name, and interest_tags are required' });
    }

    // First fetch current trends
    const trends = await trendScraperAgent.fetchTrends({
      region: 'IN',
      categories: interest_tags.slice(0, 10).map((t: any) => t.tag),
      limit: 30
    });

    // Then run radar analysis
    const result = await radarAgent.scan({
      cohort_id,
      cohort_name,
      cohort_description: cohort_description || '',
      interest_tags,
      recent_news: trends.trends.map(t => `${t.title}: ${t.description}`),
      timeframe: timeframe || 'this_week'
    });

    res.json({
      success: true,
      data: result,
      trends_scanned: trends.meta.total_trends,
      timestamp: new Date().toISOString()
    });
  } catch (err: any) {
    console.error('Radar scan error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/radar/trends
 * Get current trending topics
 */
router.get('/trends', verifyToken, async (req: Request, res: Response) => {
  try {
    const { region, categories, limit } = req.query;

    const trends = await trendScraperAgent.fetchTrends({
      region: (region as string) || 'IN',
      categories: categories ? (categories as string).split(',') : [],
      limit: parseInt(limit as string) || 50
    });

    res.json(trends);
  } catch (err: any) {
    console.error('Trends fetch error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/radar/generate-tags
 * Generate 50 interest tags for a cohort
 */
router.post('/generate-tags', verifyToken, async (req: Request, res: Response) => {
  try {
    const { cohort_name, cohort_description, firmographics, psychographics, existing_tags } = req.body;

    if (!cohort_name || !cohort_description) {
      return res.status(400).json({ error: 'cohort_name and cohort_description are required' });
    }

    const result = await cohortTagGeneratorAgent.generateTags({
      cohort_name,
      cohort_description,
      firmographics,
      psychographics,
      existing_tags
    });

    res.json({
      success: true,
      data: result
    });
  } catch (err: any) {
    console.error('Tag generation error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/radar/content-idea
 * Generate a detailed content idea from an opportunity
 */
router.post('/content-idea', verifyToken, async (req: Request, res: Response) => {
  try {
    const { 
      opportunity_title,
      opportunity_description,
      trend_type,
      cohort_name,
      cohort_description,
      matching_tags,
      format,
      platform,
      brand_voice,
      brand_guidelines
    } = req.body;

    if (!opportunity_title || !cohort_name || !format || !platform) {
      return res.status(400).json({ 
        error: 'opportunity_title, cohort_name, format, and platform are required' 
      });
    }

    const result = await contentIdeaAgent.generateIdea({
      opportunity_title,
      opportunity_description: opportunity_description || '',
      trend_type: trend_type || 'breaking_news',
      cohort_name,
      cohort_description: cohort_description || '',
      matching_tags: matching_tags || [],
      format,
      platform,
      brand_voice,
      brand_guidelines
    });

    res.json({
      success: true,
      data: result
    });
  } catch (err: any) {
    console.error('Content idea generation error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/radar/multi-platform-ideas
 * Generate content ideas for multiple platforms at once
 */
router.post('/multi-platform-ideas', verifyToken, async (req: Request, res: Response) => {
  try {
    const { 
      opportunity_title,
      opportunity_description,
      trend_type,
      cohort_name,
      cohort_description,
      matching_tags,
      platforms,
      brand_voice,
      brand_guidelines
    } = req.body;

    if (!opportunity_title || !cohort_name || !platforms?.length) {
      return res.status(400).json({ 
        error: 'opportunity_title, cohort_name, and platforms are required' 
      });
    }

    const results = await contentIdeaAgent.generateMultiPlatformIdeas(
      {
        opportunity_title,
        opportunity_description: opportunity_description || '',
        trend_type: trend_type || 'breaking_news',
        cohort_name,
        cohort_description: cohort_description || '',
        matching_tags: matching_tags || [],
        brand_voice,
        brand_guidelines
      },
      platforms
    );

    res.json({
      success: true,
      data: results
    });
  } catch (err: any) {
    console.error('Multi-platform ideas error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/radar/industry-trends/:industry
 * Get trends for a specific industry
 */
router.get('/industry-trends/:industry', verifyToken, async (req: Request, res: Response) => {
  try {
    const { industry } = req.params;
    const trends = await trendScraperAgent.getIndustryTrends(industry);
    
    res.json({
      success: true,
      industry,
      trends
    });
  } catch (err: any) {
    console.error('Industry trends error:', err);
    res.status(500).json({ error: err.message });
  }
});

export default router;

