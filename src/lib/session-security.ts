// Session Security System
// Implements concurrent session limits, device fingerprinting, and anomaly detection

import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import crypto from 'crypto'

export interface DeviceFingerprint {
  id: string
  user_id: string
  fingerprint_hash: string
  user_agent: string
  ip_address: string
  screen_resolution?: string
  timezone?: string
  language?: string
  platform?: string
  is_mobile: boolean
  is_tablet: boolean
  trusted: boolean
  first_seen: string
  last_seen: string
  access_count: number
}

export interface UserSession {
  id: string
  user_id: string
  session_token: string
  device_fingerprint_id: string
  ip_address: string
  user_agent: string
  is_active: boolean
  expires_at: string
  created_at: string
  last_accessed: string
  access_count: number
  location?: {
    country?: string
    city?: string
    latitude?: number
    longitude?: number
  }
}

export interface SecurityEvent {
  id: string
  user_id: string
  event_type: 'login' | 'logout' | 'suspicious_activity' | 'session_limit_exceeded' | 'new_device' | 'location_change' | 'concurrent_login'
  severity: 'low' | 'medium' | 'high' | 'critical'
  message: string
  metadata: any
  ip_address: string
  user_agent: string
  created_at: string
}

export interface SessionLimit {
  max_concurrent: number
  max_per_device: number
  trusted_device_limit: number
  session_duration_hours: number
  require_mfa_for_new_device: boolean
  auto_logout_inactive_hours: number
}

export class SessionSecurity {
  private supabase: any

  constructor() {
    this.supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return cookies().getAll()
          },
          setAll(cookiesToSet: any[]) {
            try {
              cookiesToSet.forEach(({ name, value, options }) =>
                cookies().set(name, value, options)
              )
            } catch {
              // The `setAll` method was called from a Server Component.
              // This can be ignored.
            }
          },
        },
      }
    )
  }

  /**
   * Generate device fingerprint from request data
   */
  generateDeviceFingerprint(request: {
    userAgent?: string
    ipAddress?: string
    screenResolution?: string
    timezone?: string
    language?: string
    platform?: string
  }): string {
    const components = [
      request.userAgent || '',
      request.ipAddress || '',
      request.screenResolution || '',
      request.timezone || '',
      request.language || '',
      request.platform || '',
      // Add browser-specific entropy
      this.getBrowserEntropy(request.userAgent || '')
    ]

    return crypto.createHash('sha256').update(components.join('|')).digest('hex')
  }

  /**
   * Get browser-specific entropy for fingerprinting
   */
  private getBrowserEntropy(userAgent: string): string {
    const entropy = []
    
    // Extract browser-specific features
    if (userAgent.includes('Chrome')) entropy.push('chrome')
    if (userAgent.includes('Firefox')) entropy.push('firefox')
    if (userAgent.includes('Safari')) entropy.push('safari')
    if (userAgent.includes('Edge')) entropy.push('edge')
    if (userAgent.includes('Opera')) entropy.push('opera')
    
    // Extract OS information
    if (userAgent.includes('Windows')) entropy.push('windows')
    if (userAgent.includes('Mac')) entropy.push('mac')
    if (userAgent.includes('Linux')) entropy.push('linux')
    if (userAgent.includes('Android')) entropy.push('android')
    if (userAgent.includes('iOS')) entropy.push('ios')
    
    // Extract device type
    if (userAgent.includes('Mobile')) entropy.push('mobile')
    if (userAgent.includes('Tablet')) entropy.push('tablet')
    
    return entropy.join('|')
  }

  /**
   * Get or create device fingerprint
   */
  async getOrCreateDeviceFingerprint(
    userId: string,
    fingerprintData: {
      fingerprint_hash: string
      user_agent: string
      ip_address: string
      screen_resolution?: string
      timezone?: string
      language?: string
      platform?: string
      is_mobile: boolean
      is_tablet: boolean
    }
  ): Promise<DeviceFingerprint> {
    try {
      // Check if device already exists
      const { data: existingDevice } = await this.supabase
        .from('device_fingerprints')
        .select('*')
        .eq('user_id', userId)
        .eq('fingerprint_hash', fingerprintData.fingerprint_hash)
        .single()

      if (existingDevice) {
        // Update last seen and access count
        const { data: updatedDevice } = await this.supabase
          .from('device_fingerprints')
          .update({
            last_seen: new Date().toISOString(),
            access_count: existingDevice.access_count + 1
          })
          .eq('id', existingDevice.id)
          .select('*')
          .single()

        return updatedDevice
      } else {
        // Create new device fingerprint
        const { data, error } = await this.supabase
          .from('device_fingerprints')
          .insert({
            user_id: userId,
            fingerprint_hash: fingerprintData.fingerprint_hash,
            user_agent: fingerprintData.user_agent,
            ip_address: fingerprintData.ip_address,
            screen_resolution: fingerprintData.screen_resolution,
            timezone: fingerprintData.timezone,
            language: fingerprintData.language,
            platform: fingerprintData.platform,
            is_mobile: fingerprintData.is_mobile,
            is_tablet: fingerprintData.is_tablet,
            trusted: false, // New devices start as untrusted
            first_seen: new Date().toISOString(),
            last_seen: new Date().toISOString(),
            access_count: 1
          })
          .select('*')
          .single()

        if (error) throw error

        // Log new device event
        await this.logSecurityEvent(userId, 'new_device', 'medium', 'New device detected', {
          device_id: data.id,
          fingerprint_hash: fingerprintData.fingerprint_hash,
          user_agent: fingerprintData.user_agent,
          ip_address: fingerprintData.ip_address
        }, fingerprintData.ip_address, fingerprintData.user_agent)

        return data
      }
    } catch (error) {
      console.error('Error getting/creating device fingerprint:', error)
      throw error
    }
  }

  /**
   * Create user session
   */
  async createSession(
    userId: string,
    sessionToken: string,
    deviceFingerprintId: string,
    sessionData: {
      ip_address: string
      user_agent: string
      location?: {
        country?: string
        city?: string
        latitude?: number
        longitude?: number
      }
    }
  ): Promise<UserSession> {
    try {
      // Check session limits
      const limits = await this.getSessionLimits(userId)
      const currentSessions = await this.getActiveSessionCount(userId)
      
      if (currentSessions >= limits.max_concurrent) {
        await this.logSecurityEvent(
          userId,
          'session_limit_exceeded',
          'high',
          'Maximum concurrent sessions exceeded',
          {
            current_sessions,
            max_sessions: limits.max_concurrent
          },
          sessionData.ip_address,
          sessionData.user_agent
        )
        
        // Remove oldest session
        await this.removeOldestSession(userId)
      }

      // Check per-device limits
      const deviceSessions = await this.getDeviceSessionCount(userId, deviceFingerprintId)
      if (deviceSessions >= limits.max_per_device) {
        await this.logSecurityEvent(
          userId,
          'concurrent_login',
          'medium',
          'Multiple sessions from same device',
          {
            device_sessions,
            max_per_device: limits.max_per_device
          },
          sessionData.ip_address,
          sessionData.user_agent
        )
        
        // Remove oldest session for this device
        await this.removeOldestDeviceSession(userId, deviceFingerprintId)
      }

      // Create new session
      const expiresAt = new Date(Date.now() + limits.session_duration_hours * 60 * 60 * 1000).toISOString()

      const { data, error } = await this.supabase
        .from('user_sessions')
        .insert({
          user_id: userId,
          session_token: sessionToken,
          device_fingerprint_id: deviceFingerprintId,
          ip_address: sessionData.ip_address,
          user_agent: sessionData.user_agent,
          is_active: true,
          expires_at: expiresAt,
          location: sessionData.location
        })
        .select('*')
        .single()

      if (error) throw error

      return data
    } catch (error) {
      console.error('Error creating session:', error)
      throw error
    }
  }

  /**
   * Validate session
   */
  async validateSession(
    sessionToken: string,
    request: {
      ipAddress?: string
      userAgent?: string
    }
  ): Promise<{
      valid: boolean
      session?: UserSession
      device?: DeviceFingerprint
      securityFlags?: string[]
    }> {
    try {
      // Get session
      const { data: session, error: sessionError } = await this.supabase
        .from('user_sessions')
        .select('*')
        .eq('session_token', sessionToken)
        .eq('is_active', true)
        .single()

      if (sessionError || !session) {
        return { valid: false }
      }

      // Check if session expired
      if (new Date(session.expires_at) < new Date()) {
        await this.deactivateSession(session.id)
        return { valid: false }
      }

      // Get device fingerprint
      const { data: device } = await this.supabase
        .from('device_fingerprints')
        .select('*')
        .eq('id', session.device_fingerprint_id)
        .single()

      if (!device) {
        return { valid: false }
      }

      const securityFlags: string[] = []

      // Check for suspicious activity
      if (request.ipAddress && request.ipAddress !== device.ip_address) {
        securityFlags.push('ip_address_changed')
        await this.logSecurityEvent(
          session.user_id,
          'suspicious_activity',
          'medium',
          'IP address changed for session',
          {
            session_id: session.id,
            device_id: device.id,
            old_ip: device.ip_address,
            new_ip: request.ipAddress
          },
          request.ipAddress,
          request.userAgent
        )
      }

      if (request.userAgent && request.userAgent !== device.user_agent) {
        securityFlags.push('user_agent_changed')
        await this.logSecurityEvent(
          session.user_id,
          'suspicious_activity',
          'medium',
          'User agent changed for session',
          {
            session_id: session.id,
            device_id: device.id,
            old_ua: device.user_agent,
            new_ua: request.userAgent
          },
          request.ipAddress,
          request.userAgent
        )
      }

      // Check location change
      if (request.ipAddress && this.isSignificantLocationChange(device.ip_address, request.ipAddress)) {
        securityFlags.push('location_change')
        await this.logSecurityEvent(
          session.user_id,
          'location_change',
          'medium',
          'Significant location change detected',
          {
            session_id: session.id,
            device_id: device.id,
            old_location: device.ip_address,
            new_location: request.ipAddress
          },
          request.ipAddress,
          request.userAgent
        )
      }

      // Update session access
      await this.updateSessionAccess(session.id)

      return {
        valid: true,
        session,
        device,
        securityFlags
      }
    } catch (error) {
      console.error('Error validating session:', error)
      return { valid: false }
    }
  }

  /**
   * Deactivate session
   */
  async deactivateSession(sessionId: string): Promise<void> {
    try {
      const { error } = await this.supabase
        .from('user_sessions')
        .update({
          is_active: false,
          last_accessed: new Date().toISOString()
        })
        .eq('id', sessionId)

      if (error) throw error
    } catch (error) {
      console.error('Error deactivating session:', error)
      throw error
    }
  }

  /**
   * Deactivate all user sessions
   */
  async deactivateAllUserSessions(userId: string): Promise<number> {
    try {
      const { error } = await this.supabase
        .from('user_sessions')
        .update({
          is_active: false,
          last_accessed: new Date().toISOString()
        })
        .eq('user_id', userId)
        .eq('is_active', true)

      if (error) throw error

      // Get count of deactivated sessions
      const { count } = await this.supabase
        .from('user_sessions')
        .select('id', { count: 'exact', head: true })
        .eq('user_id', userId)
        .eq('is_active', false)

      return count || 0
    } catch (error) {
      console.error('Error deactivating all user sessions:', error)
      throw error
    }
  }

  /**
   * Get active sessions for user
   */
  async getActiveSessions(userId: string): Promise<UserSession[]> {
    try {
      const { data, error } = await this.supabase
        .from('user_sessions')
        .select(`
          *,
          device_fingerprints (
            fingerprint_hash,
            user_agent,
            ip_address,
            trusted,
            first_seen,
            access_count
          )
        `)
        .eq('user_id', userId)
        .eq('is_active', true)
        .gt('expires_at', new Date().toISOString())
        .order('last_accessed', { ascending: false })

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting active sessions:', error)
      throw error
    }
  }

  /**
   * Get session limits for user
   */
  async getSessionLimits(userId: string): Promise<SessionLimit> {
    try {
      // Get user's subscription plan to determine limits
      const { data: profile } = await this.supabase
        .from('profiles')
        .select('subscription_plan')
        .eq('id', userId)
        .single()

      const plan = profile?.subscription_plan || 'free'

      const limits: Record<string, SessionLimit> = {
        free: {
          max_concurrent: 3,
          max_per_device: 1,
          trusted_device_limit: 2,
          session_duration_hours: 24,
          require_mfa_for_new_device: false,
          auto_logout_inactive_hours: 12
        },
        ascent: {
          max_concurrent: 5,
          max_per_device: 2,
          trusted_device_limit: 5,
          session_duration_hours: 48,
          require_mfa_for_new_device: true,
          auto_logout_inactive_hours: 24
        },
        glide: {
          max_concurrent: 10,
          max_per_device: 3,
          trusted_device_limit: 10,
          session_duration_hours: 72,
          require_mfa_for_new_device: true,
          auto_logout_inactive_hours: 48
        },
        soar: {
          max_concurrent: 20,
          max_per_device: 5,
          trusted_device_limit: 20,
          session_duration_hours: 168, // 7 days
          require_mfa_for_new_device: true,
          auto_logout_inactive_hours: 72
        }
      }

      return limits[plan] || limits.free
    } catch (error) {
      console.error('Error getting session limits:', error)
      return {
        max_concurrent: 3,
        max_per_device: 1,
        trusted_device_limit: 2,
        session_duration_hours: 24,
        require_mfa_for_new_device: false,
        auto_logout_inactive_hours: 12
      }
    }
  }

  /**
   * Get active session count for user
   */
  async getActiveSessionCount(userId: string): Promise<number> {
    try {
      const { count } = await this.supabase
        .from('user_sessions')
        .select('id', { count: 'exact', head: true })
        .eq('user_id', userId)
        .eq('is_active', true)
        .gt('expires_at', new Date().toISOString())

      return count || 0
    } catch (error) {
      console.error('Error getting active session count:', error)
      return 0
    }
  }

  /**
   * Get session count for device
   */
  async getDeviceSessionCount(userId: string, deviceFingerprintId: string): Promise<number> {
    try {
      const { count } = await this.supabase
        .from('user_sessions')
        .select('id', { count: 'exact', head: true })
        .eq('user_id', userId)
        .eq('device_fingerprint_id', deviceFingerprintId)
        .eq('is_active', true)
        .gt('expires_at', new Date().toISOString())

      return count || 0
    } catch (error) {
      console.error('Error getting device session count:', error)
      return 0
    }
  }

  /**
   * Remove oldest session for user
   */
  async removeOldestSession(userId: string): Promise<void> {
    try {
      const { data: oldestSession } = await this.supabase
        .from('user_sessions')
        .select('id')
        .eq('user_id', userId)
        .eq('is_active', true)
        .order('last_accessed', { ascending: true })
        .limit(1)
        .single()

      if (oldestSession) {
        await this.deactivateSession(oldestSession.id)
      }
    } catch (error) {
      console.error('Error removing oldest session:', error)
      // Don't throw error for cleanup failures
    }
  }

  /**
   * Remove oldest session for device
   */
  async removeOldestDeviceSession(userId: string, deviceFingerprintId: string): Promise<void> {
    try {
      const { data: oldestSession } = await this.supabase
        .from('user_sessions')
        .select('id')
        .eq('user_id', userId)
        .eq('device_fingerprint_id', deviceFingerprintId)
        .eq('is_active', true)
        .order('last_accessed', { ascending: true })
        .limit(1)
        .single()

      if (oldestSession) {
        await this.deactivateSession(oldestSession.id)
      }
    } catch (error) {
      console.error('Error removing oldest device session:', error)
      // Don't throw error for cleanup failures
    }
  }

  /**
   * Update session access
   */
  async updateSessionAccess(sessionId: string): Promise<void> {
    try {
      await this.supabase
        .from('user_sessions')
        .update({
          last_accessed: new Date().toISOString(),
          access_count: this.supabase.rpc('increment', { count: 1 })
        })
        .eq('id', sessionId)
    } catch (error) {
      console.error('Error updating session access:', error)
      // Don't throw error for logging failures
    }
  }

  /**
   * Trust device
   */
  async trustDevice(deviceFingerprintId: string): Promise<void> {
    try {
      await this.supabase
        .from('device_fingerprints')
        .update({
          trusted: true
        })
        .eq('id', deviceFingerprintId)
    } catch (error) {
      console.error('Error trusting device:', error)
      throw error
    }
  }

  /**
   * Untrust device
   */
  async untrustDevice(deviceFingerprintId: string): Promise<void> {
    try {
      await this.supabase
        .from('device_fingerprints')
        .update({
          trusted: false
        })
        .eq('id', deviceFingerprintId)
    } catch (error) {
      console.error('Error untrusting device:', error)
      throw error
    }
  }

  /**
   * Log security event
   */
  async logSecurityEvent(
    userId: string,
    eventType: string,
    severity: string,
    message: string,
    metadata: any,
    ipAddress?: string,
    userAgent?: string
  ): Promise<void> {
    try {
      await this.supabase
        .from('security_events')
        .insert({
          user_id: userId,
          event_type: eventType,
          severity,
          message,
          metadata,
          ip_address: ipAddress,
          user_agent: userAgent,
          created_at: new Date().toISOString()
        })
    } catch (error) {
      console.error('Error logging security event:', error)
      // Don't throw error for logging failures
    }
  }

  /**
   * Get security events for user
   */
  async getSecurityEvents(
    userId: string,
    limit: number = 50
  ): Promise<SecurityEvent[]> {
    try {
      const { data, error } = await this.supabase
        .from('security_events')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(limit)

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting security events:', error)
      throw error
    }
  }

  /**
   * Clean up expired sessions
   */
  async cleanupExpiredSessions(): Promise<number> {
    try {
      const { error } = await this.supabase
        .from('user_sessions')
        .update({
          is_active: false,
          last_accessed: new Date().toISOString()
        })
        .lt('expires_at', new Date().toISOString())
        .eq('is_active', true)

      if (error) throw error

      // Get count of cleaned up sessions
      const { count } = await this.supabase
        .from('user_sessions')
        .select('id', { count: 'exact', head: true })
        .eq('is_active', false)
        .lt('expires_at', new Date().toISOString())

      return count || 0
    } catch (error) {
      console.error('Error cleaning up expired sessions:', error)
      return 0
    }
  }

  /**
   * Check if IP change is significant
   */
  private isSignificantLocationChange(oldIp: string, newIp: string): boolean {
    // Simple check for significant IP change
    const oldParts = oldIp.split('.')
    const newParts = newIp.split('.')
    
    // Check if first two octets changed (different ISP or region)
    if (oldParts.length >= 2 && newParts.length >= 2) {
      return oldParts[0] !== newParts[0] || oldParts[1] !== newParts[1]
    }
    
    return false
  }

  /**
   * Get session statistics
   */
  async getSessionStats(userId: string): Promise<{
    total_sessions: number
    active_sessions: number
    trusted_devices: number
    recent_security_events: number
    last_activity?: string
  }> {
    try {
      const [
        totalSessions,
        activeSessions,
        trustedDevices,
        recentEvents
      ] = await Promise.all([
          this.supabase
            .from('user_sessions')
            .select('id', { count: 'exact', head: true })
            .eq('user_id', userId),
          this.getActiveSessionCount(userId),
          this.supabase
            .from('device_fingerprints')
            .select('id', { count: 'exact', head: true })
            .eq('user_id', userId)
            .eq('trusted', true),
          this.supabase
            .from('security_events')
            .select('id', { count: 'exact', head: true })
            .eq('user_id', userId)
            .gte('created_at', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString())
        ])

      // Get last activity
      const { data: lastSession } = await this.supabase
        .from('user_sessions')
        .select('last_accessed')
        .eq('user_id', userId)
        .eq('is_active', true)
        .order('last_accessed', { ascending: false })
        .limit(1)
        .single()

      return {
        total_sessions: totalSessions || 0,
        active_sessions: activeSessions,
        trusted_devices: trustedDevices || 0,
        recent_security_events: recentEvents || 0,
        last_activity: lastSession?.last_accessed
      }
    } catch (error) {
      console.error('Error getting session stats:', error)
      throw error
    }
  }
}

export const sessionSecurity = new SessionSecurity()
