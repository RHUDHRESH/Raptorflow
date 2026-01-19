import { createClient } from '@/lib/auth-client'

// Threat detection types
export interface ThreatDetectionRule {
  id: string
  name: string
  description?: string
  rule_type: 'pattern' | 'anomaly' | 'signature' | 'behavioral' | 'reputation'
  category: 'authentication' | 'authorization' | 'data_access' | 'malware' | 'network' | 'social_engineering' | 'insider_threat'
  conditions: Record<string, any>
  thresholds: Record<string, any>
  severity_score: number
  confidence_threshold: number
  auto_response: boolean
  response_actions: string[]
  escalation_rules: Record<string, any>
  ml_model_id?: string
  ml_features: string[]
  training_data: Record<string, any>
  is_active: boolean
  is_system: boolean
  created_by?: string
  created_at: string
  updated_at: string
}

export interface ThreatIncident {
  id: string
  incident_id: string
  title: string
  description?: string
  threat_type: 'brute_force' | 'credential_stuffing' | 'sql_injection' | 'xss' | 'csrf' | 'ddos' | 'malware' | 'phishing' | 'social_engineering' | 'insider_threat' | 'data_exfiltration' | 'account_takeover' | 'unauthorized_access'
  severity: 'low' | 'medium' | 'high' | 'critical'
  status: 'open' | 'investigating' | 'contained' | 'resolved' | 'false_positive'
  target_type: 'user' | 'workspace' | 'system' | 'data' | 'network'
  target_id?: string
  target_details: Record<string, any>
  source_ip?: string
  source_user_id?: string
  source_device_fingerprint?: string
  source_location: Record<string, any>
  detection_rule_id?: string
  detection_method: string
  confidence_score: number
  evidence: Record<string, any>
  first_detected_at: string
  last_activity_at: string
  duration_minutes?: number
  affected_users: number
  affected_systems: string[]
  data_exposed: boolean
  data_exfiltrated: boolean
  financial_impact: number
  response_actions: string[]
  auto_response_taken: boolean
  containment_measures: string[]
  assigned_to?: string
  investigation_notes?: string
  resolution_details?: string
  metadata: Record<string, any>
  created_at: string
  updated_at: string
}

export interface ThreatIndicator {
  id: string
  indicator_id: string
  indicator_type: 'ip' | 'domain' | 'url' | 'hash' | 'email' | 'user_agent' | 'pattern' | 'signature'
  value: string
  category: 'malicious' | 'suspicious' | 'benign' | 'unknown'
  threat_types: string[]
  source: string
  confidence: number
  first_seen: string
  last_seen: string
  context: Record<string, any>
  tags: string[]
  is_active: boolean
  false_positive_count: number
  created_at: string
  updated_at: string
}

export interface BehavioralBaseline {
  id: string
  entity_type: 'user' | 'ip' | 'device' | 'session'
  entity_id: string
  metrics: Record<string, any>
  patterns: Record<string, any>
  mean_values: Record<string, any>
  standard_deviations: Record<string, any>
  percentiles: Record<string, any>
  sample_size: number
  training_period_days: number
  last_trained_at?: string
  model_version: string
  model_accuracy?: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AnomalyDetection {
  id: string
  detection_id: string
  entity_type: string
  entity_id: string
  baseline_id?: string
  anomaly_type: string
  anomaly_score: number
  confidence: number
  observed_values: Record<string, any>
  expected_values: Record<string, any>
  deviation_magnitude: number
  context: Record<string, any>
  related_indicators: string[]
  detected_at: string
  duration_minutes?: number
  status: 'detected' | 'investigating' | 'confirmed' | 'false_positive' | 'resolved'
  incident_id?: string
  metadata: Record<string, any>
  created_at: string
}

export interface ThreatDetectionResult {
  threat_detected: boolean
  threat_type?: string
  severity?: string
  confidence: number
  rule_id?: string
  rule_name?: string
  indicators: Record<string, any>
  recommendations: string[]
}

// Threat detection client
export class ThreatDetectionClient {
  private static instance: ThreatDetectionClient
  private client: ReturnType<typeof createClient>

  private constructor() {
    this.client = createClient()
    if (!this.client) {
      throw new Error('Supabase client not available')
    }
  }

  static getInstance(): ThreatDetectionClient {
    if (!ThreatDetectionClient.instance) {
      ThreatDetectionClient.instance = new ThreatDetectionClient()
    }
    return ThreatDetectionClient.instance
  }

  // Detect threats for entity
  async detectThreats(
    entityType: string,
    entityId: string,
    eventData: Record<string, any>,
    context: Record<string, any> = {}
  ): Promise<ThreatDetectionResult[]> {
    try {
      const { data, error } = await this.client.rpc('detect_threats', {
        p_entity_type: entityType,
        p_entity_id: entityId,
        p_event_data: eventData,
        p_context: context
      })

      if (error) {
        throw new Error(`Threat detection failed: ${error.message}`)
      }

      return data || []
    } catch (error) {
      console.error('Threat detection error:', error)
      return []
    }
  }

  // Create threat incident
  async createIncident(
    threatType: string,
    severity: string,
    targetType: string,
    targetId?: string,
    sourceIp?: string,
    sourceUserId?: string,
    detectionRuleId?: string,
    confidence: number,
    evidence: Record<string, any> = {},
    title?: string,
    description?: string
  ): Promise<string | null> {
    try {
      const { data, error } = await this.client.rpc('create_threat_incident', {
        p_threat_type: threatType,
        p_severity: severity,
        p_target_type: targetType,
        p_target_id: targetId,
        p_source_ip: sourceIp,
        p_source_user_id: sourceUserId,
        p_detection_rule_id: detectionRuleId,
        p_confidence: confidence,
        p_evidence: evidence,
        p_title: title,
        p_description: description
      })

      if (error) {
        throw new Error(`Incident creation failed: ${error.message}`)
      }

      return data
    } catch (error) {
      console.error('Incident creation error:', error)
      return null
    }
  }

  // Get threat incidents
  async getIncidents(
    filters: {
      threat_type?: string
      severity?: string
      status?: string
      start_date?: string
      end_date?: string
      assigned_to?: string
    } = {},
    limit: number = 50,
    offset: number = 0
  ): Promise<ThreatIncident[]> {
    try {
      let query = this.client
        .from('threat_incidents')
        .select('*')
        .order('first_detected_at', { ascending: false })

      // Apply filters
      if (filters.threat_type) {
        query = query.eq('threat_type', filters.threat_type)
      }
      if (filters.severity) {
        query = query.eq('severity', filters.severity)
      }
      if (filters.status) {
        query = query.eq('status', filters.status)
      }
      if (filters.assigned_to) {
        query = query.eq('assigned_to', filters.assigned_to)
      }
      if (filters.start_date) {
        query = query.gte('first_detected_at', filters.start_date)
      }
      if (filters.end_date) {
        query = query.lte('first_detected_at', filters.end_date)
      }

      const { data, error } = await query.range(offset, offset + limit - 1)

      if (error) {
        throw error
      }

      return data || []
    } catch (error) {
      console.error('Get incidents error:', error)
      return []
    }
  }

  // Update behavioral baseline
  async updateBaseline(
    entityType: string,
    entityId: string,
    metrics: Record<string, any>,
    patterns: Record<string, any> = {}
  ): Promise<boolean> {
    try {
      const { data, error } = await this.client.rpc('update_behavioral_baseline', {
        p_entity_type: entityType,
        p_entity_id: entityId,
        p_metrics: metrics,
        p_patterns: patterns
      })

      if (error) {
        throw new Error(`Baseline update failed: ${error.message}`)
      }

      return !!data
    } catch (error) {
      console.error('Baseline update error:', error)
      return false
    }
  }

  // Get behavioral baselines
  async getBaselines(
    entityType?: string,
    entityId?: string
  ): Promise<BehavioralBaseline[]> {
    try {
      let query = this.client
        .from('behavioral_baselines')
        .select('*')
        .eq('is_active', true)

      if (entityType) {
        query = query.eq('entity_type', entityType)
      }
      if (entityId) {
        query = query.eq('entity_id', entityId)
      }

      const { data, error } = await query

      if (error) {
        throw error
      }

      return data || []
    } catch (error) {
      console.error('Get baselines error:', error)
      return []
    }
  }

  // Add threat indicator
  async addIndicator(
    indicatorType: string,
    value: string,
    category: string,
    threatTypes: string[],
    source: string,
    confidence: number = 0.5,
    context: Record<string, any> = {},
    tags: string[] = []
  ): Promise<string | null> {
    try {
      const { data, error } = await this.client.rpc('add_threat_indicator', {
        p_indicator_type: indicatorType,
        p_value: value,
        p_category: category,
        p_threat_types: threatTypes,
        p_source: source,
        p_confidence: confidence,
        p_context: context,
        p_tags: tags
      })

      if (error) {
        throw new Error(`Indicator addition failed: ${error.message}`)
      }

      return data
    } catch (error) {
      console.error('Add indicator error:', error)
      return null
    }
  }

  // Check threat indicators
  async checkIndicators(
    indicatorType: string,
    value: string
  ): Promise<{
    is_threat: boolean
    category?: string
    threat_types?: string[]
    confidence?: number
    indicator_id?: string
  }[]> {
    try {
      const { data, error } = await this.client.rpc('check_threat_indicators', {
        p_indicator_type: indicatorType,
        p_value: value
      })

      if (error) {
        throw new Error(`Indicator check failed: ${error.message}`)
      }

      return data || []
    } catch (error) {
      console.error('Check indicators error:', error)
      return []
    }
  }

  // Get threat indicators
  async getIndicators(
    filters: {
      indicator_type?: string
      category?: string
      threat_types?: string[]
      is_active?: boolean
    } = {}
  ): Promise<ThreatIndicator[]> {
    try {
      let query = this.client
        .from('threat_indicators')
        .select('*')
        .order('created_at', { ascending: false })

      // Apply filters
      if (filters.indicator_type) {
        query = query.eq('indicator_type', filters.indicator_type)
      }
      if (filters.category) {
        query = query.eq('category', filters.category)
      }
      if (filters.threat_types && filters.threat_types.length > 0) {
        query = query.contains('threat_types', filters.threat_types)
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
      console.error('Get indicators error:', error)
      return []
    }
  }

  // Get anomaly detections
  async getAnomalies(
    filters: {
      entity_type?: string
      entity_id?: string
      status?: string
      start_date?: string
      end_date?: string
    } = {},
    limit: number = 50
  ): Promise<AnomalyDetection[]> {
    try {
      let query = this.client
        .from('anomaly_detections')
        .select('*')
        .order('detected_at', { ascending: false })

      // Apply filters
      if (filters.entity_type) {
        query = query.eq('entity_type', filters.entity_type)
      }
      if (filters.entity_id) {
        query = query.eq('entity_id', filters.entity_id)
      }
      if (filters.status) {
        query = query.eq('status', filters.status)
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
      console.error('Get anomalies error:', error)
      return []
    }
  }

  // Get threat detection rules
  async getRules(
    filters: {
      rule_type?: string
      category?: string
      is_active?: boolean
    } = {}
  ): Promise<ThreatDetectionRule[]> {
    try {
      let query = this.client
        .from('threat_detection_rules')
        .select('*')
        .order('severity_score', { ascending: false })

      // Apply filters
      if (filters.rule_type) {
        query = query.eq('rule_type', filters.rule_type)
      }
      if (filters.category) {
        query = query.eq('category', filters.category)
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
      console.error('Get rules error:', error)
      return []
    }
  }
}

// Behavioral analysis utilities
export class BehavioralAnalyzer {
  // Calculate user behavior metrics
  static calculateUserMetrics(
    userId: string,
    activities: Array<{
      timestamp: string
      action: string
      ip_address: string
      user_agent: string
      success: boolean
    }>
  ): {
    login_frequency: number
    unique_ips: number
    unique_devices: number
    success_rate: number
    typical_hours: number[]
    risk_score: number
  } {
    const now = new Date()
    const last24Hours = activities.filter(a => 
      new Date(a.timestamp) > new Date(now.getTime() - 24 * 60 * 60 * 1000)
    )

    const uniqueIPs = new Set(last24Hours.map(a => a.ip_address))
    const uniqueDevices = new Set(last24Hours.map(a => a.user_agent))
    const successfulLogins = last24Hours.filter(a => a.success)
    const hours = last24Hours.map(a => new Date(a.timestamp).getHours())

    // Calculate risk score
    let riskScore = 0
    if (uniqueIPs.size > 5) riskScore += 20
    if (uniqueDevices.size > 3) riskScore += 15
    if (successfulLogins.length / last24Hours.length < 0.8) riskScore += 25
    if (last24Hours.length > 100) riskScore += 30

    return {
      login_frequency: last24Hours.length,
      unique_ips: uniqueIPs.size,
      unique_devices: uniqueDevices.size,
      success_rate: last24Hours.length > 0 ? successfulLogins.length / last24Hours.length : 1,
      typical_hours: hours,
      risk_score: Math.min(100, riskScore)
    }
  }

  // Detect anomalies in user behavior
  static detectAnomalies(
    baseline: BehavioralBaseline,
    currentMetrics: Record<string, any>
  ): {
    anomalies: Array<{
      metric: string
      observed: any
      expected: any
      deviation: number
      severity: 'low' | 'medium' | 'high'
    }>
    overall_risk: 'low' | 'medium' | 'high'
  } {
    const anomalies = []
    let totalRisk = 0

    for (const [metric, value] of Object.entries(currentMetrics)) {
      const baselineMean = baseline.mean_values[metric]
      const baselineStd = baseline.standard_deviations[metric]

      if (baselineMean !== undefined && baselineStd !== undefined) {
        const deviation = Math.abs((value - baselineMean) / baselineStd)
        
        let severity: 'low' | 'medium' | 'high'
        if (deviation > 3) {
          severity = 'high'
          totalRisk += 30
        } else if (deviation > 2) {
          severity = 'medium'
          totalRisk += 20
        } else if (deviation > 1.5) {
          severity = 'low'
          totalRisk += 10
        }

        anomalies.push({
          metric,
          observed: value,
          expected: baselineMean,
          deviation,
          severity
        })
      }
    }

    const overallRisk = totalRisk > 60 ? 'high' : totalRisk > 30 ? 'medium' : 'low'

    return { anomalies, overall_risk: overallRisk }
  }

  // Generate behavioral patterns
  static generatePatterns(
    activities: Array<{
      timestamp: string
      action: string
      ip_address: string
      user_agent: string
      success: boolean
    }>
  ): {
    temporal_patterns: Record<string, number>
    location_patterns: Record<string, number>
    device_patterns: Record<string, number>
    action_patterns: Record<string, number>
  } {
    const temporalPatterns: Record<string, number> = {}
    const locationPatterns: Record<string, number> = {}
    const devicePatterns: Record<string, number> = {}
    const actionPatterns: Record<string, number> = {}

    activities.forEach(activity => {
      // Temporal patterns (hour of day)
      const hour = new Date(activity.timestamp).getHours().toString()
      temporalPatterns[hour] = (temporalPatterns[hour] || 0) + 1

      // Location patterns
      locationPatterns[activity.ip_address] = (locationPatterns[activity.ip_address] || 0) + 1

      // Device patterns
      const device = activity.user_agent.split(' ')[0] || 'unknown'
      devicePatterns[device] = (devicePatterns[device] || 0) + 1

      // Action patterns
      actionPatterns[activity.action] = (actionPatterns[activity.action] || 0) + 1
    })

    return {
      temporal_patterns: temporalPatterns,
      location_patterns: locationPatterns,
      device_patterns: devicePatterns,
      action_patterns: actionPatterns
    }
  }
}

// Threat intelligence utilities
export class ThreatIntelligence {
  // Enrich IP with threat intelligence
  static async enrichIP(ipAddress: string): Promise<{
    reputation: {
      score: number
      risk_level: string
      source: string
    }
    geolocation: {
      country: string
      city: string
      latitude: number
      longitude: number
    }
    indicators: Array<{
      type: string
      value: string
      category: string
      confidence: number
    }>
  }> {
    const client = ThreatDetectionClient.getInstance()

    // Get threat indicators for IP
    const indicators = await client.checkIndicators('ip', ipAddress)

    // Get geolocation (simplified)
    const geolocation = {
      country: 'Unknown',
      city: 'Unknown',
      latitude: 0,
      longitude: 0
    }

    // Calculate reputation
    const maliciousIndicators = indicators.filter(i => i.category === 'malicious')
    const suspiciousIndicators = indicators.filter(i => i.category === 'suspicious')
    
    let riskLevel = 'low'
    let score = 0.8

    if (maliciousIndicators.length > 0) {
      riskLevel = 'critical'
      score = 0.1
    } else if (suspiciousIndicators.length > 0) {
      riskLevel = 'high'
      score = 0.3
    }

    return {
      reputation: {
        score,
        risk_level,
        source: 'internal_threat_intelligence'
      },
      geolocation,
      indicators: indicators.map(i => ({
        type: 'ip',
        value: ipAddress,
        category: i.category,
        confidence: i.confidence
      }))
    }
  }

  // Check domain reputation
  static async checkDomainReputation(domain: string): Promise<{
    is_malicious: boolean
    is_suspicious: boolean
    confidence: number
    sources: string[]
  }> {
    const client = ThreatDetectionClient.getInstance()
    const indicators = await client.checkIndicators('domain', domain)

    const malicious = indicators.some(i => i.category === 'malicious')
    const suspicious = indicators.some(i => i.category === 'suspicious')
    const confidence = indicators.length > 0 ? indicators[0].confidence : 0
    const sources = indicators.map(i => i.source)

    return {
      is_malicious: malicious,
      is_suspicious: suspicious,
      confidence,
      sources
    }
  }
}

// Export singleton instance
export const threatDetectionClient = ThreatDetectionClient.getInstance()
