import { createClient } from '@/lib/auth-client'

// GDPR compliance types
export interface DataSubjectConsent {
  id: string
  user_id: string
  consent_type: 'data_processing' | 'marketing' | 'analytics' | 'cookies' | 'third_party_sharing' | 'international_transfer'
  consent_given: boolean
  consent_version: string
  consent_text: string
  legal_basis: 'consent' | 'contract' | 'legal_obligation' | 'vital_interests' | 'public_task' | 'legitimate_interests'
  legal_basis_details?: string
  data_categories: string[]
  purposes: string[]
  third_parties: string[]
  valid_from: string
  valid_until?: string
  is_revocable: boolean
  withdrawn_at?: string
  withdrawal_reason?: string
  withdrawal_method?: string
  ip_address?: string
  user_agent?: string
  consent_channel: 'web' | 'mobile' | 'email' | 'phone'
  metadata: Record<string, any>
  created_at: string
  updated_at: string
}

export interface DataSubjectRequest {
  id: string
  request_id: string
  user_id?: string
  request_type: 'access' | 'portability' | 'rectification' | 'erasure' | 'restriction' | 'objection'
  request_details?: string
  data_scope: string[]
  status: 'pending' | 'processing' | 'awaiting_verification' | 'completed' | 'denied' | 'withdrawn'
  assigned_to?: string
  started_processing_at?: string
  completed_at?: string
  processing_days?: number
  response_data?: Record<string, any>
  response_format: 'json' | 'csv' | 'pdf' | 'xml'
  response_method: 'download' | 'email' | 'secure_link' | 'postal'
  verification_method: 'email' | 'sms' | 'id_document' | 'video_call' | 'in_person'
  verification_token?: string
  verified_at?: string
  ip_address?: string
  user_agent?: string
  notes?: string
  metadata: Record<string, any>
  created_at: string
  updated_at: string
}

export interface DataRetentionPolicy {
  id: string
  name: string
  description?: string
  data_category: string
  retention_period: string
  retention_reason: string
  legal_basis: 'consent' | 'contract' | 'legal_obligation' | 'vital_interests' | 'public_task' | 'legitimate_interests'
  legal_basis_details?: string
  post_retention_action: 'delete' | 'anonymize' | 'archive' | 'transfer'
  exceptions: Record<string, any>
  is_active: boolean
  is_system: boolean
  created_by?: string
  created_at: string
  updated_at: string
}

export interface DataBreachRecord {
  id: string
  breach_id: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  breach_type: 'unauthorized_access' | 'data_loss' | 'data_destruction' | 'data_alteration' | 'unauthorized_disclosure'
  detected_at: string
  occurred_at: string
  contained_at?: string
  reported_at?: string
  data_categories: string[]
  affected_records: number
  affected_users: number
  potential_consequences: string[]
  likelihood_of_risk: 'unlikely' | 'possible' | 'likely' | 'very_likely'
  severity_of_impact: 'minimal' | 'limited' | 'significant' | 'severe'
  requires_supervisor_notification: boolean
  requires_dpa_notification: boolean
  requires_subject_notification: boolean
  notification_deadline?: string
  immediate_actions: string[]
  containment_measures: string[]
  recovery_measures: string[]
  investigating_team: string[]
  investigation_status: 'ongoing' | 'completed' | 'closed'
  root_cause?: string
  source_ip?: string
  attack_vector?: string
  vulnerabilities_exploited: string[]
  notes?: string
  metadata: Record<string, any>
  created_at: string
  updated_at: string
}

export interface DataProcessingRecord {
  id: string
  record_id: string
  processing_activity: string
  data_categories: string[]
  data_subjects: string[]
  legal_basis: 'consent' | 'contract' | 'legal_obligation' | 'vital_interests' | 'public_task' | 'legitimate_interests'
  legal_basis_description?: string
  processing_purposes: string[]
  legitimate_interests: string[]
  recipients: string[]
  international_transfers: boolean
  transfer_countries: string[]
  retention_period?: string
  retention_schedule?: string
  security_measures: string[]
  processing_system: string
  automated: boolean
  created_at: string
  updated_at: string
}

export interface CookieConsentRecord {
  id: string
  consent_id: string
  user_id?: string
  session_id?: string
  consent_given: boolean
  consent_version: string
  necessary_cookies: boolean
  functional_cookies: boolean
  analytics_cookies: boolean
  marketing_cookies: boolean
  third_party_cookies: boolean
  ip_address?: string
  user_agent?: string
  consent_method: 'click' | 'scroll' | 'form_submit'
  granted_at: string
  withdrawn_at?: string
  metadata: Record<string, any>
  created_at: string
}

export interface ConsentCheckResult {
  has_consent: boolean
  consent_version?: string
  legal_basis?: string
  valid_until?: string
  is_expired: boolean
}

// GDPR compliance client
export class GDPRComplianceClient {
  private static instance: GDPRComplianceClient
  private client: ReturnType<typeof createClient>

  private constructor() {
    this.client = createClient()
    if (!this.client) {
      throw new Error('Supabase client not available')
    }
  }

  static getInstance(): GDPRComplianceClient {
    if (!GDPRComplianceClient.instance) {
      GDPRComplianceClient.instance = new GDPRComplianceClient()
    }
    return GDPRComplianceClient.instance
  }

  // Record consent
  async recordConsent(
    userId: string,
    consentType: string,
    consentGiven: boolean,
    consentText: string,
    legalBasis: string,
    legalBasisDetails?: string,
    dataCategories: string[] = [],
    purposes: string[] = [],
    thirdParties: string[] = [],
    validUntil?: Date,
    ipAddress?: string,
    userAgent?: string
  ): Promise<string | null> {
    try {
      const { data, error } = await this.client.rpc('record_consent', {
        p_user_id: userId,
        p_consent_type: consentType,
        p_consent_given: consentGiven,
        p_consent_text: consentText,
        p_legal_basis: legalBasis,
        p_legal_basis_details: legalBasisDetails,
        p_data_categories: dataCategories,
        p_purposes: purposes,
        p_third_parties: thirdParties,
        p_valid_until: validUntil?.toISOString(),
        p_ip_address: ipAddress,
        p_user_agent: userAgent
      })

      if (error) {
        throw new Error(`Consent recording failed: ${error.message}`)
      }

      return data
    } catch (error) {
      console.error('Record consent error:', error)
      return null
    }
  }

  // Withdraw consent
  async withdrawConsent(
    userId: string,
    consentType: string,
    withdrawalReason?: string,
    withdrawalMethod: string = 'web'
  ): Promise<boolean> {
    try {
      const { data, error } = await this.client.rpc('withdraw_consent', {
        p_user_id: userId,
        p_consent_type: consentType,
        p_withdrawal_reason: withdrawalReason,
        p_withdrawal_method: withdrawalMethod
      })

      if (error) {
        throw new Error(`Consent withdrawal failed: ${error.message}`)
      }

      return !!data
    } catch (error) {
      console.error('Withdraw consent error:', error)
      return false
    }
  }

  // Check consent
  async checkConsent(
    userId: string,
    consentType: string,
    dataCategories?: string[],
    purposes?: string[]
  ): Promise<ConsentCheckResult | null> {
    try {
      const { data, error } = await this.client.rpc('check_consent', {
        p_user_id: userId,
        p_consent_type: consentType,
        p_data_categories: dataCategories,
        p_purposes: purposes
      })

      if (error) {
        throw new Error(`Consent check failed: ${error.message}`)
      }

      return data?.[0] || null
    } catch (error) {
      console.error('Check consent error:', error)
      return null
    }
  }

  // Create data subject request
  async createDSAR(
    userId: string,
    requestType: string,
    requestDetails?: string,
    dataScope: string[] = [],
    responseFormat: string = 'json',
    responseMethod: string = 'download'
  ): Promise<string | null> {
    try {
      const { data, error } = await this.client.rpc('create_dsar', {
        p_user_id: userId,
        p_request_type: requestType,
        p_request_details: requestDetails,
        p_data_scope: dataScope,
        p_response_format: responseFormat,
        p_response_method: responseMethod
      })

      if (error) {
        throw new Error(`DSAR creation failed: ${error.message}`)
      }

      return data
    } catch (error) {
      console.error('Create DSAR error:', error)
      return null
    }
  }

  // Get data subject requests
  async getDSARs(
    filters: {
      request_type?: string
      status?: string
      start_date?: string
      end_date?: string
    } = {},
    limit: number = 50
  ): Promise<DataSubjectRequest[]> {
    try {
      let query = this.client
        .from('data_subject_requests')
        .select('*')
        .order('created_at', { ascending: false })

      // Apply filters
      if (filters.request_type) {
        query = query.eq('request_type', filters.request_type)
      }
      if (filters.status) {
        query = query.eq('status', filters.status)
      }
      if (filters.start_date) {
        query = query.gte('created_at', filters.start_date)
      }
      if (filters.end_date) {
        query = query.lte('created_at', filters.end_date)
      }

      const { data, error } = await query.limit(limit)

      if (error) {
        throw error
      }

      return data || []
    } catch (error) {
      console.error('Get DSARs error:', error)
      return []
    }
  }

  // Anonymize user data
  async anonymizeUserData(
    userId: string,
    anonymizationReason: string,
    preserveData: Record<string, any> = {}
  ): Promise<string | null> {
    try {
      const { data, error } = await this.client.rpc('anonymize_user_data', {
        p_user_id: userId,
        p_anonymization_reason: anonymizationReason,
        p_preserve_data: preserveData
      })

      if (error) {
        throw new Error(`User anonymization failed: ${error.message}`)
      }

      return data
    } catch (error) {
      console.error('Anonymize user data error:', error)
      return null
    }
  }

  // Get user consents
  async getUserConsents(
    userId: string,
    consentType?: string
  ): Promise<DataSubjectConsent[]> {
    try {
      let query = this.client
        .from('data_subject_consents')
        .select('*')
        .eq('user_id', userId)
        .order('valid_from', { ascending: false })

      if (consentType) {
        query = query.eq('consent_type', consentType)
      }

      const { data, error } = await query

      if (error) {
        throw error
      }

      return data || []
    } catch (error) {
      console.error('Get user consents error:', error)
      return []
    }
  }

  // Get data retention policies
  async getRetentionPolicies(
    filters: {
      data_category?: string
      is_active?: boolean
    } = {}
  ): Promise<DataRetentionPolicy[]> {
    try {
      let query = this.client
        .from('data_retention_policies')
        .select('*')
        .order('name')

      if (filters.data_category) {
        query = query.eq('data_category', filters.data_category)
      }
      if (filters.is_active !== undefined) {
        query = query.eq('is_active', filters.is_active)
      }

      const { data, error } = await query

      if (error) {
        throw error
      }

      return data || []
    } catch (error) {
      console.error('Get retention policies error:', error)
      return []
    }
  }

  // Record data breach
  async recordDataBreach(
    severity: string,
    breachType: string,
    detectedAt: Date,
    occurredAt: Date,
    dataCategories: string[],
    affectedRecords: number = 0,
    affectedUsers: number = 0,
    description?: string,
    potentialConsequences: string[] = [],
    likelihoodOfRisk: string = 'possible',
    severityOfImpact: string = 'limited',
    sourceIp?: string,
    attackVector?: string
  ): Promise<string | null> {
    try {
      const { data, error } = await this.client.rpc('record_data_breach', {
        p_severity: severity,
        p_breach_type: breachType,
        p_detected_at: detectedAt.toISOString(),
        p_occurred_at: occurredAt.toISOString(),
        p_data_categories: dataCategories,
        p_affected_records: affectedRecords,
        p_affected_users: affectedUsers,
        p_description: description,
        p_potential_consequences: potentialConsequences,
        p_likelihood_of_risk: likelihoodOfRisk,
        p_severity_of_impact: severityOfImpact,
        p_source_ip: sourceIp,
        p_attack_vector: attackVector
      })

      if (error) {
        throw new Error(`Data breach recording failed: ${error.message}`)
      }

      return data
    } catch (error) {
      console.error('Record data breach error:', error)
      return null
    }
  }

  // Get data breach records
  async getBreachRecords(
    filters: {
      severity?: string
      breach_type?: string
      status?: string
      start_date?: string
      end_date?: string
    } = {},
    limit: number = 50
  ): Promise<DataBreachRecord[]> {
    try {
      let query = this.client
        .from('data_breach_records')
        .select('*')
        .order('detected_at', { ascending: false })

      // Apply filters
      if (filters.severity) {
        query = query.eq('severity', filters.severity)
      }
      if (filters.breach_type) {
        query = query.eq('breach_type', filters.breach_type)
      }
      if (filters.status) {
        query = query.eq('investigation_status', filters.status)
      }
      if (filters.start_date) {
        query = query.gte('detected_at', filters.start_date)
      }
      if (filters.end_date) {
        query = query.lte('detected_at', filters.end_date)
      }

      const { data, error } = await query.limit(limit)

      if (error) {
        throw error
      }

      return data || []
    } catch (error) {
      console.error('Get breach records error:', error)
      return []
    }
  }

  // Record cookie consent
  async recordCookieConsent(
    userId?: string,
    sessionId?: string,
    consentGiven: boolean,
    necessaryCookies: boolean = true,
    functionalCookies: boolean = false,
    analyticsCookies: boolean = false,
    marketingCookies: boolean = false,
    thirdPartyCookies: boolean = false,
    ipAddress?: string,
    userAgent?: string,
    consentMethod: string = 'click'
  ): Promise<string | null> {
    try {
      const { data, error } = await this.client
        .from('cookie_consent_records')
        .insert({
          user_id: userId,
          session_id: sessionId,
          consent_given: consentGiven,
          necessary_cookies: necessaryCookies,
          functional_cookies: functionalCookies,
          analytics_cookies: analyticsCookies,
          marketing_cookies: marketingCookies,
          third_party_cookies: thirdPartyCookies,
          ip_address: ipAddress,
          user_agent: userAgent,
          consent_method: consentMethod
        })
        .select('consent_id')
        .single()

      if (error) {
        throw new Error(`Cookie consent recording failed: ${error.message}`)
      }

      return data?.consent_id || null
    } catch (error) {
      console.error('Record cookie consent error:', error)
      return null
    }
  }

  // Get cookie consent
  async getCookieConsent(
    userId?: string,
    sessionId?: string
  ): Promise<CookieConsentRecord | null> {
    try {
      let query = this.client
        .from('cookie_consent_records')
        .select('*')
        .order('granted_at', { ascending: false })

      if (userId) {
        query = query.eq('user_id', userId)
      }
      if (sessionId) {
        query = query.eq('session_id', sessionId)
      }

      const { data, error } = await query.limit(1)

      if (error) {
        throw error
      }

      return data || null
    } catch (error) {
      console.error('Get cookie consent error:', error)
      return null
    }
  }
}

// GDPR compliance utilities
export class GDPRUtils {
  // Generate consent text
  static generateConsentText(
    consentType: string,
    dataCategories: string[],
    purposes: string[],
    thirdParties: string[] = []
  ): string {
    const categoryDescriptions: Record<string, string> = {
      'personal_data': 'Personal information such as name, email, and contact details',
      'profile_data': 'User profile information and preferences',
      'usage_data': 'How you use our services and features',
      'device_data': 'Information about your device and browser',
      'location_data': 'Geographic location information',
      'communication_data': 'Messages and communications',
      'financial_data': 'Payment and financial information'
    }

    const purposeDescriptions: Record<string, string> = {
      'service_provision': 'To provide and maintain our services',
      'analytics': 'To analyze and improve our services',
      'marketing': 'To send you promotional content',
      'personalization': 'To personalize your experience',
      'security': 'To protect against fraud and abuse',
      'legal_compliance': 'To comply with legal obligations'
    }

    let text = `We collect and process your ${dataCategories.map(cat => categoryDescriptions[cat] || cat).join(', ')} for the following purposes: ${purposes.map(purpose => purposeDescriptions[purpose] || purpose).join(', ')}.`

    if (thirdParties.length > 0) {
      text += ` Your data may be shared with the following third parties: ${thirdParties.join(', ')}.`
    }

    text += ` You have the right to withdraw your consent at any time. This consent is valid until you withdraw it or the specified retention period expires.`

    return text
  }

  // Check if consent is required
  static isConsentRequired(
    dataCategories: string[],
    legalBasis: string
  ): boolean {
    // Consent is required for most personal data processing unless there's another legal basis
    const personalDataCategories = ['personal_data', 'profile_data', 'communication_data', 'financial_data']
    const hasPersonalData = dataCategories.some(cat => personalDataCategories.includes(cat))

    return hasPersonalData && legalBasis === 'consent'
  }

  // Calculate data retention period
  static calculateRetentionDate(
    retentionPeriod: string,
    fromDate: Date = new Date()
  ): Date {
    const period = retentionPeriod.toLowerCase()
    const value = parseInt(retentionPeriod.match(/\d+/)?.[0] || '0')
    
    switch (period) {
      case 'days':
        return new Date(fromDate.getTime() + value * 24 * 60 * 60 * 1000)
      case 'months':
        return new Date(fromDate.getFullYear(), fromDate.getMonth() + value, fromDate.getDate())
      case 'years':
        return new Date(fromDate.getFullYear() + value, fromDate.getMonth(), fromDate.getDate())
      default:
        return new Date(fromDate.getTime() + 30 * 24 * 60 * 60 * 1000) // Default to 30 days
    }
  }

  // Check if breach notification is required
  static isBreachNotificationRequired(
    severity: string,
    affectedUsers: number,
    dataCategories: string[]
  ): {
    required: boolean
    deadline: Date
    authorities: string[]
    subjects: boolean
  } {
    const personalDataCategories = ['personal_data', 'profile_data', 'communication_data', 'financial_data']
    const hasPersonalData = dataCategories.some(cat => personalDataCategories.includes(cat))

    let required = false
    let deadline = new Date()
    let authorities: string[] = []
    let subjects = false

    // GDPR notification requirements
    if (severity === 'critical' || severity === 'high') {
      required = true
      deadline = new Date(Date.now() + 72 * 60 * 60 * 1000) // 72 hours
      authorities = ['supervisory_authority']
    }

    if (affectedUsers > 0 && hasPersonalData) {
      subjects = true
    }

    return { required, deadline, authorities, subjects }
  }

  // Generate data export format
  static generateDataExport(
    userData: Record<string, any>,
    format: 'json' | 'csv' | 'pdf' | 'xml' = 'json'
  ): string | Blob {
    switch (format) {
      case 'json':
        return JSON.stringify(userData, null, 2)
      case 'csv':
        return this.generateCSV(userData)
      case 'pdf':
        return this.generatePDF(userData)
      case 'xml':
        return this.generateXML(userData)
      default:
        return JSON.stringify(userData, null, 2)
    }
  }

  private static generateCSV(data: Record<string, any>): string {
    const headers = Object.keys(data)
    const row = Object.values(data)
    
    const csvContent = [
      headers.join(','),
      row.map(cell => `"${cell}"`).join(',')
    ].join('\n')
    
    return csvContent
  }

  private static generatePDF(data: Record<string, any>): Blob {
    // Simplified PDF generation - in production, use a proper PDF library
    const pdfContent = `%PDF-1.4
1 0 obj
<< /Length ${data.toString().length} /Filter /FlateDecode
>>
stream
xS
100 500
BT
/F1 12 Tf
/F2 12 Tf
72 720 Td
(Data Subject Access Request)
ET
/F1 12 Tf
/F2 12 Tf
72 740 Td
(Generated on ${new Date().toISOString()})
ET
/F1 12 Tf
/F2 12 Tf
72 760 Td
(Your Data)
ET
/F1 12 Tf/F2 12 Tf
72 780 Td
${data.toString()}
ET
endstream
endobj`

    return new Blob([pdfContent], { type: 'application/pdf' })
  }

  private static generateXML(data: Record<string, any>): string {
    const xmlContent = `<?xml version="1.0" encoding="UTF-8"?>
<gdpr_data_export>
  <user_id>${data.id || ''}</user_id>
  <email>${data.email || ''}</email>
  <full_name>${data.full_name || ''}</full_name>
  <created_at>${data.created_at || ''}</created_at>
  <updated_at>${data.updated_at || ''}</updated_at>
  <data>
${Object.entries(data).map(([key, value]) => `    <${key}>${value}</${key}>`).join('\n')}
  </data>
</gdpr_export>`

    return xmlContent
  }

  // Validate GDPR compliance
  static validateCompliance(
    dataProcessing: Record<string, any>
  ): {
    compliant: boolean
    issues: string[]
    recommendations: string[]
  } {
    const issues: string[] = []
    const recommendations: string[] = []

    // Check for required fields
    if (!dataProcessing.legal_basis) {
      issues.push('Legal basis not specified')
      recommendations.push('Specify the legal basis for data processing')
    }

    if (!dataProcessing.data_categories || dataProcessing.data_categories.length === 0) {
      issues.push('Data categories not specified')
      recommendations.push('Specify the categories of data being processed')
    }

    if (!dataProcessing.purposes || dataProcessing.purposes.length === 0) {
      issues.push('Processing purposes not specified')
      recommendations.push('Specify the purposes for data processing')
    }

    // Check for consent if required
    if (this.isConsentRequired(dataProcessing.data_categories || [], dataProcessing.legal_basis)) {
      if (!dataProcessing.consent) {
        issues.push('Consent not obtained when required')
        recommendations.push('Obtain explicit consent from data subjects')
      }
    }

    // Check for retention policy
    if (!dataProcessing.retention_period) {
      issues.push('Retention period not specified')
      recommendations.push('Specify how long data will be retained')
    }

    // Check for security measures
    if (!dataProcessing.security_measures || dataProcessing.security_measures.length === 0) {
      issues.push('Security measures not specified')
      recommendations.push('Describe the security measures in place')
    }

    return {
      compliant: issues.length === 0,
      issues,
      recommendations
    }
  }
}

// Cookie consent management
export class CookieConsentManager {
  private static instance: CookieConsentManager
  private gdprClient: GDPRComplianceClient

  private constructor() {
    this.gdprClient = GDPRComplianceClient.getInstance()
  }

  static getInstance(): CookieConsentManager {
    if (!CookieConsentManager.instance) {
      CookieConsentManager.instance = new CookieConsentManager()
    }
    return CookieConsentManager.instance
  }

  // Show cookie consent banner
  showConsentBanner(): void {
    // Implementation would depend on your UI framework
    console.log('Cookie consent banner should be shown')
  }

  // Hide cookie consent banner
  hideConsentBanner(): void {
    // Implementation would depend on your UI framework
    console.log('Cookie consent banner should be hidden')
  }

  // Check cookie consent
  async checkCookieConsent(
    userId?: string,
    sessionId?: string
  ): Promise<{
      necessary: boolean
      functional: boolean
      analytics: boolean
      marketing: boolean
      thirdParty: boolean
    }> {
    const consent = await this.gdprClient.getCookieConsent(userId, sessionId)
    
    if (!consent) {
      return {
        necessary: false,
        functional: false,
        analytics: false,
        marketing: false,
        thirdParty: false
      }
    }

    return {
      necessary: consent.necessary_cookies,
      functional: consent.functional_cookies,
      analytics: consent.analytics_cookies,
      marketing: consent.marketing_cookies,
      thirdParty: consent.third_party_cookies
    }
  }

  // Update cookie preferences
  async updateCookiePreferences(
    preferences: {
      necessary: boolean
      functional: boolean
      analytics: boolean
      marketing: boolean
      thirdParty: boolean
    },
    userId?: string,
    sessionId?: string
  ): Promise<void> {
    await this.gdprClient.recordCookieConsent(
      userId,
      sessionId,
      true, // consent given
      preferences.necessary,
      preferences.functional,
      preferences.analytics,
      preferences.marketing,
      preferences.thirdParty
    )
  }

  // Withdraw cookie consent
  async withdrawCookieConsent(
    userId?: string,
    sessionId?: string
  ): Promise<void> {
    const consent = await this.gdprClient.getCookieConsent(userId, sessionId)
    
    if (consent && consent.user_id) {
      await this.gdprClient.withdrawConsent(
        consent.user_id,
        'cookies',
        'User withdrew cookie consent'
      )
    }
  }
}

// Export singleton instances
export const gdprClient = GDPRComplianceClient.getInstance()
export const cookieConsentManager = CookieConsentManager.getInstance()
