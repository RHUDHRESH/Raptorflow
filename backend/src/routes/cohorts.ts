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

const hydrateCohort = (row: any) => {
  const meta = row?.rules && typeof row.rules === 'object' && !Array.isArray(row.rules) ? row.rules : {};
  return {
    ...row,
    ...meta,
    user_id: row?.created_by,
  };
};

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
    const userEmail = (req as any).user.email;

    const { data: organizationId, error: orgError } = await db.getOrCreateCurrentOrgId(userId, userEmail);
    if (orgError || !organizationId) {
      return res.status(500).json({ error: 'Failed to resolve organization' });
    }
    
    const { data, error } = await supabase
      .from('cohorts')
      .select('*')
      .eq('organization_id', organizationId)
      .is('deleted_at', null)
      .order('created_at', { ascending: false });

    if (error) throw error;

    res.json({ 
      success: true, 
      data: (data || []).map(hydrateCohort),
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
    const userEmail = (req as any).user.email;
    const { id } = req.params;

    const { data: organizationId, error: orgError } = await db.getOrCreateCurrentOrgId(userId, userEmail);
    if (orgError || !organizationId) {
      return res.status(500).json({ error: 'Failed to resolve organization' });
    }

    const { data, error } = await supabase
      .from('cohorts')
      .select('*')
      .eq('id', id)
      .eq('organization_id', organizationId)
      .is('deleted_at', null)
      .single();

    if (error) throw error;
    if (!data) return res.status(404).json({ error: 'Cohort not found' });

    res.json({ success: true, data: hydrateCohort(data) });
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
    const userEmail = (req as any).user.email;
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

    const { data: organizationId, error: orgError } = await db.getOrCreateCurrentOrgId(userId, userEmail);
    if (orgError || !organizationId) {
      return res.status(500).json({ error: 'Failed to resolve organization' });
    }

    const { data: limits, error: limitsError } = await db.getOrgPlanCohortLimit(organizationId);
    if (limitsError) {
      return res.status(500).json({ error: 'Failed to resolve plan limits' });
    }

    const limit = (limits as any)?.cohortLimit || 1;

    const { count } = await supabase
      .from('cohorts')
      .select('*', { count: 'exact', head: true })
      .eq('organization_id', organizationId)
      .is('deleted_at', null);

    if ((count || 0) >= limit) {
      return res.status(403).json({ 
        error: `Cohort limit reached. Your plan allows ${limit} cohorts.`,
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
        organization_id: organizationId,
        created_by: userId,
        name,
        description,
        rules: {
          firmographics: firmographics || {},
          psychographics: psychographics || {},
          interest_tags,
          tags_count: interest_tags.length,
          status: 'active'
        },
        is_active: true,
      })
      .select()
      .single();

    if (error) throw error;

    res.status(201).json({ 
      success: true, 
      data: hydrateCohort(data),
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
    const userEmail = (req as any).user.email;
    const { id } = req.params;
    const updates = req.body;

    const { data: organizationId, error: orgError } = await db.getOrCreateCurrentOrgId(userId, userEmail);
    if (orgError || !organizationId) {
      return res.status(500).json({ error: 'Failed to resolve organization' });
    }

    // Don't allow updating ownership
    delete updates.user_id;
    delete updates.created_by;
    delete updates.organization_id;

    const { data: existing, error: fetchError } = await supabase
      .from('cohorts')
      .select('*')
      .eq('id', id)
      .eq('organization_id', organizationId)
      .is('deleted_at', null)
      .single();

    if (fetchError) throw fetchError;

    const meta = existing?.rules && typeof existing.rules === 'object' && !Array.isArray(existing.rules)
      ? { ...existing.rules }
      : {};

    const nextMeta = {
      ...meta,
      ...(updates.firmographics ? { firmographics: updates.firmographics } : {}),
      ...(updates.psychographics ? { psychographics: updates.psychographics } : {}),
      ...(updates.behavioral_triggers ? { behavioral_triggers: updates.behavioral_triggers } : {}),
      ...(updates.buying_committee ? { buying_committee: updates.buying_committee } : {}),
      ...(updates.category_context ? { category_context: updates.category_context } : {}),
      ...(updates.fit_score ? { fit_score: updates.fit_score } : {}),
      ...(updates.messaging_angle ? { messaging_angle: updates.messaging_angle } : {}),
      ...(updates.qualification_questions ? { qualification_questions: updates.qualification_questions } : {}),
      ...(updates.interest_tags ? { interest_tags: updates.interest_tags, tags_count: updates.interest_tags.length } : {}),
    };

    const updatePayload: any = {
      ...(typeof updates.name === 'string' ? { name: updates.name } : {}),
      ...(typeof updates.description === 'string' ? { description: updates.description } : {}),
      rules: nextMeta,
    };

    const { data, error } = await supabase
      .from('cohorts')
      .update(updatePayload)
      .eq('id', id)
      .eq('organization_id', organizationId)
      .eq('created_by', userId)
      .select()
      .single();

    if (error) throw error;
    if (!data) return res.status(404).json({ error: 'Cohort not found' });

    res.json({ success: true, data: hydrateCohort(data) });
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
    const userEmail = (req as any).user.email;
    const { id } = req.params;

    const { data: organizationId, error: orgError } = await db.getOrCreateCurrentOrgId(userId, userEmail);
    if (orgError || !organizationId) {
      return res.status(500).json({ error: 'Failed to resolve organization' });
    }

    const { error } = await supabase
      .from('cohorts')
      .update({ deleted_at: new Date().toISOString() })
      .eq('id', id)
      .eq('organization_id', organizationId)
      .eq('created_by', userId);

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
    const userEmail = (req as any).user.email;
    const { id } = req.params;

    const { data: organizationId, error: orgError } = await db.getOrCreateCurrentOrgId(userId, userEmail);
    if (orgError || !organizationId) {
      return res.status(500).json({ error: 'Failed to resolve organization' });
    }

    // Get cohort
    const { data: cohort, error: fetchError } = await supabase
      .from('cohorts')
      .select('*')
      .eq('id', id)
      .eq('organization_id', organizationId)
      .is('deleted_at', null)
      .single();

    if (fetchError) throw fetchError;
    if (!cohort) return res.status(404).json({ error: 'Cohort not found' });

    const meta = cohort?.rules && typeof cohort.rules === 'object' && !Array.isArray(cohort.rules)
      ? cohort.rules
      : {};

    // Regenerate tags
    const tagResult = await tagGeneratorAgent.generateTags({
      cohort_name: cohort.name,
      cohort_description: cohort.description,
      firmographics: meta.firmographics,
      psychographics: meta.psychographics,
      existing_tags: meta.interest_tags?.map((t: any) => t.tag)
    });

    // Update cohort with new tags
    const { data, error } = await supabase
      .from('cohorts')
      .update({
        rules: {
          ...meta,
          interest_tags: tagResult.tags,
          tags_count: tagResult.tags.length,
        }
      })
      .eq('id', id)
      .select()
      .single();

    if (error) throw error;

    res.json({ 
      success: true, 
      data: hydrateCohort(data),
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
    const userEmail = (req as any).user.email;
    const { description } = req.body;

    if (!description) {
      return res.status(400).json({ error: 'description is required' });
    }

    const { data: organizationId, error: orgError } = await db.getOrCreateCurrentOrgId(userId, userEmail);
    if (orgError || !organizationId) {
      return res.status(500).json({ error: 'Failed to resolve organization' });
    }

    const { data: limits, error: limitsError } = await db.getOrgPlanCohortLimit(organizationId);
    if (limitsError) {
      return res.status(500).json({ error: 'Failed to resolve plan limits' });
    }

    const limit = (limits as any)?.cohortLimit || 1;

    const { count } = await supabase
      .from('cohorts')
      .select('*', { count: 'exact', head: true })
      .eq('organization_id', organizationId)
      .is('deleted_at', null);

    if ((count || 0) >= limit) {
      return res.status(403).json({ 
        error: `Cohort limit reached. Your plan allows ${limit} cohorts.`,
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
      firmographics: cohortData.firmographics as any,
      psychographics: cohortData.psychographics as any
    });

    // Create cohort
    const { data, error } = await supabase
      .from('cohorts')
      .insert({
        organization_id: organizationId,
        created_by: userId,
        name: cohortData.name,
        description: cohortData.description,
        rules: {
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
          status: 'active'
        },
        is_active: true,
      })
      .select()
      .single();

    if (error) throw error;

    res.status(201).json({ 
      success: true, 
      data: hydrateCohort(data),
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

    const { data: organizationId, error: orgError } = await db.getOrCreateCurrentOrgId(userId);
    if (orgError || !organizationId) {
      return res.status(500).json({ error: 'Failed to resolve organization' });
    }

    const { data: limits, error: limitsError } = await db.getOrgPlanCohortLimit(organizationId);
    if (limitsError) {
      return res.status(500).json({ error: 'Failed to resolve plan limits' });
    }

    const limit = (limits as any)?.cohortLimit || 1;
    const plan = (limits as any)?.planCode || 'free';

    const { count } = await supabase
      .from('cohorts')
      .select('*', { count: 'exact', head: true })
      .eq('organization_id', organizationId)
      .is('deleted_at', null);

    res.json({
      plan,
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

