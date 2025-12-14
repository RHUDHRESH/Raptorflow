import { Router, Request, Response } from 'express';
import { db } from '../lib/db';
import { supabase } from '../lib/supabase';
import type { CreateICPInput, BarrierType } from '../types';

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
 * GET /api/icps
 * List all ICPs for the current user
 */
router.get('/', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const includeArchived = req.query.includeArchived === 'true';
    
    const { data, error } = await db.icps.list(userId, { includeArchived });
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/icps/:id
 * Get a specific ICP by ID
 */
router.get('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { data, error } = await db.icps.getById(id, userId);
    
    if (error) {
      return res.status(404).json({ error: 'ICP not found' });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/icps
 * Create a new ICP
 */
router.post('/', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const icpData: CreateICPInput = req.body;
    
    if (!icpData.label) {
      return res.status(400).json({ error: 'Label is required' });
    }
    
    const { data, error } = await db.icps.create(userId, icpData);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.status(201).json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/icps/bulk
 * Create multiple ICPs at once (from generation)
 */
router.post('/bulk', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { icps } = req.body;
    
    if (!Array.isArray(icps) || icps.length === 0) {
      return res.status(400).json({ error: 'ICPs array is required' });
    }
    
    const { data, error } = await db.icps.createMany(userId, icps);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.status(201).json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * PATCH /api/icps/:id
 * Update an ICP
 */
router.patch('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const updates: Partial<CreateICPInput> = req.body;
    
    const { data, error } = await db.icps.update(id, userId, updates);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * PATCH /api/icps/:id/selection
 * Toggle ICP selection
 */
router.patch('/:id/selection', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const { is_selected } = req.body;
    
    if (typeof is_selected !== 'boolean') {
      return res.status(400).json({ error: 'is_selected must be a boolean' });
    }
    
    const { data, error } = await db.icps.updateSelection(id, userId, is_selected);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ success: true });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/icps/reorder
 * Update priority order of ICPs
 */
router.post('/reorder', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { priorities } = req.body;
    
    if (!Array.isArray(priorities)) {
      return res.status(400).json({ error: 'priorities must be an array' });
    }
    
    await db.icps.updatePriority(userId, priorities);
    
    res.json({ success: true });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * DELETE /api/icps/:id
 * Delete an ICP
 */
router.delete('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { error } = await db.icps.delete(id, userId);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ success: true });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/icps/:id/archive
 * Archive an ICP (soft delete)
 */
router.post('/:id/archive', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { error } = await db.icps.archive(id, userId);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ success: true });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/icps/:id/barriers
 * Get barriers for an ICP
 */
router.get('/:id/barriers', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { data, error } = await db.barriers.getByICP(id, userId);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

export default router;

