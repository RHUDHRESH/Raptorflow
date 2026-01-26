import { createClient } from '@/lib/auth-client'
import { authenticator } from 'otplib'

// MFA types
export interface MFASetup {
  mfa_type: 'totp' | 'sms' | 'email' | 'backup_codes'
  is_enabled: boolean
  is_primary: boolean
  setup_completed_at?: string
  last_used_at?: string
  usage_count?: number
}

export interface TOTPSetupResult {
  secret: string
  backup_codes: string[]
  qr_code_url: string
}

export interface MFAChallenge {
  challenge_token: string
  mfa_type: string
  expires_at: string
}

export interface MFAVerification {
  success: boolean
  mfa_type: string
  user_id: string
  session_token: string
  error_message?: string
}

// Client-side MFA functions
export async function setupTOTP(
  backupCodesCount: number = 10
): Promise<TOTPSetupResult | null> {
  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }

  try {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      throw new Error('User not authenticated')
    }

    const { data, error } = await supabase.rpc('setup_totp_mfa', {
      p_user_id: user.id,
      p_backup_codes_count: backupCodesCount
    })

    if (error) {
      console.error('TOTP setup error:', error)
      throw error
    }

    return data?.[0] || null

  } catch (error) {
    console.error('TOTP setup error:', error)
    throw error
  }
}

export async function setupSMS(phoneNumber: string): Promise<boolean> {
  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }

  try {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      throw new Error('User not authenticated')
    }

    const { data, error } = await supabase.rpc('setup_sms_mfa', {
      p_user_id: user.id,
      p_phone_number: phoneNumber
    })

    if (error) {
      console.error('SMS setup error:', error)
      throw error
    }

    return !!data

  } catch (error) {
    console.error('SMS setup error:', error)
    throw error
  }
}

export async function createMFAChallenge(
  mfaType: 'totp' | 'sms' | 'email' | 'backup_code',
  sessionId?: string,
  deviceFingerprint?: string
): Promise<string | null> {
  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }

  try {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      throw new Error('User not authenticated')
    }

    const { data, error } = await supabase.rpc('create_mfa_challenge', {
      p_user_id: user.id,
      p_mfa_type: mfaType,
      p_session_id: sessionId,
      p_device_fingerprint: deviceFingerprint
    })

    if (error) {
      console.error('MFA challenge creation error:', error)
      throw error
    }

    return data

  } catch (error) {
    console.error('MFA challenge creation error:', error)
    throw error
  }
}

export async function verifyMFAChallenge(
  challengeToken: string,
  code: string,
  deviceFingerprint?: string
): Promise<MFAVerification | null> {
  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }

  try {
    const { data, error } = await supabase.rpc('verify_mfa_challenge', {
      p_challenge_token: challengeToken,
      p_code: code,
      p_device_fingerprint: deviceFingerprint
    })

    if (error) {
      console.error('MFA verification error:', error)
      throw error
    }

    return data?.[0] || null

  } catch (error) {
    console.error('MFA verification error:', error)
    throw error
  }
}

export async function toggleMFAMethod(
  mfaType: 'totp' | 'sms' | 'email' | 'backup_codes',
  enabled: boolean
): Promise<boolean> {
  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }

  try {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      throw new Error('User not authenticated')
    }

    const { data, error } = await supabase.rpc('toggle_mfa_method', {
      p_user_id: user.id,
      p_mfa_type: mfaType,
      p_enabled: enabled
    })

    if (error) {
      console.error('MFA toggle error:', error)
      throw error
    }

    return !!data

  } catch (error) {
    console.error('MFA toggle error:', error)
    throw error
  }
}

export async function getUserMFAStatus(): Promise<MFASetup[]> {
  const supabase = createClient()
  if (!supabase) {
    throw new Error('Supabase client not available')
  }

  try {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      throw new Error('User not authenticated')
    }

    const { data, error } = await supabase.rpc('get_user_mfa_status', {
      p_user_id: user.id
    })

    if (error) {
      console.error('MFA status error:', error)
      throw error
    }

    return data || []

  } catch (error) {
    console.error('MFA status error:', error)
    throw error
  }
}

// TOTP utilities
export class TOTPUtils {
  // Generate TOTP URI for QR code
  static generateTOTPUri(secret: string, email: string, issuer: string = 'Raptorflow'): string {
    const encodedSecret = encodeURIComponent(secret)
    const encodedEmail = encodeURIComponent(email)
    const encodedIssuer = encodeURIComponent(issuer)

    return `otpauth://totp/${encodedIssuer}:${encodedEmail}?secret=${encodedSecret}&issuer=${encodedIssuer}`
  }

  // Generate QR code URL (using external service)
  static generateQRCodeUrl(uri: string, size: number = 200): string {
    return `https://api.qrserver.com/v1/create-qr-code/?size=${size}x${size}&data=${encodeURIComponent(uri)}`
  }

  // Verify TOTP code (simplified - in production, use a proper TOTP library)
  static verifyTOTP(secret: string, token: string, window: number = 1): boolean {
    // This is a simplified implementation
    // In production, use a proper TOTP library like 'otplib'
    try {
      return authenticator.verify({
        token,
        secret,
        window
      })
    } catch (error) {
      console.error('TOTP verification error:', error)
      return false
    }
  }

  // Generate current TOTP code
  static generateTOTP(secret: string): string {
    try {
      return authenticator.generate(secret)
    } catch (error) {
      console.error('TOTP generation error:', error)
      return ''
    }
  }
}

// Device fingerprinting utilities
export class DeviceFingerprint {
  private static getBrowserInfo(): Record<string, string> {
    return {
      userAgent: navigator.userAgent,
      language: navigator.language,
      platform: navigator.platform,
      cookieEnabled: navigator.cookieEnabled.toString(),
      doNotTrack: navigator.doNotTrack || 'unknown',
      screenResolution: `${screen.width}x${screen.height}`,
      colorDepth: screen.colorDepth.toString(),
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      sessionStorage: typeof sessionStorage !== 'undefined' ? 'available' : 'unavailable',
      localStorage: typeof localStorage !== 'undefined' ? 'available' : 'unavailable'
    }
  }

  static generateFingerprint(): string {
    const info = this.getBrowserInfo()
    const fingerprintString = Object.values(info).join('|')

    // Simple hash (in production, use a proper hashing library)
    let hash = 0
    for (let i = 0; i < fingerprintString.length; i++) {
      const char = fingerprintString.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32-bit integer
    }

    return Math.abs(hash).toString(16)
  }

  static async getAdvancedFingerprint(): Promise<string> {
    try {
      // Use Canvas fingerprinting
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.textBaseline = 'top'
        ctx.font = '14px Arial'
        ctx.fillText('Device fingerprint', 2, 2)
        const canvasFingerprint = canvas.toDataURL()

        // Combine with basic fingerprint
        const basicFingerprint = this.generateFingerprint()
        return this.simpleHash(basicFingerprint + canvasFingerprint)
      }
    } catch (error) {
      console.error('Advanced fingerprinting error:', error)
    }

    return this.generateFingerprint()
  }

  private static simpleHash(str: string): string {
    let hash = 0
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash
    }
    return Math.abs(hash).toString(16)
  }
}

// MFA session management
export class MFASession {
  private static readonly SESSION_KEY = 'mfa_session_token'
  private static readonly DEVICE_KEY = 'mfa_device_fingerprint'

  static storeSession(sessionToken: string, deviceFingerprint: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(this.SESSION_KEY, sessionToken)
      localStorage.setItem(this.DEVICE_KEY, deviceFingerprint)
    }
  }

  static getSession(): { sessionToken: string; deviceFingerprint: string } | null {
    if (typeof window !== 'undefined') {
      const sessionToken = localStorage.getItem(this.SESSION_KEY)
      const deviceFingerprint = localStorage.getItem(this.DEVICE_KEY)

      if (sessionToken && deviceFingerprint) {
        return { sessionToken, deviceFingerprint }
      }
    }

    return null
  }

  static clearSession(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(this.SESSION_KEY)
      localStorage.removeItem(this.DEVICE_KEY)
    }
  }

  static isSessionValid(): boolean {
    const session = this.getSession()
    if (!session) return false

    // TODO: Verify session with server
    // For now, just check if session exists
    return true
  }
}

// MFA configuration
export const MFAConfig = {
  // Challenge expiration times (in minutes)
  CHALLENGE_EXPIRY: {
    TOTP: 10,
    SMS: 10,
    EMAIL: 10,
    BACKUP_CODE: 10
  },

  // Failed attempt limits
  MAX_FAILED_ATTEMPTS: 5,
  LOCKOUT_DURATION: 15, // minutes

  // Backup codes
  DEFAULT_BACKUP_CODES_COUNT: 10,
  BACKUP_CODE_LENGTH: 6,

  // Trusted devices
  DEFAULT_TRUST_DURATION: 30, // days

  // Rate limiting
  CHALLENGE_RATE_LIMIT: 3, // per minute
  SETUP_RATE_LIMIT: 1 // per hour
}

// MFA error types
export class MFAError extends Error {
  constructor(
    message: string,
    public code: string,
    public type: 'setup' | 'verification' | 'configuration' | 'session'
  ) {
    super(message)
    this.name = 'MFAError'
  }
}

export const MFAErrors = {
  // Setup errors
  SETUP_FAILED: new MFAError('MFA setup failed', 'SETUP_FAILED', 'setup'),
  INVALID_PHONE: new MFAError('Invalid phone number', 'INVALID_PHONE', 'setup'),
  INVALID_EMAIL: new MFAError('Invalid email address', 'INVALID_EMAIL', 'setup'),

  // Verification errors
  INVALID_CODE: new MFAError('Invalid verification code', 'INVALID_CODE', 'verification'),
  EXPIRED_CHALLENGE: new MFAError('Challenge expired', 'EXPIRED_CHALLENGE', 'verification'),
  MAX_ATTEMPTS: new MFAError('Maximum attempts exceeded', 'MAX_ATTEMPTS', 'verification'),
  METHOD_LOCKED: new MFAError('MFA method locked', 'METHOD_LOCKED', 'verification'),

  // Configuration errors
  METHOD_NOT_ENABLED: new MFAError('MFA method not enabled', 'METHOD_NOT_ENABLED', 'configuration'),
  NO_PRIMARY_METHOD: new MFAError('No primary MFA method configured', 'NO_PRIMARY_METHOD', 'configuration'),

  // Session errors
  INVALID_SESSION: new MFAError('Invalid MFA session', 'INVALID_SESSION', 'session'),
  SESSION_EXPIRED: new MFAError('MFA session expired', 'SESSION_EXPIRED', 'session')
}
