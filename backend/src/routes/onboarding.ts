import { Router, Response } from 'express';
import { z } from 'zod';
import { supabaseAdmin } from '../lib/supabase';
import { requireAuth, AuthenticatedRequest } from '../middleware/auth';
import { redis } from '../lib/redis';
import { analyzeBattlefield, BattlefieldAnalysis } from '../lib/onboarding/analyzeBattlefield';
import { generatePositioningBlueprint, PositioningBlueprint } from '../lib/onboarding/generatePositioningBlueprint';

const router = Router();

// Validation schemas
const positioningBodySchema = z.object({
  analysisId: z.string().uuid("Invalid analysis ID"),
  userConfidence: z.enum(['spot_on', 'mostly', 'not_really']),
  primaryFocus: z.enum(['revenue', 'pipeline', 'retention', 'brand']),
});

const analyzeBodySchema = z.object({
  description: z.string().trim().min(1, "Description is required"),
  websiteUrl: z.string().trim().optional().nullable().transform(val => val === "" ? null : val),
  geography: z.string().trim().optional().nullable().transform(val => val === "" ? null : val),
  industry: z.string().trim().optional().nullable().transform(val => val === "" ? null : val),
});

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

// POST /api/onboarding/analyze
router.post('/analyze', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const userId = req.user!.id;
    
    const parseResult = analyzeBodySchema.safeParse(req.body);
    if (!parseResult.success) {
      return res.status(400).json({ error: parseResult.error });
    }

    const input = parseResult.data;

    // Call LLM
    const llmResult = await analyzeBattlefield(input);

    // Persist to DB
    const { data: savedAnalysis, error } = await supabaseAdmin
      .from('onboarding_analyses')
      .insert({
        user_id: userId,
        description: input.description,
        website_url: input.websiteUrl,
        geography: input.geography,
        industry: input.industry,
        analysis: llmResult
      })
      .select('id, created_at')
      .single();

    if (error) {
      console.error('Database insertion error:', error);
      return res.status(500).json({ error: 'Failed to save analysis' });
    }

    // Construct response
    const response: BattlefieldAnalysis = {
      analysisId: savedAnalysis.id,
      createdAt: savedAnalysis.created_at,
      ...llmResult
    };

    return res.json(response);

  } catch (err) {
    console.error('Analyze error:', err);
    res.status(500).json({ error: 'Failed to analyze business data' });
  }
});

// POST /api/onboarding/positioning
router.post('/positioning', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const userId = req.user!.id;

    const parseResult = positioningBodySchema.safeParse(req.body);
    if (!parseResult.success) {
      return res.status(400).json({ error: parseResult.error });
    }

    const { analysisId, userConfidence, primaryFocus } = parseResult.data;

    // 1. Fetch existing analysis
    const { data: analysisRow, error: fetchError } = await supabaseAdmin
      .from('onboarding_analyses')
      .select('*')
      .eq('id', analysisId)
      .eq('user_id', userId)
      .single();

    if (fetchError || !analysisRow) {
      return res.status(404).json({ error: 'Analysis not found or access denied' });
    }

    // 2. Generate Blueprint
    const blueprintLLM = await generatePositioningBlueprint(
      analysisRow.analysis,
      userConfidence,
      primaryFocus
    );

    // 3. Persist Blueprint
    const { data: savedBlueprint, error: saveError } = await supabaseAdmin
      .from('positioning_blueprints')
      .insert({
        user_id: userId,
        analysis_id: analysisId,
        primary_focus: primaryFocus,
        user_confidence: userConfidence,
        blueprint: blueprintLLM
      })
      .select('id, created_at')
      .single();

    if (saveError) {
      console.error('Database insertion error:', saveError);
      return res.status(500).json({ error: 'Failed to save positioning blueprint' });
    }

    // 4. Return Response
    const response: PositioningBlueprint = {
      blueprintId: savedBlueprint.id,
      analysisId: analysisId,
      createdAt: savedBlueprint.created_at,
      ...blueprintLLM
    };

    return res.json(response);

  } catch (err) {
    console.error('Positioning generation error:', err);
    res.status(500).json({ error: 'Failed to generate positioning blueprint' });
  }
});

export const onboardingRouter = router;
