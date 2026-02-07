import { Router, Request, Response } from 'express';
import { db } from '../lib/db';
import { supabase } from '../lib/supabase';
import type { CreateSpikeInput, SpikeStatus, SpikeType, BarrierType, ProtocolType, GoalType } from '../types';

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

// Helper: Get default barriers and protocols for spike type
function getSpikeDefaults(spikeType: SpikeType): { barriers: BarrierType[], protocols: ProtocolType[], goal: GoalType } {
  switch (spikeType) {
    case 'pipeline':
      return {
        barriers: ['OBSCURITY', 'RISK'],
        protocols: ['A_AUTHORITY_BLITZ', 'B_TRUST_ANCHOR'],
        goal: 'velocity'
      };
    case 'efficiency':
      return {
        barriers: ['RISK', 'INERTIA'],
        protocols: ['B_TRUST_ANCHOR', 'C_COST_OF_INACTION'],
        goal: 'efficiency'
      };
    case 'expansion':
      return {
        barriers: ['CAPACITY', 'ATROPHY'],
        protocols: ['E_ENTERPRISE_WEDGE', 'F_CHURN_INTERCEPT'],
        goal: 'penetration'
      };
  }
}

// Helper: Get first 3 move templates for a spike
async function getFirst3Moves(spikeType: SpikeType) {
  const { protocols } = getSpikeDefaults(spikeType);
  
  const { data: templates } = await db.moveTemplates.list();
  
  if (!templates) return [];
  
  // Get templates matching the protocols, max 3
  return templates
    .filter(t => protocols.includes(t.protocol_type as ProtocolType))
    .slice(0, 3);
}

/**
 * GET /api/spikes
 * List all spikes for the current user
 */
router.get('/', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const status = req.query.status as SpikeStatus | undefined;
    
    const { data, error } = await db.spikes.list(userId, { status });
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/spikes/:id
 * Get a specific spike with related data
 */
router.get('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const withRelations = req.query.withRelations === 'true';
    
    if (withRelations) {
      const { data, error } = await db.spikes.getWithRelations(id, userId);
      if (error || !data) {
        return res.status(404).json({ error: 'Spike not found' });
      }
      return res.json({ data });
    }
    
    const { data, error } = await db.spikes.getById(id, userId);
    
    if (error) {
      return res.status(404).json({ error: 'Spike not found' });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/spikes
 * Create a new spike
 */
router.post('/', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const spikeData: CreateSpikeInput = req.body;
    
    // Validation
    if (!spikeData.name) {
      return res.status(400).json({ error: 'Name is required' });
    }
    if (!spikeData.spike_type) {
      return res.status(400).json({ error: 'Spike type is required' });
    }
    if (!spikeData.start_date || !spikeData.end_date) {
      return res.status(400).json({ error: 'Start and end dates are required' });
    }
    if (!spikeData.targets || Object.keys(spikeData.targets).length === 0) {
      return res.status(400).json({ error: 'At least one target is required' });
    }
    
    // Apply defaults based on spike type
    const defaults = getSpikeDefaults(spikeData.spike_type);
    spikeData.goal = spikeData.goal || defaults.goal;
    spikeData.barriers = spikeData.barriers?.length ? spikeData.barriers : defaults.barriers;
    spikeData.protocols = spikeData.protocols?.length ? spikeData.protocols : defaults.protocols;
    
    const { data, error } = await db.spikes.create(userId, spikeData);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.status(201).json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * PATCH /api/spikes/:id
 * Update a spike
 */
router.patch('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const updates = req.body;
    
    const { data, error } = await db.spikes.update(id, userId, updates);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * PATCH /api/spikes/:id/status
 * Update spike status
 */
router.patch('/:id/status', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const { status } = req.body;
    
    const validStatuses: SpikeStatus[] = ['configuring', 'active', 'paused', 'completed', 'cancelled'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({ error: 'Invalid status' });
    }
    
    const { data, error } = await db.spikes.updateStatus(id, userId, status);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * DELETE /api/spikes/:id
 * Delete a spike
 */
router.delete('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { error } = await db.spikes.delete(id, userId);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ success: true });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/spikes/:id/activate
 * Activate a spike
 */
router.post('/:id/activate', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    // Get current spike
    const { data: spike, error: fetchError } = await db.spikes.getById(id, userId);
    
    if (fetchError || !spike) {
      return res.status(404).json({ error: 'Spike not found' });
    }
    
    if (spike.status !== 'configuring') {
      return res.status(400).json({ error: 'Spike must be in configuring status to activate' });
    }
    
    const { data, error } = await db.spikes.updateStatus(id, userId, 'active');
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/spikes/:id/first-moves
 * Get recommended first 3 moves for a spike
 */
router.get('/:id/first-moves', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    // Get spike
    const { data: spike, error: fetchError } = await db.spikes.getById(id, userId);
    
    if (fetchError || !spike) {
      return res.status(404).json({ error: 'Spike not found' });
    }
    
    const firstMoves = await getFirst3Moves(spike.spike_type);
    
    res.json({ data: firstMoves });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/spikes/:id/generate-moves
 * Generate the first 3 moves for a spike from templates
 */
router.post('/:id/generate-moves', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    // Get spike with relations
    const { data: spike, error: fetchError } = await db.spikes.getWithRelations(id, userId);
    
    if (fetchError || !spike) {
      return res.status(404).json({ error: 'Spike not found' });
    }
    
    // Get first 3 move templates
    const templates = await getFirst3Moves(spike.spike_type);
    
    if (templates.length === 0) {
      return res.status(400).json({ error: 'No move templates available for this spike type' });
    }
    
    // Create moves from templates
    const createdMoves = [];
    
    for (const template of templates) {
      const { data: move, error: moveError } = await db.moves.create(userId, {
        name: template.name,
        description: template.description,
        template_id: template.id,
        spike_id: id,
        campaign_id: spike.campaign_id,
        icp_id: spike.primary_icp_id,
        protocol: template.protocol_type as ProtocolType,
        channels: template.channels
      });
      
      if (!moveError && move) {
        createdMoves.push(move);
      }
    }
    
    // Update spike with move IDs
    const moveIds = createdMoves.map(m => m.id);
    await db.spikes.update(id, userId, { move_ids: moveIds });
    
    res.json({ data: createdMoves });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/spikes/:id/guardrails
 * Get guardrails for a spike
 */
router.get('/:id/guardrails', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { data, error } = await db.guardrails.list(userId, { spike_id: id });
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/spikes/:id/guardrails
 * Create a guardrail for a spike
 */
router.post('/:id/guardrails', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const guardrailData = req.body;
    
    // Verify spike exists
    const { data: spike, error: fetchError } = await db.spikes.getById(id, userId);
    
    if (fetchError || !spike) {
      return res.status(404).json({ error: 'Spike not found' });
    }
    
    const { data, error } = await db.guardrails.create(userId, {
      ...guardrailData,
      spike_id: id
    });
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.status(201).json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/spikes/:id/complete
 * Mark a spike as completed with results and learnings
 */
router.post('/:id/complete', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const { results, learnings } = req.body;
    
    // Get current spike
    const { data: spike, error: fetchError } = await db.spikes.getById(id, userId);
    
    if (fetchError || !spike) {
      return res.status(404).json({ error: 'Spike not found' });
    }
    
    // Update with results and learnings
    const { data, error } = await db.spikes.update(id, userId, {
      status: 'completed',
      completed_at: new Date().toISOString(),
      results: results || {},
      learnings: learnings || []
    });
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/spikes/defaults/:type
 * Get default configuration for a spike type
 */
router.get('/defaults/:type', verifyToken, async (req: Request, res: Response) => {
  try {
    const { type } = req.params;
    
    const validTypes: SpikeType[] = ['pipeline', 'efficiency', 'expansion'];
    if (!validTypes.includes(type as SpikeType)) {
      return res.status(400).json({ error: 'Invalid spike type' });
    }
    
    const defaults = getSpikeDefaults(type as SpikeType);
    const firstMoves = await getFirst3Moves(type as SpikeType);
    
    res.json({ 
      data: {
        ...defaults,
        suggested_moves: firstMoves
      }
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

export default router;

