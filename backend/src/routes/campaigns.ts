import { Router, Request, Response } from 'express';
import { db } from '../lib/db';
import { supabase } from '../lib/supabase';
import type { CreateCampaignInput, CampaignStatus, BarrierType, ProtocolType } from '../types';

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

// Helper: Get recommended protocols for barriers
function getRecommendedProtocols(barriers: BarrierType[]): ProtocolType[] {
  const protocolMap: Record<BarrierType, ProtocolType> = {
    'OBSCURITY': 'A_AUTHORITY_BLITZ',
    'RISK': 'B_TRUST_ANCHOR',
    'INERTIA': 'C_COST_OF_INACTION',
    'FRICTION': 'D_HABIT_HARDCODE',
    'CAPACITY': 'E_ENTERPRISE_WEDGE',
    'ATROPHY': 'F_CHURN_INTERCEPT'
  };
  
  return barriers.map(b => protocolMap[b]).filter(Boolean);
}

/**
 * GET /api/campaigns
 * List all campaigns for the current user
 */
router.get('/', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const status = req.query.status as CampaignStatus | undefined;
    
    const { data, error } = await db.campaigns.list(userId, { status });
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/campaigns/:id
 * Get a specific campaign with related data
 */
router.get('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const withRelations = req.query.withRelations === 'true';
    
    if (withRelations) {
      const { data, error } = await db.campaigns.getWithRelations(id, userId);
      if (error || !data) {
        return res.status(404).json({ error: 'Campaign not found' });
      }
      return res.json({ data });
    }
    
    const { data, error } = await db.campaigns.getById(id, userId);
    
    if (error) {
      return res.status(404).json({ error: 'Campaign not found' });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/campaigns
 * Create a new campaign
 */
router.post('/', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const campaignData: CreateCampaignInput = req.body;
    
    // Validation
    if (!campaignData.name) {
      return res.status(400).json({ error: 'Name is required' });
    }
    if (!campaignData.goal) {
      return res.status(400).json({ error: 'Goal is required' });
    }
    if (!campaignData.demand_source) {
      return res.status(400).json({ error: 'Demand source is required' });
    }
    if (!campaignData.persuasion_axis) {
      return res.status(400).json({ error: 'Persuasion axis is required' });
    }
    
    // Auto-suggest protocols if barriers are provided but protocols aren't
    if (campaignData.primary_barriers?.length && !campaignData.protocols?.length) {
      campaignData.protocols = getRecommendedProtocols(campaignData.primary_barriers);
    }
    
    const { data, error } = await db.campaigns.create(userId, campaignData);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.status(201).json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * PATCH /api/campaigns/:id
 * Update a campaign
 */
router.patch('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const updates = req.body;
    
    const { data, error } = await db.campaigns.update(id, userId, updates);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * PATCH /api/campaigns/:id/status
 * Update campaign status
 */
router.patch('/:id/status', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const { status } = req.body;
    
    const validStatuses: CampaignStatus[] = ['draft', 'planned', 'active', 'paused', 'completed', 'cancelled'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({ error: 'Invalid status' });
    }
    
    const { data, error } = await db.campaigns.updateStatus(id, userId, status);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * DELETE /api/campaigns/:id
 * Delete a campaign
 */
router.delete('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { error } = await db.campaigns.delete(id, userId);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ success: true });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/campaigns/:id/moves
 * Get all moves for a campaign
 */
router.get('/:id/moves', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { data, error } = await db.moves.list(userId, { campaign_id: id });
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/campaigns/:id/assets
 * Get all assets for a campaign
 */
router.get('/:id/assets', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { data, error } = await db.assets.list(userId, { campaign_id: id });
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/campaigns/:id/activate
 * Activate a campaign (move from planned to active)
 */
router.post('/:id/activate', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    // Get current campaign
    const { data: campaign, error: fetchError } = await db.campaigns.getById(id, userId);
    
    if (fetchError || !campaign) {
      return res.status(404).json({ error: 'Campaign not found' });
    }
    
    if (campaign.status !== 'planned' && campaign.status !== 'draft') {
      return res.status(400).json({ error: 'Campaign must be in planned or draft status to activate' });
    }
    
    const { data, error } = await db.campaigns.updateStatus(id, userId, 'active');
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/campaigns/:id/pause
 * Pause a campaign
 */
router.post('/:id/pause', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { data, error } = await db.campaigns.updateStatus(id, userId, 'paused');
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/campaigns/:id/complete
 * Mark a campaign as completed
 */
router.post('/:id/complete', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { data, error } = await db.campaigns.updateStatus(id, userId, 'completed');
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/campaigns/recommend-protocols
 * Get protocol recommendations based on barriers
 */
router.post('/recommend-protocols', verifyToken, async (req: Request, res: Response) => {
  try {
    const { barriers } = req.body;
    
    if (!Array.isArray(barriers)) {
      return res.status(400).json({ error: 'barriers must be an array' });
    }
    
    const recommendedProtocols = getRecommendedProtocols(barriers);
    
    // Get full protocol details
    const { data: protocols } = await db.protocols.list();
    const recommended = protocols?.filter(p => recommendedProtocols.includes(p.code as ProtocolType)) || [];
    
    res.json({ data: recommended });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

export default router;

