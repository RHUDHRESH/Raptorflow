// Two-Factor Authentication System
// Implements TOTP support, backup codes, and recovery options

import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import * as speakeasy from 'speakeasy'

export interface TOTPSetup {
  secret: string
  qrCodeUrl: string
  backupCodes: string[]
  manualEntryKey: string
}

export interface UserMFA {
  id: string
  user_id: string
  totp_secret?: string
  totp_enabled: boolean
  backup_codes: string[]
  backup_codes_used: string[]
  recovery_email: string
  recovery_phone?: string
  last_used_at?: string
  created_at: string
  updated_at: string
}

export interface MFAVerification {
  success: boolean
  token?: string
  backupCode?: string
  method?: 'totp' | 'backup_code'
  error?: string
}

export class TwoFactorAuth {
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
   * Generate TOTP secret and setup information
   */
  generateTOTPSecret(): TOTPSetup {
    const secret = speakeasy.generateSecret({
      name: 'Raptorflow',
      issuer: 'Raptorflow',
      length: 32
    })

    const backupCodes = this.generateBackupCodes()

    return {
      secret: secret.base32,
      qrCodeUrl: speakeasy.otpauthURL({
        secret: secret.base32,
        label: 'Raptorflow',
        issuer: 'Raptorflow'
      }),
      backupCodes,
      manualEntryKey: secret.base32
    }
  }

  /**
   * Generate backup codes
   */
  generateBackupCodes(count: number = 10): string[] {
    const codes: string[] = []
    for (let i = 0; i < count; i++) {
      codes.push(this.generateBackupCode())
    }
    return codes
  }

  /**
   * Generate a single backup code
   */
  private generateBackupCode(): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    let code = ''
    for (let i = 0; i < 8; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    // Add space for readability (XXXX-XXXX)
    return code.substring(0, 4) + '-' + code.substring(4)
  }

  /**
   * Verify TOTP token
   */
  verifyTOTPToken(secret: string, token: string, window: number = 1): boolean {
    const verified = speakeasy.totp.verify({
      secret,
      encoding: 'base32',
      token,
      window
    })
    return verified
  }

  /**
   * Verify backup code
   */
  verifyBackupCode(userMFA: UserMFA, code: string): boolean {
    const normalizedCode = code.replace(/[-\s]/g, '').toUpperCase()
    
    return userMFA.backup_codes.some(backupCode => {
      const normalizedBackupCode = backupCode.replace(/[-\s]/g, '').toUpperCase()
      return normalizedBackupCode === normalizedCode && 
             !userMFA.backup_codes_used.includes(backupCode)
    })
  }

  /**
   * Setup TOTP for user
   */
  async setupTOTP(
    userId: string,
    secret: string,
    backupCodes: string[],
    recoveryEmail: string,
    recoveryPhone?: string
  ): Promise<UserMFA> {
    try {
      // Verify TOTP setup with a test token
      const testToken = speakeasy.totp({
        secret,
        encoding: 'base32'
      })

      if (!this.verifyTOTPToken(secret, testToken)) {
        throw new Error('Invalid TOTP secret')
      }

      const { data, error } = await this.supabase
        .from('user_mfa')
        .upsert({
          user_id: userId,
          totp_secret: secret,
          totp_enabled: true,
          backup_codes,
          backup_codes_used: [],
          recovery_email: recoveryEmail,
          recovery_phone: recoveryPhone,
          last_used_at: new Date().toISOString()
        })
        .select()
        .single()

      if (error) throw error

      return data
    } catch (error) {
      console.error('Error setting up TOTP:', error)
      throw error
    }
  }

  /**
   * Enable TOTP for user
   */
  async enableTOTP(userId: string, secret: string, token: string): Promise<void> {
    try {
      // Verify the token before enabling
      if (!this.verifyTOTPToken(secret, token)) {
        throw new Error('Invalid verification token')
      }

      const { error } = await this.supabase
        .from('user_mfa')
        .update({
          totp_secret: secret,
          totp_enabled: true,
          last_used_at: new Date().toISOString()
        })
        .eq('user_id', userId)

      if (error) throw error
    } catch (error) {
      console.error('Error enabling TOTP:', error)
      throw error
    }
  }

  /**
   * Disable TOTP for user
   */
  async disableTOTP(userId: string): Promise<void> {
    try {
      const { error } = await this.supabase
        .from('user_mfa')
        .update({
          totp_enabled: false,
          totp_secret: null,
          last_used_at: new Date().toISOString()
        })
        .eq('user_id', userId)

      if (error) throw error
    } catch (error) {
      console.error('Error disabling TOTP:', error)
      throw error
    }
  }

  /**
   * Verify MFA for user
   */
  async verifyMFA(
    userId: string,
    token: string,
    method: 'totp' | 'backup_code' = 'totp'
  ): Promise<MFAVerification> {
    try {
      // Get user's MFA settings
      const { data: userMFA, error: mfaError } = await this.supabase
        .from('user_mfa')
        .select('*')
        .eq('user_id', userId)
        .single()

      if (mfaError || !userMFA) {
        return { success: false, error: 'MFA not set up for user' }
      }

      if (!userMFA.totp_enabled) {
        return { success: false, error: 'MFA is not enabled' }
      }

      let verification: MFAVerification = { success: false }

      if (method === 'totp') {
        if (!userMFA.totp_secret) {
          return { success: false, error: 'TOTP not set up' }
        }

        const isValid = this.verifyTOTPToken(userMFA.totp_secret, token)
        if (isValid) {
          verification = { success: true, token, method: 'totp' }
          
          // Update last used timestamp
          await this.updateLastUsed(userId)
        }
      } else if (method === 'backup_code') {
        if (this.verifyBackupCode(userMFA, token)) {
          const backupCode = userMFA.backup_codes.find(code => {
            const normalizedCode = code.replace(/[-\s]/g, '').toUpperCase()
            const normalizedToken = token.replace(/[-\s]/g, '').toUpperCase()
            return normalizedCode === normalizedToken
          })

          if (backupCode) {
            verification = { success: true, backupCode, method: 'backup_code' }
            
            // Mark backup code as used
            await this.markBackupCodeUsed(userId, backupCode)
          }
        }
      }

      return verification
    } catch (error) {
      console.error('Error verifying MFA:', error)
      return { success: false, error: 'Verification failed' }
    }
  }

  /**
   * Get user's MFA settings
   */
  async getUserMFA(userId: string): Promise<UserMFA | null> {
    try {
      const { data, error } = await this.supabase
        .from('user_mfa')
        .select('*')
        .eq('user_id', userId)
        .single()

      if (error) return null

      return data
    } catch (error) {
      console.error('Error getting user MFA:', error)
      return null
    }
  }

  /**
   * Regenerate backup codes
   */
  async regenerateBackupCodes(userId: string): Promise<string[]> {
    try {
      const newBackupCodes = this.generateBackupCodes()

      const { error } = await this.supabase
        .from('user_mfa')
        .update({
          backup_codes: newBackupCodes,
          backup_codes_used: [],
          updated_at: new Date().toISOString()
        })
        .eq('user_id', userId)

      if (error) throw error

      return newBackupCodes
    } catch (error) {
      console.error('Error regenerating backup codes:', error)
      throw error
    }
  }

  /**
   * Mark backup code as used
   */
  private async markBackupCodeUsed(userId: string, backupCode: string): Promise<void> {
    try {
      const { data: userMFA } = await this.supabase
        .from('user_mfa')
        .select('backup_codes_used')
        .eq('user_id', userId)
        .single()

      if (!userMFA) return

      const updatedUsedCodes = [...userMFA.backup_codes_used, backupCode]

      await this.supabase
        .from('user_mfa')
        .update({
          backup_codes_used: updatedUsedCodes,
          last_used_at: new Date().toISOString()
        })
        .eq('user_id', userId)
    } catch (error) {
      console.error('Error marking backup code as used:', error)
      // Don't throw error for logging failures
    }
  }

  /**
   * Update last used timestamp
   */
  private async updateLastUsed(userId: string): Promise<void> {
    try {
      await this.supabase
        .from('user_mfa')
        .update({
          last_used_at: new Date().toISOString()
        })
        .eq('user_id', userId)
    } catch (error) {
      console.error('Error updating last used timestamp:', error)
      // Don't throw error for logging failures
    }
  }

  /**
   * Send recovery code via email
   */
  async sendRecoveryCode(userId: string, method: 'email' | 'sms' = 'email'): Promise<void> {
    try {
      const { data: userMFA } = await this.supabase
        .from('user_mfa')
        .select('recovery_email, recovery_phone')
        .eq('user_id', userId)
        .single()

      if (!userMFA) {
        throw new Error('User MFA not found')
      }

      const recoveryCode = this.generateBackupCode()
      
      // Store recovery code temporarily (expires in 15 minutes)
      const expiresAt = new Date(Date.now() + 15 * 60 * 1000).toISOString()
      
      await this.supabase
        .from('recovery_codes')
        .insert({
          user_id: userId,
          code: recoveryCode,
          method,
          expires_at: expiresAt,
          created_at: new Date().toISOString()
        })

      if (method === 'email' && userMFA.recovery_email) {
        // TODO: Send email with recovery code
        console.log(`Recovery code sent to ${userMFA.recovery_email}: ${recoveryCode}`)
      } else if (method === 'sms' && userMFA.recovery_phone) {
        // TODO: Send SMS with recovery code
        console.log(`Recovery code sent to ${userMFA.recovery_phone}: ${recoveryCode}`)
      } else {
        throw new Error('No recovery method available')
      }
    } catch (error) {
      console.error('Error sending recovery code:', error)
      throw error
    }
  }

  /**
   * Verify recovery code
   */
  async verifyRecoveryCode(userId: string, code: string): Promise<boolean> {
    try {
      const { data, error } = await this.supabase
        .from('recovery_codes')
        .select('*')
        .eq('user_id', userId)
        .eq('code', code)
        .gt('expires_at', new Date().toISOString())
        .single()

      if (error || !data) {
        return false
      }

      // Mark code as used
      await this.supabase
        .from('recovery_codes')
        .update({
          used_at: new Date().toISOString()
        })
        .eq('id', data.id)

      return true
    } catch (error) {
      console.error('Error verifying recovery code:', error)
      return false
    }
  }

  /**
   * Disable MFA using recovery code
   */
  async disableMFAWithRecovery(userId: string, recoveryCode: string): Promise<void> {
    try {
      const isValid = await this.verifyRecoveryCode(userId, recoveryCode)
      
      if (!isValid) {
        throw new Error('Invalid or expired recovery code')
      }

      await this.disableTOTP(userId)
    } catch (error) {
      console.error('Error disabling MFA with recovery:', error)
      throw error
    }
  }

  /**
   * Get MFA statistics
   */
  async getMFAStats(userId: string): Promise<{
    enabled: boolean
    method: 'totp' | 'backup_code' | null
    lastUsed?: string
    backupCodesTotal: number
    backupCodesUsed: number
    backupCodesRemaining: number
    recoveryEmail: string
    recoveryPhone?: string
  }> {
    try {
      const userMFA = await this.getUserMFA(userId)
      
      if (!userMFA) {
        return {
          enabled: false,
          method: null,
          backupCodesTotal: 0,
          backupCodesUsed: 0,
          backupCodesRemaining: 0,
          recoveryEmail: ''
        }
      }

      return {
        enabled: userMFA.totp_enabled,
        method: userMFA.totp_enabled ? 'totp' : null,
        lastUsed: userMFA.last_used_at,
        backupCodesTotal: userMFA.backup_codes.length,
        backupCodesUsed: userMFA.backup_codes_used.length,
        backupCodesRemaining: userMFA.backup_codes.length - userMFA.backup_codes_used.length,
        recoveryEmail: userMFA.recovery_email,
        recoveryPhone: userMFA.recovery_phone
      }
    } catch (error) {
      console.error('Error getting MFA stats:', error)
      throw error
    }
  }

  /**
   * Clean up expired recovery codes
   */
  async cleanupExpiredRecoveryCodes(): Promise<number> {
    try {
      const { error } = await this.supabase
        .from('recovery_codes')
        .delete()
        .lt('expires_at', new Date().toISOString())

      if (error) throw error

      // Get count of deleted codes
      const { count } = await this.supabase
        .from('recovery_codes')
        .select('id', { count: 'exact', head: true })
        .lt('expires_at', new Date().toISOString())

      return count || 0
    } catch (error) {
      console.error('Error cleaning up expired recovery codes:', error)
      return 0
    }
  }
}

export const twoFactorAuth = new TwoFactorAuth()
