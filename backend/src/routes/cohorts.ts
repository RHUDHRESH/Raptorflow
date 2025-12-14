/**
 * Cohorts API Routes
 * 
 * Handles cohort CRUD with automatic tag generation
 * Enforces tier limits: Ascent=3, Glide=5, Soar=10
 */

import { Router, Request, Response } from 'express';
import { db, supabase } from '../lib/supabase';
import { CohortTagGeneratorAgent } from '../agents/CohortTagGeneratorAgent';
import { CohortBuilderAgent } from '../agents/CohortBuilderAgent';

const router = Router();

// Initialize agents
const tagGeneratorAgent = new CohortTagGeneratorAgent();
const cohortBuilderAgent = new CohortBuilderAgent();

// Tier limits
const TIER_LIMITS = {
  'ascent': 3,
  'glide': 5,
  'soar': 10,
  'free': 1 // Free tier gets 1 cohort
};

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
 * GET /api/cohorts
 * Get all cohorts for the current user
 */
router.get('/', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    
    const { data, error } = await supabase
      .from('cohorts')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (error) throw error;

    res.json({ 
      success: true, 
      data: data || [],
      count: data?.length || 0
    });
  } catch (err: any) {
    console.error('Get cohorts error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/cohorts/:id
 * Get a specific cohort with full details
 */
router.get('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;

    const { data, error } = await supabase
      .from('cohorts')
      .select('*')
      .eq('id', id)
      .eq('user_id', userId)
      .single();

    if (error) throw error;
    if (!data) return res.status(404).json({ error: 'Cohort not found' });

    res.json({ success: true, data });
  } catch (err: any) {
    console.error('Get cohort error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/cohorts
 * Create a new cohort - automatically generates 50 interest tags
 */
router.post('/', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { 
      name, 
      description,
      firmographics,
      psychographics,
      generate_tags = true // Auto-generate tags by default
    } = req.body;

    if (!name || !description) {
      return res.status(400).json({ error: 'name and description are required' });
    }

    // Check tier limits
    const { data: profile } = await supabase
      .from('profiles')
      .select('plan')
      .eq('id', userId)
      .single();

    const userPlan = profile?.plan || 'free';
    const limit = TIER_LIMITS[userPlan as keyof typeof TIER_LIMITS] || 1;

    const { count } = await supabase
      .from('cohorts')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', userId);

    if ((count || 0) >= limit) {
      return res.status(403).json({ 
        error: `Cohort limit reached. Your ${userPlan} plan allows ${limit} cohorts.`,
        limit,
        current: count,
        upgrade_needed: true
      });
    }

    // Generate interest tags using AI agent
    let interest_tags: any[] = [];
    if (generate_tags) {
      try {
        const tagResult = await tagGeneratorAgent.generateTags({
          cohort_name: name,
          cohort_description: description,
          firmographics,
          psychographics
        });
        interest_tags = tagResult.tags;
      } catch (tagError) {
        console.error('Tag generation error:', tagError);
        // Continue without tags - can regenerate later
      }
    }

    // Create cohort
    const { data, error } = await supabase
      .from('cohorts')
      .insert({
        user_id: userId,
        name,
        description,
        firmographics: firmographics || {},
        psychographics: psychographics || {},
        interest_tags,
        tags_count: interest_tags.length,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      })
      .select()
      .single();

    if (error) throw error;

    res.status(201).json({ 
      success: true, 
      data,
      tags_generated: interest_tags.length
    });
  } catch (err: any) {
    console.error('Create cohort error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * PUT /api/cohorts/:id
 * Update a cohort
 */
router.put('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const updates = req.body;

    // Don't allow updating user_id
    delete updates.user_id;
    updates.updated_at = new Date().toISOString();

    const { data, error } = await supabase
      .from('cohorts')
      .update(updates)
      .eq('id', id)
      .eq('user_id', userId)
      .select()
      .single();

    if (error) throw error;
    if (!data) return res.status(404).json({ error: 'Cohort not found' });

    res.json({ success: true, data });
  } catch (err: any) {
    console.error('Update cohort error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * DELETE /api/cohorts/:id
 * Delete a cohort
 */
router.delete('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;

    const { error } = await supabase
      .from('cohorts')
      .delete()
      .eq('id', id)
      .eq('user_id', userId);

    if (error) throw error;

    res.json({ success: true });
  } catch (err: any) {
    console.error('Delete cohort error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/cohorts/:id/regenerate-tags
 * Regenerate interest tags for a cohort
 */
router.post('/:id/regenerate-tags', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;

    // Get cohort
    const { data: cohort, error: fetchError } = await supabase
      .from('cohorts')
      .select('*')
      .eq('id', id)
      .eq('user_id', userId)
      .single();

    if (fetchError) throw fetchError;
    if (!cohort) return res.status(404).json({ error: 'Cohort not found' });

    // Regenerate tags
    const tagResult = await tagGeneratorAgent.generateTags({
      cohort_name: cohort.name,
      cohort_description: cohort.description,
      firmographics: cohort.firmographics,
      psychographics: cohort.psychographics,
      existing_tags: cohort.interest_tags?.map((t: any) => t.tag)
    });

    // Update cohort with new tags
    const { data, error } = await supabase
      .from('cohorts')
      .update({
        interest_tags: tagResult.tags,
        tags_count: tagResult.tags.length,
        updated_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single();

    if (error) throw error;

    res.json({ 
      success: true, 
      data,
      tags_generated: tagResult.tags.length,
      meta: tagResult.meta
    });
  } catch (err: any) {
    console.error('Regenerate tags error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/cohorts/generate-from-description
 * AI generates a full cohort from a simple description
 */
router.post('/generate-from-description', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { description } = req.body;

    if (!description) {
      return res.status(400).json({ error: 'description is required' });
    }

    // Check tier limits first
    const { data: profile } = await supabase
      .from('profiles')
      .select('plan')
      .eq('id', userId)
      .single();

    const userPlan = profile?.plan || 'free';
    const limit = TIER_LIMITS[userPlan as keyof typeof TIER_LIMITS] || 1;

    const { count } = await supabase
      .from('cohorts')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', userId);

    if ((count || 0) >= limit) {
      return res.status(403).json({ 
        error: `Cohort limit reached. Your ${userPlan} plan allows ${limit} cohorts.`,
        limit,
        current: count,
        upgrade_needed: true
      });
    }

    // Use AI to build full cohort from description
    const cohortData = await cohortBuilderAgent.buildFromDescription(description);

    // Generate interest tags
    const tagResult = await tagGeneratorAgent.generateTags({
      cohort_name: cohortData.name,
      cohort_description: cohortData.description,
      firmographics: cohortData.firmographics,
      psychographics: cohortData.psychographics
    });

    // Create cohort
    const { data, error } = await supabase
      .from('cohorts')
      .insert({
        user_id: userId,
        name: cohortData.name,
        description: cohortData.description,
        firmographics: cohortData.firmographics,
        psychographics: cohortData.psychographics,
        behavioral_triggers: cohortData.behavioral_triggers,
        buying_committee: cohortData.buying_committee,
        category_context: cohortData.category_context,
        interest_tags: tagResult.tags,
        tags_count: tagResult.tags.length,
        fit_score: cohortData.fit_score,
        messaging_angle: cohortData.messaging_angle,
        qualification_questions: cohortData.qualification_questions,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      })
      .select()
      .single();

    if (error) throw error;

    res.status(201).json({ 
      success: true, 
      data,
      tags_generated: tagResult.tags.length,
      ai_generated: true
    });
  } catch (err: any) {
    console.error('Generate cohort error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/cohorts/limits
 * Get current cohort usage and limits
 */
router.get('/limits/check', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;

    const { data: profile } = await supabase
      .from('profiles')
      .select('plan')
      .eq('id', userId)
      .single();

    const userPlan = profile?.plan || 'free';
    const limit = TIER_LIMITS[userPlan as keyof typeof TIER_LIMITS] || 1;

    const { count } = await supabase
      .from('cohorts')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', userId);

    res.json({
      plan: userPlan,
      limit,
      used: count || 0,
      remaining: limit - (count || 0),
      can_create: (count || 0) < limit
    });
  } catch (err: any) {
    console.error('Check limits error:', err);
    res.status(500).json({ error: err.message });
  }
});

export default router;

