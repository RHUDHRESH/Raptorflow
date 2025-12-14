import { Router, Request, Response } from 'express';
import { db } from '../lib/db';
import { supabase } from '../lib/supabase';
import type { CreateAssetInput, AssetStatus } from '../types';

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
 * GET /api/assets
 * List all assets for the current user
 */
router.get('/', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { move_id, campaign_id, status, asset_type } = req.query;
    
    const { data, error } = await db.assets.list(userId, {
      move_id: move_id as string,
      campaign_id: campaign_id as string,
      status: status as AssetStatus,
      asset_type: asset_type as string
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
 * GET /api/assets/:id
 * Get a specific asset
 */
router.get('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { data, error } = await db.assets.getById(id, userId);
    
    if (error) {
      return res.status(404).json({ error: 'Asset not found' });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/assets
 * Create a new asset
 */
router.post('/', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const assetData: CreateAssetInput = req.body;
    
    if (!assetData.name) {
      return res.status(400).json({ error: 'Name is required' });
    }
    if (!assetData.asset_type) {
      return res.status(400).json({ error: 'Asset type is required' });
    }
    
    const { data, error } = await db.assets.create(userId, assetData);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.status(201).json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * PATCH /api/assets/:id
 * Update an asset
 */
router.patch('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const updates = req.body;
    
    const { data, error } = await db.assets.update(id, userId, updates);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * PATCH /api/assets/:id/status
 * Update asset status
 */
router.patch('/:id/status', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const { status } = req.body;
    
    const validStatuses: AssetStatus[] = ['draft', 'generating', 'needs_review', 'approved', 'deployed', 'archived'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({ error: 'Invalid status' });
    }
    
    const { data, error } = await db.assets.updateStatus(id, userId, status);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/assets/:id/approve
 * Approve an asset
 */
router.post('/:id/approve', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { data, error } = await db.assets.updateStatus(id, userId, 'approved');
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/assets/:id/deploy
 * Mark an asset as deployed
 */
router.post('/:id/deploy', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const { distribution_links } = req.body;
    
    // Update status and distribution links
    const { data, error } = await db.assets.update(id, userId, {
      status: 'deployed',
      deployed_at: new Date().toISOString(),
      distribution_links: distribution_links || {}
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
 * POST /api/assets/:id/variants
 * Add a variant to an asset
 */
router.post('/:id/variants', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const { name, content } = req.body;
    
    if (!name || !content) {
      return res.status(400).json({ error: 'Name and content are required' });
    }
    
    // Get current asset
    const { data: asset, error: fetchError } = await db.assets.getById(id, userId);
    
    if (fetchError || !asset) {
      return res.status(404).json({ error: 'Asset not found' });
    }
    
    // Add new variant
    const newVariant = {
      id: `variant_${Date.now()}`,
      name,
      content,
      performance_data: {}
    };
    
    const variants = [...(asset.variants || []), newVariant];
    
    const { data, error } = await db.assets.update(id, userId, { variants });
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * DELETE /api/assets/:id
 * Delete an asset
 */
router.delete('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { error } = await db.assets.delete(id, userId);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ success: true });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/assets/types
 * Get available asset types
 */
router.get('/types/list', verifyToken, async (req: Request, res: Response) => {
  try {
    const assetTypes = [
      { type: 'pillar_webinar_script', label: 'Pillar Webinar Script', category: 'pillar' },
      { type: 'pillar_whitepaper', label: 'Pillar Whitepaper', category: 'pillar' },
      { type: 'pillar_keynote', label: 'Pillar Keynote', category: 'pillar' },
      { type: 'pillar_report', label: 'State of Industry Report', category: 'pillar' },
      { type: 'linkedin_post', label: 'LinkedIn Post', category: 'micro' },
      { type: 'twitter_thread', label: 'Twitter Thread', category: 'micro' },
      { type: 'short_video_script', label: 'Short Video Script', category: 'micro' },
      { type: 'carousel_copy', label: 'Carousel Copy', category: 'micro' },
      { type: 'battlecard', label: 'Sales Battlecard', category: 'sales' },
      { type: 'comparison_page', label: 'Us vs Them Page', category: 'sales' },
      { type: 'why_now_deck', label: 'Why Now Deck', category: 'sales' },
      { type: 'objection_handler', label: 'Objection Handler', category: 'sales' },
      { type: 'onboarding_email', label: 'Onboarding Email', category: 'lifecycle' },
      { type: 'activation_sequence', label: 'Activation Sequence', category: 'lifecycle' },
      { type: 'upsell_sequence', label: 'Upsell Sequence', category: 'lifecycle' },
      { type: 'churn_intercept', label: 'Churn Intercept Email', category: 'lifecycle' },
      { type: 'account_audit', label: 'Account Audit Report', category: 'abm' },
      { type: 'loom_script', label: 'Loom Video Script', category: 'abm' },
      { type: 'one_pager', label: 'One-Pager PDF', category: 'abm' },
      { type: 'roi_calculator_spec', label: 'ROI Calculator Spec', category: 'tools' },
      { type: 'value_calculator_spec', label: 'Value Calculator Spec', category: 'tools' }
    ];
    
    res.json({ data: assetTypes });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

export default router;

