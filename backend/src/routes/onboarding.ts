import { Router, Request, Response } from 'express';
import { db, supabase } from '../lib/supabase';
import { orchestrator } from '../lib/orchestrator';

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
 * GET /api/onboarding/intake
 * Get or create onboarding intake for the current user
 */
router.get('/intake', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { data, error } = await db.getOrCreateIntake(userId);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }

    res.json(data);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/onboarding/intake
 * Save step data and trigger agent processing
 */
router.post('/intake', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { step, data } = req.body;

    if (!step || !data) {
      return res.status(400).json({ error: 'Step and data are required' });
    }

    // Get or create intake
    let { data: intake, error } = await db.getOrCreateIntake(userId);
    
    if (error || !intake) {
      return res.status(500).json({ error: 'Failed to get intake' });
    }

    // Update step data
    const updateData: any = {
      current_step: step,
      completed_steps: [...new Set([...(intake.completed_steps || []), step])]
    };

    // Map step to field
    switch (step) {
      case 1:
        updateData.positioning = data.positioning;
        break;
      case 2:
        updateData.company = data.company;
        break;
      case 3:
        updateData.product = data.product;
        break;
      case 4:
        updateData.market = data.market;
        break;
      case 5:
        updateData.strategy = data.strategy;
        break;
    }

    // Update intake
    const { data: updatedIntake } = await db.updateIntake(intake.id, updateData);

    // Process step with orchestrator (runs agents)
    const processingResult = await orchestrator.processStep(intake.id, step, data);

    // Return updated intake
    const { data: finalIntake } = await db.getIntake(userId);
    
    res.json({
      intake: finalIntake,
      processing: processingResult
    });
  } catch (err: any) {
    console.error('Error processing step:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/onboarding/generate-icps
 * Trigger ICP generation
 */
router.post('/generate-icps', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { data: intake, error } = await db.getIntake(userId);
    
    if (error || !intake) {
      return res.status(404).json({ error: 'Intake not found' });
    }

    // Check prerequisites
    const requiredSteps = [1, 2, 3, 4, 5];
    const completedSteps = intake.completed_steps || [];
    const missingSteps = requiredSteps.filter(s => !completedSteps.includes(s));
    
    if (missingSteps.length > 0) {
      return res.status(400).json({ 
        error: 'Complete all steps before generating ICPs',
        missingSteps 
      });
    }

    // Generate ICPs
    const result = await orchestrator.generateICPs(intake.id, intake);

    res.json(result);
  } catch (err: any) {
    console.error('Error generating ICPs:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/onboarding/generate-warplan
 * Trigger War Plan generation
 */
router.post('/generate-warplan', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { data: intake, error } = await db.getIntake(userId);
    
    if (error || !intake) {
      return res.status(404).json({ error: 'Intake not found' });
    }

    // Check ICPs exist
    if (!intake.icps || intake.icps.length === 0) {
      return res.status(400).json({ error: 'Generate ICPs first' });
    }

    // Generate War Plan
    const result = await orchestrator.generateWarPlan(intake.id, intake);

    res.json(result);
  } catch (err: any) {
    console.error('Error generating war plan:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/onboarding/complete
 * Mark onboarding as complete
 */
router.post('/complete', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { data: intake, error } = await db.getIntake(userId);
    
    if (error || !intake) {
      return res.status(404).json({ error: 'Intake not found' });
    }

    // Update profile to mark onboarding complete
    await db.updateProfile(userId, {
      onboarding_completed: true,
      onboarding_completed_at: new Date().toISOString()
    });

    res.json({ success: true });
  } catch (err: any) {
    console.error('Error completing onboarding:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/onboarding/reset
 * Reset onboarding to start fresh
 */
router.post('/reset', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { data: intake, error } = await db.getIntake(userId);
    
    if (error || !intake) {
      return res.status(404).json({ error: 'Intake not found' });
    }

    // Reset intake
    await db.updateIntake(intake.id, {
      positioning: {},
      positioning_derived: {},
      company: {},
      company_enriched: {},
      product: {},
      product_derived: {},
      market: {},
      market_system_view: {},
      strategy: {},
      strategy_derived: {},
      icps: [],
      war_plan: {},
      current_step: 1,
      completed_steps: []
    });

    // Update profile
    await db.updateProfile(userId, {
      onboarding_completed: false,
      onboarding_completed_at: null
    });

    res.json({ success: true });
  } catch (err: any) {
    console.error('Error resetting onboarding:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/onboarding/status
 * Get onboarding completion status
 */
router.get('/status', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    
    const { data: profile } = await db.getProfile(userId);
    const { data: intake } = await db.getIntake(userId);

    res.json({
      completed: profile?.onboarding_completed || false,
      completedAt: profile?.onboarding_completed_at,
      plan: profile?.plan,
      planStatus: profile?.plan_status,
      currentStep: intake?.current_step || 1,
      completedSteps: intake?.completed_steps || [],
      hasICPs: intake?.icps?.length > 0,
      hasWarPlan: intake?.war_plan?.generated || false
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

export default router;

