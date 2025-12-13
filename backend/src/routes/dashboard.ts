import { Router, Request, Response } from 'express';
import { db } from '../lib/db';
import { supabase } from '../lib/supabase';
import type { RAGStatus } from '../types';

const router = Router();

// Middleware to verify JWT token (reuse from metrics)
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

// Dashboard overview with aggregated KPIs
interface DashboardOverview {
  pipeline: number;
  win_rate: number;
  customer_acquisition_cost: number;
  net_revenue_retention: number;
  rag_status: RAGStatus;
}

interface CampaignSummary {
  id: string;
  name: string;
  protocol: string;
  status: string;
  progress: number;
}

interface TaskStatus {
  completed: number;
  pending: number;
  total: number;
}

interface DashboardResponse {
  overview: DashboardOverview;
  active_campaigns: CampaignSummary[];
  rag_summary: {
    green: number;
    amber: number;
    red: number;
    total: number;
  };
  tasks: TaskStatus;
}

/**
 * GET /api/dashboard
 * Get comprehensive dashboard data for the frontend
 */
router.get('/', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;

    // Get latest metrics for dashboard overview
    const { data: metrics, error: metricsError } = await db.metrics.list(userId, {
      scope_type: 'business'
    });

    if (metricsError) {
      console.error('Error fetching metrics:', metricsError);
      return res.status(500).json({ error: 'Failed to fetch dashboard metrics' });
    }

    // Calculate overview metrics (simplified for demo)
    const pipeline = 2450000; // Example value
    const win_rate = 28;
    const customer_acquisition_cost = 4200;
    const net_revenue_retention = 112;

    // Get active campaigns
    const { data: campaigns, error: campaignsError } = await db.campaigns.list(userId, {
      status: 'active'
    });

    if (campaignsError) {
      console.error('Error fetching campaigns:', campaignsError);
      return res.status(500).json({ error: 'Failed to fetch campaigns' });
    }

    const activeCampaigns: CampaignSummary[] = (campaigns || []).map(campaign => ({
      id: campaign.id,
      name: campaign.name,
      protocol: campaign.protocols?.[0] || 'Unknown',
      status: campaign.status,
      progress: Math.floor(Math.random() * 100) // Example progress
    }));

    // Get RAG status summary from latest metrics
    const ragSummary = {
      green: metrics?.filter(m => m.rag_status === 'green').length || 0,
      amber: metrics?.filter(m => m.rag_status === 'amber').length || 0,
      red: metrics?.filter(m => m.rag_status === 'red').length || 0,
      total: metrics?.length || 0
    };

    // Calculate task status (simplified example)
    const tasks: TaskStatus = {
      completed: 12,
      pending: 8,
      total: 20
    };

    const response: DashboardResponse = {
      overview: {
        pipeline,
        win_rate,
        customer_acquisition_cost,
        net_revenue_retention,
        rag_status: ragSummary.green > ragSummary.red ? 'green' : ragSummary.amber > 0 ? 'amber' : 'red'
      },
      active_campaigns: activeCampaigns,
      rag_summary: ragSummary,
      tasks
    };

    res.json(response);
  } catch (err: any) {
    console.error('Dashboard error:', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/dashboard/metrics/:scopeType/:scopeId
 * Get metrics for a specific scope (campaign, move, etc.)
 */
router.get('/metrics/:scopeType/:scopeId', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { scopeType, scopeId } = req.params;

    const { data, error } = await db.metrics.getLatest(userId, scopeType, scopeId);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/dashboard/campaigns/active
 * Get only active campaigns for dashboard
 */
router.get('/campaigns/active', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;

    const { data, error } = await db.campaigns.list(userId, {
      status: 'active'
    });

    if (error) {
      return res.status(500).json({ error: error.message });
    }

    res.json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

export default router;
