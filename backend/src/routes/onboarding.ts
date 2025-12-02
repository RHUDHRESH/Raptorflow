import { Router, Response } from 'express';
import { z } from 'zod';
import { supabaseAdmin } from '../lib/supabase';
import { requireAuth, AuthenticatedRequest } from '../middleware/auth';
import { redis } from '../lib/redis';

const router = Router();

// Validation schemas
const intakeSectionSchema = z.enum(['goals', 'audience', 'positioning', 'execution']);
const intakeBodySchema = z.object({
  projectId: z.string().uuid(),
  section: intakeSectionSchema,
  data: z.record(z.string(), z.any()),
});

const lockBodySchema = z.object({
  projectId: z.string().uuid(),
});

// GET /api/onboarding/intake?projectId=...
router.get('/intake', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const userId = req.user!.id;
    const projectId = req.query.projectId as string;

    if (!projectId) {
      return res.status(400).json({ error: 'projectId is required' });
    }

    // 1. Verify project ownership
    const { data: project, error: projectError } = await supabaseAdmin
      .from('projects')
      .select('id')
      .eq('id', projectId)
      .eq('user_id', userId)
      .single();

    if (projectError || !project) {
      return res.status(404).json({ error: 'Project not found or access denied' });
    }

    // 2. Get intake
    const { data: intake, error: intakeError } = await supabaseAdmin
      .from('intake')
      .select('*')
      .eq('project_id', projectId)
      .single();

    if (intakeError && intakeError.code !== 'PGRST116') { // PGRST116 = JSON null / no rows
      console.error('Error fetching intake:', intakeError);
      return res.status(500).json({ error: 'Database error' });
    }

    // 3. If no intake exists, create a blank one
    if (!intake) {
      const { data: newIntake, error: createError } = await supabaseAdmin
        .from('intake')
        .insert({ project_id: projectId })
        .select('*')
        .single();
      
      if (createError) {
        console.error('Error creating intake:', createError);
        return res.status(500).json({ error: 'Failed to create intake record' });
      }
      return res.json(newIntake);
    }

    return res.json(intake);

  } catch (err) {
    console.error('GET intake error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /api/onboarding/intake
router.post('/intake', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const userId = req.user!.id;
    
    const parseResult = intakeBodySchema.safeParse(req.body);
    if (!parseResult.success) {
      return res.status(400).json({ error: parseResult.error });
    }
    
    const { projectId, section, data } = parseResult.data;

    // 1. Verify project ownership
    const { data: project, error: projectError } = await supabaseAdmin
      .from('projects')
      .select('id')
      .eq('id', projectId)
      .eq('user_id', userId)
      .single();

    if (projectError || !project) {
      return res.status(403).json({ error: 'Access denied to project' });
    }

    // 2. Upsert intake section
    // We need to check if intake exists to know if we insert or update.
    // But Supabase upsert might wipe other fields if not careful, so let's fetch first or use specific update.
    // Safest pattern: check existence -> update specific column.
    
    const { data: existingIntake } = await supabaseAdmin
      .from('intake')
      .select('id')
      .eq('project_id', projectId)
      .single();

    let error;
    let result;

    if (existingIntake) {
      const updatePayload = { [section]: data, updated_at: new Date() };
      ({ data: result, error } = await supabaseAdmin
        .from('intake')
        .update(updatePayload)
        .eq('project_id', projectId)
        .select()
        .single());
    } else {
      const insertPayload = {
        project_id: projectId,
        [section]: data
      };
      ({ data: result, error } = await supabaseAdmin
        .from('intake')
        .insert(insertPayload)
        .select()
        .single());
    }

    if (error) {
      console.error('Error updating intake:', error);
      return res.status(500).json({ error: 'Database update failed' });
    }

    return res.json(result);

  } catch (err) {
    console.error('POST intake error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /api/onboarding/lock-and-generate
router.post('/lock-and-generate', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const userId = req.user!.id;
    
    const parseResult = lockBodySchema.safeParse(req.body);
    if (!parseResult.success) {
      return res.status(400).json({ error: parseResult.error });
    }
    
    const { projectId } = parseResult.data;

    // 1. Verify project ownership
    const { data: project, error: projectError } = await supabaseAdmin
      .from('projects')
      .select('id')
      .eq('id', projectId)
      .eq('user_id', userId)
      .single();

    if (projectError || !project) {
      return res.status(403).json({ error: 'Access denied to project' });
    }

    // 2. Lock intake
    const { data: intake, error: lockError } = await supabaseAdmin
      .from('intake')
      .update({ locked_at: new Date().toISOString() })
      .eq('project_id', projectId)
      .select()
      .single();

    if (lockError) {
      console.error('Error locking intake:', lockError);
      return res.status(500).json({ error: 'Failed to lock intake' });
    }

    // 3. Create Plan (Draft)
    // Copy intake JSON to raw_outline as a placeholder
    const placeholderOutline = {
      source_intake: intake,
      note: "Pending AI Generation",
      version: "v0.1"
    };

    const { data: plan, error: planError } = await supabaseAdmin
      .from('plans')
      .insert({
        project_id: projectId,
        status: 'draft',
        raw_outline: placeholderOutline,
        raw_pillars: []
      })
      .select()
      .single();

    if (planError) {
      console.error('Error creating plan:', planError);
      return res.status(500).json({ error: 'Failed to create plan' });
    }

    // 4. (Stub) Push job to Upstash Redis for AI processing
    try {
        // Placeholder for actual AI pipeline job
        const job = {
            type: "GENERATE_PLAN",
            projectId: projectId,
            planId: plan.id,
            userId: userId,
            timestamp: Date.now()
        };
        
        // Pushing to a Redis list named 'ai-jobs'
        await redis.lpush('ai-jobs', JSON.stringify(job));
        console.log('Queued AI job:', job);
    } catch (redisError) {
        // Don't fail the request if Redis fails, just log it. 
        // In a real system, we might want robustness here.
        console.error('Failed to queue AI job:', redisError);
    }

    return res.json({ planId: plan.id, status: 'queued' });

  } catch (err) {
    console.error('Lock and generate error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export const onboardingRouter = router;
