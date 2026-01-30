import crypto from 'crypto'

export type PhonePeEnv = 'PRODUCTION' | 'SANDBOX'

export interface PhonePeConfig {
  merchantId: string
  saltKey: string
  saltIndex: string
  baseUrl: string
}

export interface PhonePePayPayload {
  merchantId: string
  merchantTransactionId: string
  merchantUserId: string
  amount: number
  redirectUrl: string
  redirectMode: 'REDIRECT' | 'POST'
  callbackUrl: string
  paymentInstrument: {
    type: 'PAY_PAGE'
  }
}

export interface PhonePeStatusResponse {
  success: boolean
  code?: string
  message?: string
  data?: {
    merchantId?: string
    merchantTransactionId?: string
    transactionId?: string
    state?: string
    amount?: number
    paymentInstrument?: Record<string, unknown>
    responseCode?: string
    responseMessage?: string
  }
}

export function getPhonePeConfig(): PhonePeConfig {
  const merchantId = process.env.PHONEPE_MERCHANT_ID || ''
  const saltKey = process.env.PHONEPE_SALT_KEY || ''
  const saltIndex = process.env.PHONEPE_SALT_INDEX || '1'
  const env = (process.env.PHONEPE_ENV || 'SANDBOX').toUpperCase() as PhonePeEnv
  const baseUrl =
    process.env.PHONEPE_BASE_URL ||
    (env === 'PRODUCTION'
      ? 'https://api.phonepe.com/apis/hermes'
      : 'https://api-preprod.phonepe.com/apis/pg-sandbox')

  return { merchantId, saltKey, saltIndex, baseUrl }
}

export function encodePayload(payload: Record<string, unknown>): string {
  return Buffer.from(JSON.stringify(payload)).toString('base64')
}

export function createXVerify(payload: string, apiPath: string, saltKey: string, saltIndex: string): string {
  const checksum = crypto.createHash('sha256').update(payload + apiPath + saltKey).digest('hex')
  return `${checksum}###${saltIndex}`
}

export function createWebhookSignature(rawBody: string, saltKey: string, saltIndex: string): string {
  const checksum = crypto.createHash('sha256').update(rawBody + saltKey).digest('hex')
  return `${checksum}###${saltIndex}`
}

export function normalizeSignature(signature: string | null): string | null {
  if (!signature) return null
  if (signature.startsWith('X-VERIFY ')) {
    return signature.slice('X-VERIFY '.length)
  }
  return signature
}
