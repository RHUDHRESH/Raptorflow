import type { Request, Response } from 'express';
import { supabase } from './supabase';

export async function requireSupabaseUser(req: Request, res: Response, next: any) {
  const authHeader = req.headers.authorization;

  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or invalid authorization header' });
  }

  const token = authHeader.slice('Bearer '.length).trim();
  if (!token) {
    return res.status(401).json({ error: 'Missing bearer token' });
  }

  try {
    const { data, error } = await supabase.auth.getUser(token);
    if (error || !data?.user) {
      return res.status(401).json({ error: 'Invalid token' });
    }

    (req as any).user = data.user;
    (req as any).accessToken = token;
    return next();
  } catch {
    return res.status(401).json({ error: 'Token verification failed' });
  }
}
