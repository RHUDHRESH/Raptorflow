import { createClient } from '@/lib/auth-client'

// IP access types
export interface IPAccessPolicy {
  id: string
  name: string
  description?: string
  policy_type: 'whitelist' | 'blacklist' | 'geofence' | 'rate_limit'
  priority: number
  target_type: 'global' | 'user' | 'role' | 'workspace' | 'client'
  target_id?: string
  target_role?: string
  ip_ranges: string[]
  ip_networks: string[]
  ip_countries: string[]
  action: 'allow' | 'deny' | 'challenge' | 'rate_limit'
  requests_per_minute?: number
  requests_per_hour?: number
  requests_per_day?: number
  allowed_countries?: string[]
  blocked_countries?: string[]
  allow_unknown_countries?: boolean
  time_restrictions: Record<string, any>
  is_active: boolean
  is_system: boolean
  created_by?: string
  created_at: string
  updated_at: string
}

export interface IPAccessLog {
  id: string
  ip_address: string
  user_id?: string
  session_id?: string
  request_path?: string
  request_method?: string
  user_agent?: string
  country_code?: string
  country_name?: string
  city?: string
  region?: string
  latitude?: number
  longitude?: number
  asn?: number
  organization?: string
  policy_id?: string
  policy_action?: string
  policy_name?: string
  access_granted: boolean
  denial_reason?: string
  challenge_required: boolean
  challenge_type?: string
  request_time: string
  response_time_ms?: number
  metadata: Record<string, any>
}

export interface IPReputation {
  id: string
  ip_address: string
  ip_range?: string
  reputation_score: number
  risk_level: 'low' | 'medium' | 'high' | 'critical'
  ip_type: 'residential' | 'business' | 'datacenter' | 'mobile' | 'vpn' | 'proxy' | 'tor' | 'malicious'
  country_code?: string
  country_name?: string
  city?: string
  region?: string
  asn?: number
  organization?: string
  isp?: string
  is_known_attacker: boolean
  is_known_scanner: boolean
  is_tor_exit_node: boolean
  is_vpn: boolean
  is_proxy: boolean
  is_datacenter: boolean
  first_seen: string
  last_seen: string
  request_count: number
  blocked_requests: number
  factors: Record<string, any>
  source?: string
  updated_at: string
  created_at: string
}

export interface IPAccessChallenge {
  id: string
  challenge_id: string
  ip_address: string
  user_id?: string
  session_id?: string
  challenge_type: 'captcha' | 'email' | 'sms' | 'mfa' | 'device_verification'
  challenge_data: Record<string, any>
  status: 'pending' | 'passed' | 'failed' | 'expired'
  created_at: string
  expires_at: string
  completed_at?: string
  attempts: number
  max_attempts: number
  request_path?: string
  user_agent?: string
}

export interface IPAccessEvaluation {
  access_granted: boolean
  action: string
  policy_id?: string
  policy_name?: string
  denial_reason?: string
  challenge_required: boolean
  challenge_type?: string
  reputation_score: number
  risk_level: string
}

// IP access control client
export class IPAccessControl {
  private static instance: IPAccessControl
  private client: ReturnType<typeof createClient>
  private currentIP: string | null = null
  private accessEvaluation: IPAccessEvaluation | null = null

  private constructor() {
    this.client = createClient()
    if (!this.client) {
      throw new Error('Supabase client not available')
    }
  }

  static getInstance(): IPAccessControl {
    if (!IPAccessControl.instance) {
      IPAccessControl.instance = new IPAccessControl()
    }
    return IPAccessControl.instance
  }

  // Get current client IP
  async getCurrentIP(): Promise<string> {
    if (this.currentIP) {
      return this.currentIP
    }

    try {
      // Use a service to get client IP
      const response = await fetch('https://api.ipify.org?format=json')
      const data = await response.json()
      this.currentIP = data.ip
      return this.currentIP
    } catch (error) {
      console.error('Failed to get client IP:', error)
      // Fallback to a default IP for development
      this.currentIP = '127.0.0.1'
      return this.currentIP
    }
  }

  // Evaluate IP access
  async evaluateAccess(
    requestPath?: string,
    userAgent?: string,
    sessionId?: string
  ): Promise<IPAccessEvaluation> {
    const ipAddress = await this.getCurrentIP()
    
    try {
      const { data: { user } } = await this.client.auth.getUser()
      const userId = user?.id

      const { data, error } = await this.client.rpc('evaluate_ip_access', {
        p_ip_address: ipAddress,
        p_user_id: userId,
        p_request_path: requestPath,
        p_user_agent: userAgent,
        p_session_id: sessionId
      })

      if (error) {
        throw new Error(`IP access evaluation failed: ${error.message}`)
      }

      this.accessEvaluation = data?.[0] || {
        access_granted: true,
        action: 'allow',
        reputation_score: 0.5,
        risk_level: 'medium'
      }

      return this.accessEvaluation
    } catch (error) {
      console.error('IP access evaluation error:', error)
      // Fallback to allow access on error
      return {
        access_granted: true,
        action: 'allow',
        reputation_score: 0.5,
        risk_level: 'medium'
      }
    }
  }

  // Log IP access
  async logAccess(
    accessGranted: boolean,
    denialReason?: string,
    challengeRequired?: boolean,
    challengeType?: string,
    responseTimeMs?: number,
    metadata: Record<string, any> = {}
  ): Promise<string | null> {
    const ipAddress = await this.getCurrentIP()
    
    try {
      const { data: { user } } = await this.client.auth.getUser()
      const userId = user?.id

      const { data, error } = await this.client.rpc('log_ip_access', {
        p_ip_address: ipAddress,
        p_user_id: userId,
        p_access_granted: accessGranted,
        p_denial_reason: denialReason,
        p_challenge_required: challengeRequired,
        p_challenge_type: challengeType,
        p_response_time_ms: responseTimeMs,
        p_metadata: metadata
      })

      if (error) {
        console.error('IP access logging error:', error)
        return null
      }

      return data
    } catch (error) {
      console.error('IP access logging error:', error)
      return null
    }
  }

  // Create access challenge
  async createChallenge(
    challengeType: string,
    requestPath?: string
  ): Promise<string | null> {
    const ipAddress = await this.getCurrentIP()
    
    try {
      const { data: { user } } = await this.client.auth.getUser()
      const userId = user?.id

      const { data, error } = await this.client.rpc('create_ip_challenge', {
        p_ip_address: ipAddress,
        p_user_id: userId,
        p_challenge_type: challengeType,
        p_request_path: requestPath
      })

      if (error) {
        throw new Error(`Challenge creation failed: ${error.message}`)
      }

      return data
    } catch (error) {
      console.error('Challenge creation error:', error)
      return null
    }
  }

  // Verify challenge
  async verifyChallenge(challengeId: string, response: string): Promise<boolean> {
    try {
      const { data, error } = await this.client.rpc('verify_ip_challenge', {
        p_challenge_id: challengeId,
        p_response: response
      })

      if (error) {
        throw new Error(`Challenge verification failed: ${error.message}`)
      }

      return !!data
    } catch (error) {
      console.error('Challenge verification error:', error)
      return false
    }
  }

  // Get IP reputation
  async getIPReputation(ipAddress?: string): Promise<IPReputation | null> {
    const ip = ipAddress || await this.getCurrentIP()
    
    try {
      const { data, error } = await this.client
        .from('ip_reputation')
        .select('*')
        .eq('ip_address', ip)
        .single()

      if (error) {
        if (error.code === 'PGRST116') {
          // No reputation record found
          return null
        }
        throw error
      }

      return data
    } catch (error) {
      console.error('Get IP reputation error:', error)
      return null
    }
  }

  // Update IP reputation
  async updateIPReputation(
    ipAddress: string,
    reputationScore: number,
    riskLevel: string,
    ipType: string,
    factors: Record<string, any> = {}
  ): Promise<boolean> {
    try {
      const { data, error } = await this.client.rpc('update_ip_reputation', {
        p_ip_address: ipAddress,
        p_reputation_score: reputationScore,
        p_risk_level: riskLevel,
        p_ip_type: ipType,
        p_factors: factors
      })

      if (error) {
        throw new Error(`IP reputation update failed: ${error.message}`)
      }

      return !!data
    } catch (error) {
      console.error('Update IP reputation error:', error)
      return false
    }
  }

  // Get access policies
  async getAccessPolicies(): Promise<IPAccessPolicy[]> {
    try {
      const { data, error } = await this.client
        .from('ip_access_policies')
        .select('*')
        .order('priority', { ascending: true })

      if (error) {
        throw error
      }

      return data || []
    } catch (error) {
      console.error('Get access policies error:', error)
      return []
    }
  }

  // Get access logs
  async getAccessLogs(
    limit: number = 100,
    offset: number = 0,
    filters: {
      ip_address?: string
      user_id?: string
      access_granted?: boolean
      start_date?: string
      end_date?: string
    } = {}
  ): Promise<IPAccessLog[]> {
    try {
      let query = this.client
        .from('ip_access_logs')
        .select('*')
        .order('request_time', { ascending: false })

      // Apply filters
      if (filters.ip_address) {
        query = query.eq('ip_address', filters.ip_address)
      }
      if (filters.user_id) {
        query = query.eq('user_id', filters.user_id)
      }
      if (filters.access_granted !== undefined) {
        query = query.eq('access_granted', filters.access_granted)
      }
      if (filters.start_date) {
        query = query.gte('request_time', filters.start_date)
      }
      if (filters.end_date) {
        query = query.lte('request_time', filters.end_date)
      }

      const { data, error } = await query.range(offset, offset + limit - 1)

      if (error) {
        throw error
      }

      return data || []
    } catch (error) {
      console.error('Get access logs error:', error)
      return []
    }
  }

  // Get current access evaluation
  getCurrentEvaluation(): IPAccessEvaluation | null {
    return this.accessEvaluation
  }

  // Clear cached data
  clearCache(): void {
    this.currentIP = null
    this.accessEvaluation = null
  }
}

// IP geolocation utilities
export class IPGeolocation {
  // Get geolocation data for IP
  static async getGeolocation(ipAddress: string): Promise<{
    country_code?: string
    country_name?: string
    city?: string
    region?: string
    latitude?: number
    longitude?: number
    asn?: number
    organization?: string
    isp?: string
  } | null> {
    try {
      // Use a free geolocation API (in production, use a paid service)
      const response = await fetch(`https://ipapi.co/${ipAddress}/json/`)
      const data = await response.json()

      return {
        country_code: data.country_code,
        country_name: data.country_name,
        city: data.city,
        region: data.region,
        latitude: data.latitude,
        longitude: data.longitude,
        asn: data.asn,
        organization: data.org,
        isp: data.org
      }
    } catch (error) {
      console.error('Geolocation lookup error:', error)
      return null
    }
  }

  // Check if IP is from specific country
  static async isFromCountry(ipAddress: string, countryCode: string): Promise<boolean> {
    const geo = await IPGeolocation.getGeolocation(ipAddress)
    return geo?.country_code === countryCode
  }

  // Check if IP is from EU
  static async isFromEU(ipAddress: string): Promise<boolean> {
    const geo = await IPGeolocation.getGeolocation(ipAddress)
    if (!geo?.country_code) return false

    const euCountries = [
      'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
      'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
      'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
    ]

    return euCountries.includes(geo.country_code)
  }

  // Get timezone for IP
  static async getTimezone(ipAddress: string): Promise<string | null> {
    try {
      const response = await fetch(`http://ip-api.com/json/${ipAddress}`)
      const data = await response.json()
      return data.timezone || null
    } catch (error) {
      console.error('Timezone lookup error:', error)
      return null
    }
  }
}

// IP reputation utilities
export class IPReputationAnalyzer {
  // Analyze IP for suspicious patterns
  static analyzeIP(ipAddress: string, accessLogs: IPAccessLog[]): {
    risk_level: 'low' | 'medium' | 'high' | 'critical'
    reputation_score: number
    factors: Record<string, any>
    recommendations: string[]
  } {
    const factors: Record<string, any> = {}
    const recommendations: string[] = []
    let riskScore = 0

    // Analyze request patterns
    const recentLogs = accessLogs.filter(log => 
      new Date(log.request_time) > new Date(Date.now() - 24 * 60 * 60 * 1000)
    )

    // High request frequency
    if (recentLogs.length > 1000) {
      factors.high_request_frequency = recentLogs.length
      riskScore += 30
      recommendations.push('Consider rate limiting')
    }

    // High failure rate
    const failureRate = recentLogs.filter(log => !log.access_granted).length / recentLogs.length
    if (failureRate > 0.5) {
      factors.high_failure_rate = failureRate
      riskScore += 40
      recommendations.push('Block this IP')
    }

    // Suspicious user agents
    const suspiciousAgents = recentLogs.filter(log => 
      log.user_agent?.includes('bot') || 
      log.user_agent?.includes('scanner') ||
      log.user_agent?.includes('crawler')
    )
    if (suspiciousAgents.length > 0) {
      factors.suspicious_user_agent = suspiciousAgents.length
      riskScore += 20
      recommendations.push('Require CAPTCHA')
    }

    // Multiple user accounts
    const uniqueUsers = new Set(recentLogs.map(log => log.user_id).filter(Boolean))
    if (uniqueUsers.size > 10) {
      factors.multiple_user_accounts = uniqueUsers.size
      riskScore += 25
      recommendations.push('Monitor for account takeover')
    }

    // Determine risk level
    let riskLevel: 'low' | 'medium' | 'high' | 'critical'
    if (riskScore >= 80) {
      riskLevel = 'critical'
    } else if (riskScore >= 60) {
      riskLevel = 'high'
    } else if (riskScore >= 30) {
      riskLevel = 'medium'
    } else {
      riskLevel = 'low'
    }

    // Calculate reputation score (inverse of risk)
    const reputationScore = Math.max(0, Math.min(1, (100 - riskScore) / 100))

    return {
      risk_level: riskLevel,
      reputation_score: reputationScore,
      factors,
      recommendations
    }
  }

  // Check if IP is from datacenter
  static async isDatacenter(ipAddress: string): Promise<boolean> {
    try {
      // Use a service to check if IP is from datacenter
      const response = await fetch(`https://ipinfo.io/${ipAddress}/json`)
      const data = await response.json()
      
      return data.org?.toLowerCase().includes('datacenter') ||
             data.org?.toLowerCase().includes('hosting') ||
             data.org?.toLowerCase().includes('cloud') ||
             data.org?.toLowerCase().includes('server')
    } catch (error) {
      console.error('Datacenter check error:', error)
      return false
    }
  }

  // Check if IP is from VPN
  static async isVPN(ipAddress: string): Promise<boolean> {
    try {
      const response = await fetch(`https://ipinfo.io/${ipAddress}/json`)
      const data = await response.json()
      
      return data.org?.toLowerCase().includes('vpn') ||
             data.org?.toLowerCase().includes('private') ||
             data.org?.toLowerCase().includes('anonymous')
    } catch (error) {
      console.error('VPN check error:', error)
      return false
    }
  }

  // Check if IP is Tor exit node
  static async isTorExitNode(ipAddress: string): Promise<boolean> {
    try {
      const response = await fetch(`https://check.torproject.org/cgi-bin/TorBulkExitList.py?ip=${ipAddress}`)
      const data = await response.text()
      return data.includes(ipAddress)
    } catch (error) {
      console.error('Tor check error:', error)
      return false
    }
  }
}

// IP access middleware helper
export class IPAccessMiddleware {
  private static ipControl = IPAccessControl.getInstance()

  // Middleware function for Next.js
  static async middleware(
    request: Request,
    response: Response,
    next: () => void
  ): Promise<void> {
    const startTime = Date.now()
    const userAgent = request.headers.get('user-agent') || undefined
    const requestPath = new URL(request.url).pathname

    try {
      // Evaluate IP access
      const evaluation = await this.ipControl.evaluateAccess(
        requestPath,
        userAgent
      )

      // Log the access attempt
      const responseTime = Date.now() - startTime
      await this.ipControl.logAccess(
        evaluation.access_granted,
        evaluation.denial_reason,
        evaluation.challenge_required,
        evaluation.challenge_type,
        responseTime,
        {
          method: request.method,
          path: requestPath,
          user_agent: userAgent
        }
      )

      // Handle access denial
      if (!evaluation.access_granted) {
        if (evaluation.challenge_required) {
          // Redirect to challenge page
          const challengeId = await this.ipControl.createChallenge(
            evaluation.challenge_type || 'captcha',
            requestPath
          )
          
          // In a real implementation, redirect to challenge page
          console.log('Challenge required:', challengeId)
        } else {
          // Block access
          throw new Error('Access denied')
        }
      }

      next()
    } catch (error) {
      console.error('IP access middleware error:', error)
      // Allow access on error to prevent service disruption
      next()
    }
  }
}

// Export singleton instance
export const ipAccessControl = IPAccessControl.getInstance()
