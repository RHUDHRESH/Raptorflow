import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { ValidationError, AuthenticationError, createDatabaseError } from '@/lib/security/error-handler';
import { validateUuid, sanitizeInput } from '@/lib/security/input-validation';

export async function POST(request: Request) {
  try {
    const { action, sessionId, userId } = await request.json();
    
    // Validate input
    if (!action || typeof action !== 'string') {
      throw new ValidationError('Action is required');
    }
    
    const sanitizedAction = sanitizeInput(action);
    
    // Initialize Supabase client
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    );
    
    switch (sanitizedAction) {
      case 'list':
        return await listSessions(supabase, userId);
      case 'revoke':
        return await revokeSession(supabase, sessionId, userId);
      case 'revoke-all':
        return await revokeAllSessions(supabase, userId);
      case 'extend':
        return await extendSession(supabase, sessionId, userId);
      default:
        throw new ValidationError('Invalid action');
    }
    
  } catch (error) {
    console.error('Session management error:', error);
    
    if (error instanceof ValidationError) {
      return NextResponse.json(
        { error: error.message },
        { status: 400 }
      );
    }
    
    if (error instanceof AuthenticationError) {
      return NextResponse.json(
        { error: error.message },
        { status: 401 }
      );
    }
    
    return NextResponse.json(
      { error: 'Failed to manage sessions' },
      { status: 500 }
    );
  }
}

async function listSessions(supabase: any, userId?: string) {
  if (!userId) {
    throw new ValidationError('User ID is required');
  }
  
  const sanitizedUserId = sanitizeInput(userId);
  
  if (!validateUuid(sanitizedUserId)) {
    throw new ValidationError('Invalid user ID format');
  }
  
  // Get user sessions
  const { data: sessions, error: sessionsError } = await supabase
    .from('user_sessions')
    .select('*')
    .eq('user_id', sanitizedUserId)
    .eq('active', true)
    .order('created_at', { ascending: false });
  
  if (sessionsError) {
    throw createDatabaseError('get user sessions', sessionsError);
  }
  
  // Clean up expired sessions
  const now = new Date();
  const activeSessions = sessions.filter((session: any) => 
    new Date(session.expires_at) > now
  );
  
  // Update expired sessions in database
  const expiredSessions = sessions.filter((session: any) => 
    new Date(session.expires_at) <= now
  );
  
  if (expiredSessions.length > 0) {
    const expiredIds = expiredSessions.map((session: any) => session.id);
    await supabase
      .from('user_sessions')
      .update({ active: false })
      .in('id', expiredIds);
  }
  
  return NextResponse.json({
    sessions: activeSessions.map((session: any) => ({
      id: session.id,
      device: session.device_type,
      browser: session.browser,
      location: session.location,
      ipAddress: session.ip_address,
      createdAt: session.created_at,
      expiresAt: session.expires_at,
      lastActivity: session.last_activity
    }))
  });
}

async function revokeSession(supabase: any, sessionId?: string, userId?: string) {
  if (!sessionId) {
    throw new ValidationError('Session ID is required');
  }
  
  if (!userId) {
    throw new ValidationError('User ID is required');
  }
  
  const sanitizedSessionId = sanitizeInput(sessionId);
  const sanitizedUserId = sanitizeInput(userId);
  
  if (!validateUuid(sanitizedSessionId)) {
    throw new ValidationError('Invalid session ID format');
  }
  
  if (!validateUuid(sanitizedUserId)) {
    throw new ValidationError('Invalid user ID format');
  }
  
  // Verify session belongs to user
  const { data: session, error: sessionError } = await supabase
    .from('user_sessions')
    .select('*')
    .eq('id', sanitizedSessionId)
    .eq('user_id', sanitizedUserId)
    .single();
  
  if (sessionError || !session) {
    throw new AuthenticationError('Session not found');
  }
  
  // Revoke session
  const { error: revokeError } = await supabase
    .from('user_sessions')
    .update({ active: false })
    .eq('id', sanitizedSessionId);
  
  if (revokeError) {
    throw createDatabaseError('revoke session', revokeError);
  }
  
  return NextResponse.json({
    message: 'Session revoked successfully'
  });
}

async function revokeAllSessions(supabase: any, userId?: string) {
  if (!userId) {
    throw new ValidationError('User ID is required');
  }
  
  const sanitizedUserId = sanitizeInput(userId);
  
  if (!validateUuid(sanitizedUserId)) {
    throw new ValidationError('Invalid user ID format');
  }
  
  // Revoke all sessions for user
  const { error: revokeError } = await supabase
    .from('user_sessions')
    .update({ active: false })
    .eq('user_id', sanitizedUserId);
  
  if (revokeError) {
    throw createDatabaseError('revoke all sessions', revokeError);
  }
  
  return NextResponse.json({
    message: 'All sessions revoked successfully'
  });
}

async function extendSession(supabase: any, sessionId?: string, userId?: string) {
  if (!sessionId) {
    throw new ValidationError('Session ID is required');
  }
  
  if (!userId) {
    throw new ValidationError('User ID is required');
  }
  
  const sanitizedSessionId = sanitizeInput(sessionId);
  const sanitizedUserId = sanitizeInput(userId);
  
  if (!validateUuid(sanitizedSessionId)) {
    throw new ValidationError('Invalid session ID format');
  }
  
  if (!validateUuid(sanitizedUserId)) {
    throw new ValidationError('Invalid user ID format');
  }
  
  // Verify session belongs to user
  const { data: session, error: sessionError } = await supabase
    .from('user_sessions')
    .select('*')
    .eq('id', sanitizedSessionId)
    .eq('user_id', sanitizedUserId)
    .eq('active', true)
    .single();
  
  if (sessionError || !session) {
    throw new AuthenticationError('Session not found or expired');
  }
  
  // Extend session expiration
  const newExpiresAt = new Date();
  newExpiresAt.setHours(newExpiresAt.getHours() + 24); // Extend by 24 hours
  
  const { error: extendError } = await supabase
    .from('user_sessions')
    .update({ 
      expires_at: newExpiresAt.toISOString(),
      last_activity: new Date().toISOString()
    })
    .eq('id', sanitizedSessionId);
  
  if (extendError) {
    throw createDatabaseError('extend session', extendError);
  }
  
  return NextResponse.json({
    message: 'Session extended successfully',
    expiresAt: newExpiresAt.toISOString()
  });
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');
    
    if (!userId) {
      throw new ValidationError('User ID is required');
    }
    
    const sanitizedUserId = sanitizeInput(userId);
    
    if (!validateUuid(sanitizedUserId)) {
      throw new ValidationError('Invalid user ID format');
    }
    
    // Initialize Supabase client
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    );
    
    // Get active session count
    const { data: sessions, error: sessionsError } = await supabase
      .from('user_sessions')
      .select('id')
      .eq('user_id', sanitizedUserId)
      .eq('active', true);
    
    if (sessionsError) {
      throw createDatabaseError('get session count', sessionsError);
    }
    
    return NextResponse.json({
      activeSessionCount: sessions?.length || 0,
      maxSessions: 5 // Maximum allowed sessions
    });
    
  } catch (error) {
    console.error('Session count error:', error);
    
    if (error instanceof ValidationError) {
      return NextResponse.json(
        { error: error.message },
        { status: 400 }
      );
    }
    
    return NextResponse.json(
      { error: 'Failed to get session count' },
      { status: 500 }
    );
  }
}
