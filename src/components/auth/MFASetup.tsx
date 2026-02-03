'use client'

import React, { useState, useEffect } from 'react'
import {
  setupTOTP,
  setupSMS,
  toggleMFAMethod,
  getUserMFAStatus,
  MFAConfig,
  MFAError,
  type TOTPSetupResult,
  type MFASetup as MFASetupType,
  type MFAErrors
} from '@/lib/mfa'

interface MFASetupProps {
  onSuccess?: () => void
  onCancel?: () => void
}

export default function MFASetup({ onSuccess, onCancel }: MFASetupProps) {
  const [activeTab, setActiveTab] = useState<'totp' | 'sms'>('totp')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentMFA, setCurrentMFA] = useState<MFASetupType[]>([])
  const [totpSetup, setTotpSetup] = useState<TOTPSetupResult | null>(null)
  const [phoneNumber, setPhoneNumber] = useState('')
  const [backupCodesSaved, setBackupCodesSaved] = useState(false)

  useEffect(() => {
    loadMFAStatus()
  }, [])

  const loadMFAStatus = async () => {
    try {
      const status = await getUserMFAStatus()
      setCurrentMFA(status)
    } catch (error) {
      console.error('Failed to load MFA status:', error)
    }
  }

  const handleTOTPSetup = async () => {
    setLoading(true)
    setError(null)

    try {
      const result = await setupTOTP(MFAConfig.DEFAULT_BACKUP_CODES_COUNT)
      if (result) {
        setTotpSetup(result)
      }
    } catch (error) {
      if (error instanceof MFAError) {
        setError(error.message)
      } else {
        setError('Failed to setup TOTP')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSMSSetup = async () => {
    if (!phoneNumber.trim()) {
      setError('Please enter a valid phone number')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const success = await setupSMS(phoneNumber.trim())
      if (success) {
        await toggleMFAMethod('sms', true)
        await loadMFAStatus()
        onSuccess?.()
      }
    } catch (error) {
      if (error instanceof MFAError) {
        setError(error.message)
      } else {
        setError('Failed to setup SMS')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleEnableTOTP = async () => {
    if (!totpSetup) return

    setLoading(true)
    setError(null)

    try {
      await toggleMFAMethod('totp', true)
      await loadMFAStatus()
      onSuccess?.()
    } catch (error) {
      if (error instanceof MFAError) {
        setError(error.message)
      } else {
        setError('Failed to enable TOTP')
      }
    } finally {
      setLoading(false)
    }
  }

  const downloadBackupCodes = () => {
    if (!totpSetup) return

    const codesText = totpSetup.backup_codes.join('\n')
    const blob = new Blob([`Raptorflow Backup Codes\n\n${codesText}`], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'raptorflow-backup-codes.txt'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    setBackupCodesSaved(true)
  }

  const isMFAEnabled = (type: string) => {
    return currentMFA.some(mfa => mfa.mfa_type === type && mfa.is_enabled)
  }

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Setup Multi-Factor Authentication</h2>
        <p className="mt-2 text-gray-600">
          Add an extra layer of security to your account by enabling MFA.
        </p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Current MFA Status */}
      {currentMFA.length > 0 && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <h3 className="text-sm font-medium text-blue-800 mb-2">Current MFA Methods</h3>
          <div className="space-y-2">
            {currentMFA.map((mfa) => (
              <div key={mfa.mfa_type} className="flex items-center justify-between">
                <span className="text-sm text-blue-700 capitalize">
                  {mfa.mfa_type.replace('_', ' ')}
                  {mfa.is_primary && ' (Primary)'}
                </span>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  mfa.is_enabled
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {mfa.is_enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* MFA Setup Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('totp')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'totp'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Authenticator App
          </button>
          <button
            onClick={() => setActiveTab('sms')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'sms'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            disabled={isMFAEnabled('sms')}
          >
            SMS Verification
          </button>
        </nav>
      </div>

      {/* TOTP Setup */}
      {activeTab === 'totp' && (
        <div className="mt-6">
          {isMFAEnabled('totp') ? (
            <div className="text-center py-8">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="mt-4 text-lg font-medium text-gray-900">TOTP Already Enabled</h3>
              <p className="mt-2 text-sm text-gray-500">
                Your authenticator app is already configured for this account.
              </p>
            </div>
          ) : totpSetup ? (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900">Step 1: Scan QR Code</h3>
                <p className="mt-2 text-sm text-gray-600">
                  Use your authenticator app (Google Authenticator, Authy, etc.) to scan this QR code:
                </p>
                <div className="mt-4 p-4 bg-white border border-gray-200 rounded-lg">
                  <div className="text-center text-gray-500">
                    <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm6 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1z" />
                    </svg>
                    <p className="mt-2 text-sm">QR Code</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {totpSetup.qr_code_url}
                    </p>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900">Step 2: Enter Verification Code</h3>
                <p className="mt-2 text-sm text-gray-600">
                  Enter the 6-digit code from your authenticator app to verify the setup:
                </p>
                <div className="mt-4">
                  <input
                    type="text"
                    maxLength={6}
                    pattern="[0-9]*"
                    placeholder="000000"
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900">Step 3: Save Backup Codes</h3>
                <p className="mt-2 text-sm text-gray-600">
                  Save these backup codes in a secure location. You can use them to access your account if you lose your device:
                </p>
                <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
                  <div className="grid grid-cols-2 gap-2">
                    {totpSetup.backup_codes.map((code, index) => (
                      <code key={index} className="text-sm font-mono bg-white px-2 py-1 rounded">
                        {code}
                      </code>
                    ))}
                  </div>
                </div>
                <div className="mt-4 flex space-x-4">
                  <button
                    onClick={downloadBackupCodes}
                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    Download Backup Codes
                  </button>
                  <button
                    onClick={handleEnableTOTP}
                    disabled={loading || !backupCodesSaved}
                    className="flex-1 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:ring-green-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Enabling...' : 'Enable TOTP'}
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <button
                onClick={handleTOTPSetup}
                disabled={loading}
                className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? 'Setting up...' : 'Setup Authenticator App'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* SMS Setup */}
      {activeTab === 'sms' && (
        <div className="mt-6">
          {isMFAEnabled('sms') ? (
            <div className="text-center py-8">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="mt-4 text-lg font-medium text-gray-900">SMS Already Enabled</h3>
              <p className="mt-2 text-sm text-gray-500">
                SMS verification is already configured for this account.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                  Phone Number
                </label>
                <div className="mt-1">
                  <input
                    type="tel"
                    id="phone"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    placeholder="+1 (555) 123-4567"
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
                <p className="mt-2 text-sm text-gray-500">
                  We'll send a verification code to this number each time you sign in.
                </p>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={handleSMSSetup}
                  disabled={loading || !phoneNumber.trim()}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {loading ? 'Setting up...' : 'Enable SMS'}
                </button>
                <button
                  onClick={onCancel}
                  className="flex-1 bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300 focus:ring-gray-500 focus:ring-offset-2"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Security Tips */}
      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-md">
        <h3 className="text-sm font-medium text-blue-800 mb-2">Security Tips</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Store backup codes in a secure, offline location</li>
          <li>• Enable multiple MFA methods for backup access</li>
          <li>• Never share your verification codes with anyone</li>
          <li>• Keep your authenticator app updated</li>
        </ul>
      </div>
    </div>
  )
}
