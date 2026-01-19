// Database Token Store for Production
// Replaces in-memory storage with persistent database storage
// Includes in-memory fallback for development

import { createClient, type PostgrestError } from '@supabase/supabase-js';

// In-memory fallback store (only used if database fails)
const memoryStore = new Map<string, { email: string; expires_at: string; used_at?: string; created_at: string; updated_at: string }>();
// Always try database first - only use memory as last resort fallback
const HAS_DATABASE = !!(process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY);

interface TokenData {
  token: string;
  email: string;
  expires_at: string;
  used_at?: string;
  created_at: string;
  updated_at: string;
}

interface DatabaseToken {
  token: string;
  email: string;
  expires_at: string;
  used_at?: string | null;
  created_at: string;
  updated_at: string;
}

class DatabaseTokenStore {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private supabase: any;

  constructor() {
    this.supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    );
  }

  /**
   * Store a new reset token in the database
   */
  async storeToken(token: string, email: string, expires: number): Promise<boolean> {
    const expiresAt = new Date(expires).toISOString();
    const now = new Date().toISOString();
    
    // Always try database first if configured
    if (!HAS_DATABASE) {
      memoryStore.set(token, { 
        email, 
        expires_at: expiresAt, 
        created_at: now, 
        updated_at: now 
      });
      console.log('[TokenStore] No database configured, stored token in memory for:', email);
      return true;
    }
    
    try {
      const { error } = await this.supabase
        .from('password_reset_tokens')
        .insert({
          token,
          email,
          expires_at: expiresAt,
        });

      if (error) {
        console.error('Error storing token:', error);
        // Fallback to memory
        memoryStore.set(token, { email, expires_at: expiresAt, created_at: now, updated_at: now });
        return true;
      }

      return true;
    } catch (error) {
      console.error('Database error storing token:', error);
      // Fallback to memory
      memoryStore.set(token, { email, expires_at: expiresAt, created_at: now, updated_at: now });
      return true;
    }
  }

  /**
   * Retrieve token data from database
   */
  async getToken(token: string): Promise<TokenData | null> {
    // No database - use memory only
    if (!HAS_DATABASE) {
      const memData = memoryStore.get(token);
      if (!memData) {
        console.log('[TokenStore] Token not found in memory');
        return null;
      }
      
      if (new Date(memData.expires_at) < new Date()) {
        memoryStore.delete(token);
        return null;
      }
      
      if (memData.used_at) {
        return null;
      }
      
      console.log('[TokenStore] Retrieved token from memory for:', memData.email);
      return {
        token,
        email: memData.email,
        expires_at: memData.expires_at,
        used_at: memData.used_at,
        created_at: memData.created_at,
        updated_at: memData.updated_at
      };
    }
    
    try {
      const { data, error } = await this.supabase
        .from('password_reset_tokens')
        .select('*')
        .eq('token', token)
        .single();

      if (error) {
        console.error('Error retrieving token:', error);
        // Check memory fallback
        const memData = memoryStore.get(token);
        if (memData && new Date(memData.expires_at) > new Date() && !memData.used_at) {
          return { token, ...memData };
        }
        return null;
      }

      if (!data) {
        return null;
      }

      const tokenData = data as DatabaseToken;

      // Check if token has expired
      if (new Date(tokenData.expires_at) < new Date()) {
        await this.deleteToken(token);
        return null;
      }

      // Check if token was already used
      if (tokenData.used_at) {
        return null;
      }

      return {
        token: tokenData.token,
        email: tokenData.email,
        expires_at: tokenData.expires_at,
        used_at: tokenData.used_at || undefined,
        created_at: tokenData.created_at,
        updated_at: tokenData.updated_at
      };
    } catch (error) {
      console.error('Database error retrieving token:', error);
      return null;
    }
  }

  /**
   * Delete a token from database
   */
  async deleteToken(token: string): Promise<boolean> {
    // No database - use memory only
    if (!HAS_DATABASE) {
      memoryStore.delete(token);
      console.log('[TokenStore] Deleted token from memory');
      return true;
    }
    
    try {
      const { error } = await this.supabase
        .from('password_reset_tokens')
        .delete()
        .eq('token', token);

      if (error) {
        console.error('Error deleting token:', error);
        memoryStore.delete(token);
        return true;
      }

      memoryStore.delete(token);
      return true;
    } catch (error) {
      console.error('Database error deleting token:', error);
      memoryStore.delete(token);
      return true;
    }
  }

  /**
   * Mark token as used
   */
  async markTokenUsed(token: string): Promise<boolean> {
    try {
      const { error } = await this.supabase
        .from('password_reset_tokens')
        .update({ used_at: new Date().toISOString() })
        .eq('token', token);

      if (error) {
        console.error('Error marking token as used:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Database error marking token as used:', error);
      return false;
    }
  }

  /**
   * Clean up expired tokens
   */
  async cleanupExpiredTokens(): Promise<number> {
    try {
      const { data, error } = await this.supabase
        .from('password_reset_tokens')
        .delete()
        .lt('expires_at', new Date().toISOString());

      if (error) {
        console.error('Error cleaning up expired tokens:', error);
        return 0;
      }

      return Array.isArray(data) ? data.length : 0;
    } catch (error) {
      console.error('Database error cleaning up expired tokens:', error);
      return 0;
    }
  }

  /**
   * Get token statistics
   */
  async getTokenStats(): Promise<{
    total: number;
    active: number;
    expired: number;
    used: number;
  }> {
    try {
      const now = new Date().toISOString();
      
      // Get total tokens
      const { count: total, error: totalError } = await this.supabase
        .from('password_reset_tokens')
        .select('*', { count: 'exact', head: true });

      // Get active tokens
      const { count: active, error: activeError } = await this.supabase
        .from('password_reset_tokens')
        .select('*', { count: 'exact', head: true })
        .gt('expires_at', now)
        .is('used_at', null);

      // Get expired tokens
      const { count: expired, error: expiredError } = await this.supabase
        .from('password_reset_tokens')
        .select('*', { count: 'exact', head: true })
        .lt('expires_at', now);

      // Get used tokens
      const { count: used, error: usedError } = await this.supabase
        .from('password_reset_tokens')
        .select('*', { count: 'exact', head: true })
        .not('used_at', null);

      if (totalError || activeError || expiredError || usedError) {
        console.error('Error getting token stats');
        return { total: 0, active: 0, expired: 0, used: 0 };
      }

      return {
        total: total || 0,
        active: active || 0,
        expired: expired || 0,
        used: used || 0
      };
    } catch (error) {
      console.error('Database error getting token stats:', error);
      return { total: 0, active: 0, expired: 0, used: 0 };
    }
  }

  /**
   * Validate token and return email if valid
   */
  async validateToken(token: string): Promise<{ valid: boolean; email?: string }> {
    const tokenData = await this.getToken(token);
    
    if (!tokenData) {
      return { valid: false };
    }

    return { valid: true, email: tokenData.email };
  }

  /**
   * Check if token exists and is valid
   */
  async tokenExists(token: string): Promise<boolean> {
    const tokenData = await this.getToken(token);
    return tokenData !== null;
  }
}

// Export singleton instance
export const tokenStore = new DatabaseTokenStore();

// Export functions for backward compatibility
export function storeToken(token: string, email: string, expires: number): Promise<boolean> {
  return tokenStore.storeToken(token, email, expires);
}

export function getToken(token: string): Promise<TokenData | null> {
  return tokenStore.getToken(token);
}

export function deleteToken(token: string): Promise<boolean> {
  return tokenStore.deleteToken(token);
}

export function cleanupExpiredTokens(): Promise<number> {
  return tokenStore.cleanupExpiredTokens();
}

export function validateToken(token: string): Promise<{ valid: boolean; email?: string }> {
  return tokenStore.validateToken(token);
}

export function tokenExists(token: string): Promise<boolean> {
  return tokenStore.tokenExists(token);
}

// Auto-cleanup expired tokens every hour
setInterval(async () => {
  const cleaned = await tokenStore.cleanupExpiredTokens();
  if (cleaned > 0) {
    console.log(`Cleaned up ${cleaned} expired tokens`);
  }
}, 60 * 60 * 1000); // 1 hour
