import { Request, Response, NextFunction } from 'express';
import { supabaseAdmin } from '../lib/supabase';

export interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    email?: string;
    role?: string;
    app_metadata?: any;
    user_metadata?: any;
  };
}

export const requireAuth = async (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  const authHeader = req.headers.authorization;

  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or invalid authorization header' });
  }

  const token = authHeader.split(' ')[1];

  try {
    // Verify the token using Supabase
    const { data: { user }, error } = await supabaseAdmin.auth.getUser(token);

    if (error || !user) {
      console.error('Token verification failed:', error?.message);
      return res.status(401).json({ error: 'Invalid or expired token' });
    }

    // Attach user to request
    req.user = {
      id: user.id,
      email: user.email,
      role: user.role,
      app_metadata: user.app_metadata,
      user_metadata: user.user_metadata,
    };

    next();
  } catch (err) {
    console.error('Auth middleware error:', err);
    return res.status(500).json({ error: 'Internal server error during authentication' });
  }
};
