import { Router, Request, Response } from 'express';
import { db } from '../lib/db';
import { supabase } from '../lib/supabase';
import type { CreateMetricInput, RAGStatus } from '../types';

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

// Helper: Calculate RAG status
function calculateRAGStatus(value: number | undefined, target: number | undefined, thresholds: { green_above?: number; red_below?: number }): RAGStatus {
  if (value === undefined || target === undefined) {
    return 'unknown';
  }
  
  const percentOfTarget = (value / target) * 100;
  
  // Default thresholds: green > 90%, red < 80%
  const greenThreshold = thresholds.green_above ?? 90;
  const redThreshold = thresholds.red_below ?? 80;
  
  if (percentOfTarget >= greenThreshold) {
    return 'green';
  } else if (percentOfTarget < redThreshold) {
    return 'red';
  } else {
    return 'amber';
  }
}

/**
 * GET /api/metrics
 * List metrics with optional filters
 */
router.get('/', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { scope_type, scope_id, metric_name } = req.query;
    
    const { data, error } = await db.metrics.list(userId, {
      scope_type: scope_type as string,
      scope_id: scope_id as string,
      metric_name: metric_name as string
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
 * GET /api/metrics/latest/:scopeType/:scopeId
 * Get latest metrics for a specific scope
 */
router.get('/latest/:scopeType/:scopeId', verifyToken, async (req: Request, res: Response) => {
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
 * POST /api/metrics
 * Record a new metric value
 */
router.post('/', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const metricData: CreateMetricInput = req.body;
    
    if (!metricData.scope_type) {
      return res.status(400).json({ error: 'scope_type is required' });
    }
    if (!metricData.metric_name) {
      return res.status(400).json({ error: 'metric_name is required' });
    }
    
    // Calculate RAG status if value and target are provided
    let rag_status: RAGStatus = 'unknown';
    if (metricData.value !== undefined && metricData.target_value !== undefined) {
      rag_status = calculateRAGStatus(
        metricData.value,
        metricData.target_value,
        metricData.rag_thresholds || {}
      );
    }
    
    const { data, error } = await db.metrics.create(userId, {
      ...metricData,
      source: metricData.source || 'manual'
    });
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    // Update the RAG status
    if (data) {
      await supabase
        .from('metrics')
        .update({ rag_status })
        .eq('id', data.id);
      
      data.rag_status = rag_status;
    }
    
    res.status(201).json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/metrics/bulk
 * Record multiple metrics at once
 */
router.post('/bulk', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { metrics } = req.body;
    
    if (!Array.isArray(metrics) || metrics.length === 0) {
      return res.status(400).json({ error: 'metrics array is required' });
    }
    
    // Calculate RAG status for each metric
    const metricsWithRAG = metrics.map((m: CreateMetricInput) => {
      const rag_status = m.value !== undefined && m.target_value !== undefined
        ? calculateRAGStatus(m.value, m.target_value, m.rag_thresholds || {})
        : 'unknown';
      
      return { ...m, rag_status, source: m.source || 'manual' };
    });
    
    const { data, error } = await db.metrics.createMany(userId, metricsWithRAG);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.status(201).json({ data });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * DELETE /api/metrics/:id
 * Delete a metric
 */
router.delete('/:id', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { id } = req.params;
    
    const { error } = await db.metrics.delete(id, userId);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.json({ success: true });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /api/metrics/summary/:scopeType/:scopeId
 * Get a summary of metrics with RAG status breakdown
 */
router.get('/summary/:scopeType/:scopeId', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { scopeType, scopeId } = req.params;
    
    const { data, error } = await db.metrics.getLatest(userId, scopeType, scopeId);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    // Calculate summary
    const summary = {
      total: data?.length || 0,
      green: data?.filter(m => m.rag_status === 'green').length || 0,
      amber: data?.filter(m => m.rag_status === 'amber').length || 0,
      red: data?.filter(m => m.rag_status === 'red').length || 0,
      unknown: data?.filter(m => m.rag_status === 'unknown').length || 0,
      overall_status: 'unknown' as RAGStatus,
      metrics: data || []
    };
    
    // Calculate overall status
    if (summary.red > 0) {
      summary.overall_status = 'red';
    } else if (summary.amber > 0) {
      summary.overall_status = 'amber';
    } else if (summary.green > 0) {
      summary.overall_status = 'green';
    }
    
    res.json({ data: summary });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * POST /api/metrics/recalculate-rag
 * Recalculate RAG status for all metrics in a scope
 */
router.post('/recalculate-rag', verifyToken, async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user.id;
    const { scope_type, scope_id } = req.body;
    
    const { data: metrics, error } = await db.metrics.list(userId, { scope_type, scope_id });
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    // Recalculate RAG for each metric
    const updates = (metrics || []).map(async (metric) => {
      const newRAG = calculateRAGStatus(
        metric.value,
        metric.target_value,
        metric.rag_thresholds || {}
      );
      
      if (newRAG !== metric.rag_status) {
        await supabase
          .from('metrics')
          .update({ rag_status: newRAG })
          .eq('id', metric.id)
          .eq('user_id', userId);
      }
      
      return { id: metric.id, rag_status: newRAG };
    });
    
    const results = await Promise.all(updates);
    
    res.json({ data: results });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

export default router;

