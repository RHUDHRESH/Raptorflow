import { Router, Request, Response } from 'express';
import { db } from '../lib/db';
import { supabase } from '../lib/supabase';
import type { CreateCampaignInput, CampaignStatus, BarrierType, ProtocolType } from '../types';
import { evaluateCampaignPreflight } from '../services/campaignPreflight';

const router = Router();

async function getCurrentOrgId(userId: string): Promise<string> {
  const { data: profile, error } = await supabase
    .from('profiles')
    .select('current_org_id')
    .eq('id', userId)
    .single();

  if (error) throw new Error(error.message);
  const orgId = (profile as any)?.current_org_id;
  if (!orgId) throw new Error('No workspace selected (profiles.current_org_id missing).');
  return String(orgId);
}

async function logCampaignEvent(params: {
  organizationId: string;
  userId: string;
  campaignId: string;
  eventName: string;
  properties?: Record<string, any>;
  moveId?: string | null;
}) {
  await supabase
    .from('campaign_events')
    .insert({
      organization_id: params.organizationId,
      user_id: params.userId,
      campaign_id: params.campaignId,
      move_id: params.moveId || null,
      event_name: params.eventName,
      properties: params.properties || {},
    });
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
    const orgId = await getCurrentOrgId(userId);
    const campaignData: Partial<CreateCampaignInput> & Record<string, any> = req.body || {};

    if (!campaignData.name) {
      return res.status(400).json({ error: 'Name is required' });
    }

    const insert = {
      organization_id: orgId,
      created_by: userId,
      name: campaignData.name,
      description: campaignData.description || null,
      status: 'draft',
      objective_text: campaignData.objective_text || null,
      primary_kpi_type: campaignData.primary_kpi_type || null,
      primary_kpi_baseline: campaignData.primary_kpi_baseline ?? null,
      primary_kpi_target: campaignData.primary_kpi_target ?? null,
      primary_kpi_window_start: campaignData.primary_kpi_window_start || campaignData.start_date || null,
      primary_kpi_window_end: campaignData.primary_kpi_window_end || campaignData.end_date || null,
      budget_amount: campaignData.budget_amount ?? null,
      strategy_version_id: campaignData.strategy_version_id ?? null,
      primary_cohort_id: campaignData.primary_cohort_id ?? null,
      secondary_cohort_ids: campaignData.secondary_cohort_ids ?? [],
      stage_model: campaignData.stage_model || null,
      stages_json: campaignData.stages_json ?? [],
      channels_json: campaignData.channels_json ?? [],
      measurement_json: campaignData.measurement_json ?? {},
      execution_capacity_json: campaignData.execution_capacity_json ?? {},
      execution_override: Boolean(campaignData.execution_override),
      config: campaignData.config ?? {},
    };

    const { data, error } = await supabase
      .from('campaigns')
      .insert(insert)
      .select('*')
      .single();

    if (error) {
      return res.status(500).json({ error: error.message });
    }

    await logCampaignEvent({
      organizationId: orgId,
      userId,
      campaignId: (data as any).id,
      eventName: 'campaign.created',
      properties: { status: 'draft' },
    });

    res.status(201).json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/campaigns/:id/slots
 * Seed empty move slots (does NOT create moves)
 */
router.post('/:id/slots', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const orgId = await getCurrentOrgId(userId);
    const { id } = req.params;
    const { slots } = req.body || {};

    if (!Array.isArray(slots) || slots.length === 0) {
      return res.status(400).json({ error: 'slots must be a non-empty array' });
    }

    const rows = slots.map((s: any) => ({
      organization_id: orgId,
      created_by: userId,
      campaign_id: id,
      slot_index: Number(s.slot_index || 0),
      stage_key: s.stage_key || null,
      outcome_text: s.outcome_text || null,
      recommended_move_template_id: s.recommended_move_template_id || null,
      created_move_id: s.created_move_id || null,
    }));

    const { data, error } = await supabase
      .from('campaign_move_slots')
      .insert(rows)
      .select('*');

    if (error) return res.status(500).json({ error: error.message });

    await logCampaignEvent({
      organizationId: orgId,
      userId,
      campaignId: id,
      eventName: 'campaign.slots_seeded',
      properties: { count: rows.length },
    });

    res.status(201).json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/campaigns/:id/link-move
 * Link an existing move to a campaign
 */
router.post('/:id/link-move', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const orgId = await getCurrentOrgId(userId);
    const { id } = req.params;
    const { move_id, slot_index, stage_key, week_start, week_end } = req.body || {};

    if (!move_id) return res.status(400).json({ error: 'move_id is required' });

    const { data: move, error: moveErr } = await supabase
      .from('moves')
      .select('*')
      .eq('id', move_id)
      .eq('organization_id', orgId)
      .single();

    if (moveErr || !move) return res.status(404).json({ error: 'Move not found' });

    const derivedStatus = (move as any).status === 'ready'
      ? 'ready'
      : (move as any).status === 'running'
        ? 'running'
        : (move as any).status === 'completed'
          ? 'done'
          : 'planned';

    const { data: link, error: linkErr } = await supabase
      .from('campaign_move_links')
      .insert({
        organization_id: orgId,
        created_by: userId,
        campaign_id: id,
        move_id,
        slot_index: Number(slot_index || 0),
        stage_key: stage_key || null,
        week_start: week_start || null,
        week_end: week_end || null,
        status: derivedStatus,
      })
      .select('*')
      .single();

    if (linkErr) return res.status(500).json({ error: linkErr.message });

    await supabase
      .from('moves')
      .update({ campaign_id: id })
      .eq('id', move_id)
      .eq('organization_id', orgId);

    await logCampaignEvent({
      organizationId: orgId,
      userId,
      campaignId: id,
      moveId: move_id,
      eventName: 'campaign.move_linked',
      properties: { slot_index: Number(slot_index || 0), stage_key: stage_key || null },
    });

    res.status(201).json({ data: link });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * DELETE /api/campaigns/:id/unlink-move?move_id=
 */
router.delete('/:id/unlink-move', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const orgId = await getCurrentOrgId(userId);
    const { id } = req.params;
    const moveId = (req.query.move_id as string) || '';
    if (!moveId) return res.status(400).json({ error: 'move_id is required' });

    const { error } = await supabase
      .from('campaign_move_links')
      .delete()
      .eq('campaign_id', id)
      .eq('move_id', moveId)
      .eq('organization_id', orgId);

    if (error) return res.status(500).json({ error: error.message });

    await supabase
      .from('moves')
      .update({ campaign_id: null })
      .eq('id', moveId)
      .eq('organization_id', orgId);

    await logCampaignEvent({
      organizationId: orgId,
      userId,
      campaignId: id,
      moveId,
      eventName: 'campaign.move_unlinked',
    });

    res.json({ success: true });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/campaigns/:id/preflight
 * Returns gating + warnings + health_score breakdown
 */
router.post('/:id/preflight', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const orgId = await getCurrentOrgId(userId);
    const { id } = req.params;

    const { data: campaign, error: cErr } = await supabase
      .from('campaigns')
      .select('*')
      .eq('id', id)
      .eq('organization_id', orgId)
      .is('deleted_at', null)
      .single();

    if (cErr || !campaign) return res.status(404).json({ error: 'Campaign not found' });

    const { data: links } = await supabase
      .from('campaign_move_links')
      .select('move_id')
      .eq('campaign_id', id)
      .eq('organization_id', orgId);

    const moveIds = (links || []).map((l: any) => l.move_id).filter(Boolean);
    const { data: linkedMoves } = moveIds.length
      ? await supabase
          .from('moves')
          .select('*')
          .in('id', moveIds)
          .eq('organization_id', orgId)
      : { data: [] as any[] };

    const { count: slotCount } = await supabase
      .from('campaign_move_slots')
      .select('id', { count: 'exact', head: true })
      .eq('campaign_id', id)
      .eq('organization_id', orgId);

    const result = evaluateCampaignPreflight({
      campaign,
      linkedMoves: linkedMoves || [],
      slotCount: Number(slotCount || 0),
    });

    await supabase
      .from('campaigns')
      .update({
        health_score: result.health_score,
        health_details: result.breakdown,
        last_preflight_at: new Date().toISOString(),
      })
      .eq('id', id)
      .eq('organization_id', orgId);

    await logCampaignEvent({
      organizationId: orgId,
      userId,
      campaignId: id,
      eventName: 'campaign.preflight',
      properties: {
        ok: result.ok,
        label: result.label,
        health_score: result.health_score,
        blockers: result.blockers,
        warnings: result.warnings,
      },
    });

    res.json({ data: result });
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

    const orgId = await getCurrentOrgId(userId);

    const { data: campaign, error: cErr } = await supabase
      .from('campaigns')
      .select('*')
      .eq('id', id)
      .eq('organization_id', orgId)
      .is('deleted_at', null)
      .single();

    if (cErr || !campaign) return res.status(404).json({ error: 'Campaign not found' });

    if (!['planned', 'draft'].includes((campaign as any).status)) {
      return res.status(400).json({ error: 'Campaign must be in planned or draft status to activate' });
    }

    const { data: links } = await supabase
      .from('campaign_move_links')
      .select('move_id')
      .eq('campaign_id', id)
      .eq('organization_id', orgId);

    const moveIds = (links || []).map((l: any) => l.move_id).filter(Boolean);
    const { data: linkedMoves } = moveIds.length
      ? await supabase
          .from('moves')
          .select('*')
          .in('id', moveIds)
          .eq('organization_id', orgId)
      : { data: [] as any[] };

    const { count: slotCount } = await supabase
      .from('campaign_move_slots')
      .select('id', { count: 'exact', head: true })
      .eq('campaign_id', id)
      .eq('organization_id', orgId);

    const preflight = evaluateCampaignPreflight({
      campaign,
      linkedMoves: linkedMoves || [],
      slotCount: Number(slotCount || 0),
    });

    await supabase
      .from('campaigns')
      .update({
        health_score: preflight.health_score,
        health_details: preflight.breakdown,
        last_preflight_at: new Date().toISOString(),
      })
      .eq('id', id)
      .eq('organization_id', orgId);

    if (!preflight.ok) {
      return res.status(400).json({
        error: 'Preflight failed',
        data: preflight,
      });
    }

    const { data, error } = await supabase
      .from('campaigns')
      .update({ status: 'active' })
      .eq('id', id)
      .eq('organization_id', orgId)
      .select('*')
      .single();

    if (error) return res.status(500).json({ error: error.message });

    await logCampaignEvent({
      organizationId: orgId,
      userId,
      campaignId: id,
      eventName: 'campaign.activated',
      properties: { health_score: preflight.health_score },
    });

    res.json({ data });
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
    
    const validStatuses: CampaignStatus[] = ['draft', 'planned', 'active', 'paused', 'completed', 'cancelled', 'archived'];
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

