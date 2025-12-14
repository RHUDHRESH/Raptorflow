import { Router, Request, Response } from 'express';
import { db } from '../lib/db';
import { supabase } from '../lib/supabase';
import type { BarrierType, ProtocolType } from '../types';

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
 * GET /api/protocols
 * List all protocols
 */
router.get('/', verifyToken, async (req: Request, res: Response) => {
  try {
    const { data, error } = await db.protocols.list();
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/protocols/:code
 * Get a specific protocol by code
 */
router.get('/:code', verifyToken, async (req: Request, res: Response) => {
  try {
    const { code } = req.params;
    
    const { data, error } = await db.protocols.getByCode(code as ProtocolType);
    
    if (error) {
      return res.status(404).json({ error: 'Protocol not found' });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/protocols/barrier/:barrier
 * Get protocols that target a specific barrier
 */
router.get('/barrier/:barrier', verifyToken, async (req: Request, res: Response) => {
  try {
    const { barrier } = req.params;
    
    const validBarriers: BarrierType[] = ['OBSCURITY', 'RISK', 'INERTIA', 'FRICTION', 'CAPACITY', 'ATROPHY'];
    if (!validBarriers.includes(barrier as BarrierType)) {
      return res.status(400).json({ error: 'Invalid barrier type' });
    }
    
    const { data, error } = await db.protocols.getByBarrier(barrier as BarrierType);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/protocols/:code/templates
 * Get move templates for a specific protocol
 */
router.get('/:code/templates', verifyToken, async (req: Request, res: Response) => {
  try {
    const { code } = req.params;
    
    const { data, error } = await db.moveTemplates.getByProtocol(code as ProtocolType);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/protocols/recommend
 * Get protocol recommendations based on context
 */
router.post('/recommend', verifyToken, async (req: Request, res: Response) => {
  try {
    const { barriers, goal, demand_source } = req.body;
    
    // Get all protocols
    const { data: protocols, error } = await db.protocols.list();
    
    if (error || !protocols) {
      return res.status(500).json({ error: error?.message || 'Failed to fetch protocols' });
    }
    
    // Score protocols based on context
    const scoredProtocols = protocols.map(protocol => {
      let score = 0;
      
      // Match by barrier (highest weight)
      if (barriers?.includes(protocol.targets_barrier)) {
        score += 50;
      }
      
      // Boost for demand creation (Authority Blitz, Trust Anchor)
      if (demand_source === 'creation' && ['A_AUTHORITY_BLITZ', 'B_TRUST_ANCHOR'].includes(protocol.code)) {
        score += 20;
      }
      
      // Boost for demand capture (Trust Anchor, Cost of Inaction)
      if (demand_source === 'capture' && ['B_TRUST_ANCHOR', 'C_COST_OF_INACTION'].includes(protocol.code)) {
        score += 20;
      }
      
      // Boost for expansion (Enterprise Wedge, Churn Intercept)
      if (demand_source === 'expansion' && ['E_ENTERPRISE_WEDGE', 'F_CHURN_INTERCEPT'].includes(protocol.code)) {
        score += 30;
      }
      
      // Boost for velocity goal
      if (goal === 'velocity' && ['A_AUTHORITY_BLITZ', 'D_HABIT_HARDCODE'].includes(protocol.code)) {
        score += 15;
      }
      
      // Boost for efficiency goal
      if (goal === 'efficiency' && ['B_TRUST_ANCHOR', 'C_COST_OF_INACTION'].includes(protocol.code)) {
        score += 15;
      }
      
      // Boost for penetration goal
      if (goal === 'penetration' && ['E_ENTERPRISE_WEDGE', 'F_CHURN_INTERCEPT'].includes(protocol.code)) {
        score += 15;
      }
      
      return { ...protocol, recommendation_score: score };
    });
    
    // Sort by score and filter out zero-score
    const recommended = scoredProtocols
      .filter(p => p.recommendation_score > 0)
      .sort((a, b) => b.recommendation_score - a.recommendation_score);
    
    res.json({ data: recommended });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

export default router;

