import { Router, Request, Response } from 'express';
import { db } from '../lib/db';
import { supabase } from '../lib/supabase';
import type { CreateMoveInput, MoveStatus, MoveTask } from '../types';
import { v4 as uuidv4 } from 'uuid';

const router = Router();

function normalize90DayWindow(input: { planned_start?: any; planned_end?: any }) {
  const startRaw = input.planned_start;
  const endRaw = input.planned_end;

  const start = startRaw ? new Date(String(startRaw)) : null;
  const end = endRaw ? new Date(String(endRaw)) : null;

  const startValid = start && !Number.isNaN(start.getTime()) ? start : null;
  const endValid = end && !Number.isNaN(end.getTime()) ? end : null;

  const dayMs = 24 * 60 * 60 * 1000;
  if (startValid) {
    const computedEnd = new Date(startValid.getTime() + 90 * dayMs);
    return {
      planned_start: startValid.toISOString().slice(0, 10),
      planned_end: computedEnd.toISOString().slice(0, 10),
    };
  }

  if (endValid) {
    const computedStart = new Date(endValid.getTime() - 90 * dayMs);
    return {
      planned_start: computedStart.toISOString().slice(0, 10),
      planned_end: endValid.toISOString().slice(0, 10),
    };
  }

  const today = new Date();
  const computedEnd = new Date(today.getTime() + 90 * dayMs);
  return {
    planned_start: today.toISOString().slice(0, 10),
    planned_end: computedEnd.toISOString().slice(0, 10),
  };
}

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
 * GET /api/moves
 * List all moves for the current user
 */
router.get('/', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { campaign_id, spike_id, status } = req.query;
    
    const { data, error } = await db.moves.list(userId, {
      campaign_id: campaign_id as string,
      spike_id: spike_id as string,
      status: status as MoveStatus
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
 * GET /api/moves/templates
 * List all move templates
 */
router.get('/templates', verifyToken, async (req: Request, res: Response) => {
  try {
    const { data, error } = await db.moveTemplates.list();
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/moves/templates/:slug
 * Get a specific move template
 */
router.get('/templates/:slug', verifyToken, async (req: Request, res: Response) => {
  try {
    const { slug } = req.params;
    
    const { data, error } = await db.moveTemplates.getBySlug(slug);
    
    if (error) {
      return res.status(404).json({ error: 'Template not found' });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/moves/:id
 * Get a specific move with related data
 */
router.get('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { data, error } = await db.moves.getById(id, userId);
    
    if (error) {
      return res.status(404).json({ error: 'Move not found' });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/moves
 * Create a new move
 */
router.post('/', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const moveData: CreateMoveInput = req.body;
    
    if (!moveData.name) {
      return res.status(400).json({ error: 'Name is required' });
    }
    
    // If template_id is provided, load template and merge data
    if (moveData.template_id) {
      const { data: template } = await db.moveTemplates.getBySlug(moveData.template_id);
      
      if (template) {
        // Pre-populate tasks from template
        const tasks: MoveTask[] = template.task_template.map((t: any) => ({
          id: uuidv4(),
          task: t.task,
          status: 'pending' as const,
          due_date: undefined,
          completed_at: undefined
        }));
        
        moveData.channels = moveData.channels || template.channels;
        (moveData as any).tasks = tasks;
        (moveData as any).impact_score = template.base_impact_score;
        (moveData as any).effort_score = template.base_effort_score;
        moveData.protocol = moveData.protocol || template.protocol_type;
      }
    }

    const window = normalize90DayWindow({
      planned_start: (moveData as any).planned_start,
      planned_end: (moveData as any).planned_end,
    });

    (moveData as any).planned_start = window.planned_start;
    (moveData as any).planned_end = window.planned_end;
    
    const { data, error } = await db.moves.create(userId, moveData);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.status(201).json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/moves/from-template
 * Create a move from a template with customizations
 */
router.post('/from-template', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { template_slug, campaign_id, spike_id, icp_id, customizations } = req.body;
    
    if (!template_slug) {
      return res.status(400).json({ error: 'template_slug is required' });
    }
    
    // Get template
    const { data: template, error: templateError } = await db.moveTemplates.getBySlug(template_slug);
    
    if (templateError || !template) {
      return res.status(404).json({ error: 'Template not found' });
    }
    
    // Generate tasks from template
    const tasks: MoveTask[] = template.task_template.map((t: any) => ({
      id: uuidv4(),
      task: t.task,
      status: 'pending' as const,
      due_date: undefined,
      completed_at: undefined
    }));
    
    // Calculate EV score
    const ev_score = (template.base_impact_score * 0.5) / template.base_effort_score;
    
    const moveData = {
      name: customizations?.name || template.name,
      description: customizations?.description || template.description,
      template_id: template.id,
      campaign_id,
      spike_id,
      icp_id,
      protocol: template.protocol_type,
      channels: customizations?.channels || template.channels,
      tasks,
      impact_score: template.base_impact_score,
      effort_score: template.base_effort_score,
      ev_score,
      kpis: template.success_metrics.reduce((acc: any, m: any) => {
        acc[m.metric] = { target: m.target, unit: m.unit };
        return acc;
      }, {}),
      ...normalize90DayWindow({
        planned_start: customizations?.planned_start,
        planned_end: customizations?.planned_end,
      })
    };
    
    const { data, error } = await db.moves.create(userId, moveData as any);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.status(201).json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * PATCH /api/moves/:id
 * Update a move
 */
router.patch('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const updates = req.body;

    if (Object.prototype.hasOwnProperty.call(updates || {}, 'planned_start') || Object.prototype.hasOwnProperty.call(updates || {}, 'planned_end')) {
      const window = normalize90DayWindow({
        planned_start: (updates as any).planned_start,
        planned_end: (updates as any).planned_end,
      });
      (updates as any).planned_start = window.planned_start;
      (updates as any).planned_end = window.planned_end;
    }
    
    const { data, error } = await db.moves.update(id, userId, updates);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * PATCH /api/moves/:id/status
 * Update move status
 */
router.patch('/:id/status', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const { status } = req.body;
    
    const validStatuses: MoveStatus[] = ['planned', 'generating_assets', 'ready', 'running', 'paused', 'completed', 'failed'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({ error: 'Invalid status' });
    }
    
    const { data, error } = await db.moves.updateStatus(id, userId, status);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * PATCH /api/moves/:id/tasks
 * Update move tasks
 */
router.patch('/:id/tasks', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    const { tasks } = req.body;
    
    if (!Array.isArray(tasks)) {
      return res.status(400).json({ error: 'tasks must be an array' });
    }
    
    const { data, error } = await db.moves.updateTasks(id, userId, tasks);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/moves/:id/tasks/:taskId/complete
 * Mark a specific task as complete
 */
router.post('/:id/tasks/:taskId/complete', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id, taskId } = req.params;
    
    // Get current move
    const { data: move, error: fetchError } = await db.moves.getById(id, userId);
    
    if (fetchError || !move) {
      return res.status(404).json({ error: 'Move not found' });
    }
    
    // Update the specific task
    const tasks = move.tasks.map((t: MoveTask) => 
      t.id === taskId 
        ? { ...t, status: 'completed' as const, completed_at: new Date().toISOString() }
        : t
    );
    
    const { data, error } = await db.moves.updateTasks(id, userId, tasks);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * DELETE /api/moves/:id
 * Delete a move
 */
router.delete('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { error } = await db.moves.delete(id, userId);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ success: true });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/moves/:id/assets
 * Get all assets for a move
 */
router.get('/:id/assets', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { data, error } = await db.assets.list(userId, { move_id: id });
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

export default router;

