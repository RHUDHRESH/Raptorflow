import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

// Audit event types
export interface AuditEvent {
  actor_id?: string
  action_category: 'read' | 'write' | 'delete' | 'admin' | 'auth' | 'security' | 'billing' | 'workspace'
  action_type: string
  resource_type: string
  resource_id?: string
  workspace_id?: string
  old_values?: Record<string, any>
  new_values?: Record<string, any>
  sensitive_fields?: string[]
  request_id?: string
  request_path?: string
  request_method?: string
  success?: boolean
  error_code?: string
  error_message?: string
  gdpr_relevant?: boolean
  data_subject_id?: string
  legal_basis?: string
  duration_ms?: number
}

// Data access log entry
export interface DataAccessLog {
  data_subject_id: string
  purpose: string
  legal_basis: string
  accessed_data: Record<string, any>
  accessor_id?: string
}

// Security event types
export interface SecurityEvent {
  event_type: string
  severity: 'info' | 'warning' | 'high' | 'critical'
  category: 'authentication' | 'authorization' | 'data_access' | 'system' | 'network' | 'malware' | 'fraud'
  description?: string
  details?: Record<string, any>
  indicators?: Record<string, any>
  user_id?: string
  workspace_id?: string
  action_taken?: 'blocked' | 'flagged' | 'logged' | 'notified' | 'investigated' | 'resolved'
  auto_response?: boolean
  investigation_priority?: 'low' | 'medium' | 'high' | 'critical'
}

// User behavior baseline update
export interface BehaviorBaseline {
  user_id: string
  session_duration?: number
  actions_count?: number
  data_access_pattern?: Record<string, any>
}

// Server-side audit logging
export async function logAuditEvent(event: AuditEvent): Promise<string | null> {
  const cookieStore = cookies()
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { getAll: () => cookieStore.getAll(), setAll: () => {} } }
  )

  try {
    const { data, error } = await supabase.rpc('log_audit_event', {
      p_actor_id: event.actor_id,
      p_action_category: event.action_category,
      p_action_type: event.action_type,
      p_resource_type: event.resource_type,
      p_resource_id: event.resource_id,
      p_workspace_id: event.workspace_id,
      p_old_values: event.old_values,
      p_new_values: event.new_values,
      p_sensitive_fields: event.sensitive_fields,
      p_request_id: event.request_id,
      p_request_path: event.request_path,
      p_request_method: event.request_method,
      p_success: event.success ?? true,
      p_error_code: event.error_code,
      p_error_message: event.error_message,
      p_gdpr_relevant: event.gdpr_relevant ?? false,
      p_data_subject_id: event.data_subject_id,
      p_legal_basis: event.legal_basis,
      p_duration_ms: event.duration_ms
    })

    if (error) {
      console.error('Audit log error:', error)
      return null
    }

    return data

  } catch (error) {
    console.error('Audit log error:', error)
    return null
  }
}

// Server-side data access logging
export async function logDataAccess(log: DataAccessLog): Promise<string | null> {
  const cookieStore = cookies()
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { getAll: () => cookieStore.getAll(), setAll: () => {} } }
  )

  try {
    const { data, error } = await supabase.rpc('log_data_access', {
      p_data_subject_id: log.data_subject_id,
      p_purpose: log.purpose,
      p_legal_basis: log.legal_basis,
      p_accessed_data: log.accessed_data,
      p_accessor_id: log.accessor_id
    })

    if (error) {
      console.error('Data access log error:', error)
      return null
    }

    return data

  } catch (error) {
    console.error('Data access log error:', error)
    return null
  }
}

// Server-side security event logging
export async function logSecurityEvent(event: SecurityEvent): Promise<string | null> {
  const cookieStore = cookies()
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { getAll: () => cookieStore.getAll(), setAll: () => {} } }
  )

  try {
    const { data, error } = await supabase.rpc('log_security_event', {
      p_event_type: event.event_type,
      p_severity: event.severity,
      p_category: event.category,
      p_description: event.description,
      p_details: event.details,
      p_indicators: event.indicators,
      p_user_id: event.user_id,
      p_workspace_id: event.workspace_id,
      p_action_taken: event.action_taken ?? 'logged',
      p_auto_response: event.auto_response ?? false,
      p_investigation_priority: event.investigation_priority ?? 'medium'
    })

    if (error) {
      console.error('Security event log error:', error)
      return null
    }

    return data

  } catch (error) {
    console.error('Security event log error:', error)
    return null
  }
}

// Update user behavior baseline
export async function updateBehaviorBaseline(baseline: BehaviorBaseline): Promise<boolean> {
  const cookieStore = cookies()
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { getAll: () => cookieStore.getAll(), setAll: () => {} } }
  )

  try {
    const { data, error } = await supabase.rpc('update_user_behavior_baseline', {
      p_user_id: baseline.user_id,
      p_session_duration: baseline.session_duration,
      p_actions_count: baseline.actions_count,
      p_data_access_pattern: baseline.data_access_pattern
    })

    if (error) {
      console.error('Behavior baseline update error:', error)
      return false
    }

    return !!data

  } catch (error) {
    console.error('Behavior baseline update error:', error)
    return false
  }
}

// Detect anomalous behavior
export async function detectAnomalousBehavior(
  userId: string,
  currentIp?: string,
  currentDevice?: Record<string, any>,
  currentTime?: Date,
  sessionDuration?: number,
  actionsCount?: number
): Promise<Array<{
  anomaly_type: string
  severity: string
  confidence: number
  details: Record<string, any>
}>> {
  const cookieStore = cookies()
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { getAll: () => cookieStore.getAll(), setAll: () => {} } }
  )

  try {
    const { data, error } = await supabase.rpc('detect_anomalous_behavior', {
      p_user_id: userId,
      p_current_ip: currentIp,
      p_current_device: currentDevice,
      p_current_time: currentTime?.toISOString(),
      p_session_duration: sessionDuration,
      p_actions_count: actionsCount
    })

    if (error) {
      console.error('Anomaly detection error:', error)
      return []
    }

    return data || []

  } catch (error) {
    console.error('Anomaly detection error:', error)
    return []
  }
}

// Common audit event helpers
export const AuditHelpers = {
  // User actions
  userLogin: (userId: string, success: boolean, error?: string) => ({
    actor_id: userId,
    action_category: 'auth' as const,
    action_type: 'user_login',
    resource_type: 'user',
    resource_id: userId,
    success,
    error_message: error,
    gdpr_relevant: true
  }),

  userLogout: (userId: string, sessionDuration?: number) => ({
    actor_id: userId,
    action_category: 'auth' as const,
    action_type: 'user_logout',
    resource_type: 'user',
    resource_id: userId,
    duration_ms: sessionDuration,
    gdpr_relevant: true
  }),

  userRegistration: (userId: string) => ({
    actor_id: userId,
    action_category: 'write' as const,
    action_type: 'user_registration',
    resource_type: 'user',
    resource_id: userId,
    gdpr_relevant: true
  }),

  // Workspace actions
  workspaceCreated: (userId: string, workspaceId: string, workspaceName: string) => ({
    actor_id: userId,
    action_category: 'write' as const,
    action_type: 'workspace_created',
    resource_type: 'workspace',
    resource_id: workspaceId,
    new_values: { name: workspaceName },
    gdpr_relevant: true
  }),

  workspaceUpdated: (userId: string, workspaceId: string, oldValues: Record<string, any>, newValues: Record<string, any>) => ({
    actor_id: userId,
    action_category: 'write' as const,
    action_type: 'workspace_updated',
    resource_type: 'workspace',
    resource_id: workspaceId,
    old_values: oldValues,
    new_values: newValues,
    gdpr_relevant: true
  }),

  workspaceDeleted: (userId: string, workspaceId: string, workspaceName: string) => ({
    actor_id: userId,
    action_category: 'delete' as const,
    action_type: 'workspace_deleted',
    resource_type: 'workspace',
    resource_id: workspaceId,
    old_values: { name: workspaceName },
    gdpr_relevant: true
  }),

  // Data access
  dataAccessed: (userId: string, resourceType: string, resourceId: string, fields: string[]) => ({
    actor_id: userId,
    action_category: 'read' as const,
    action_type: 'data_accessed',
    resource_type: resourceType,
    resource_id: resourceId,
    sensitive_fields: fields,
    gdpr_relevant: true
  }),

  dataModified: (userId: string, resourceType: string, resourceId: string, oldValues: Record<string, any>, newValues: Record<string, any>) => ({
    actor_id: userId,
    action_category: 'write' as const,
    action_type: 'data_modified',
    resource_type: resourceType,
    resource_id: resourceId,
    old_values: oldValues,
    new_values: newValues,
    gdpr_relevant: true
  }),

  dataDeleted: (userId: string, resourceType: string, resourceId: string, deletedData: Record<string, any>) => ({
    actor_id: userId,
    action_category: 'delete' as const,
    action_type: 'data_deleted',
    resource_type: resourceType,
    resource_id: resourceId,
    old_values: deletedData,
    gdpr_relevant: true
  }),

  // Admin actions
  permissionGranted: (adminId: string, targetUserId: string, permission: string) => ({
    actor_id: adminId,
    action_category: 'admin' as const,
    action_type: 'permission_granted',
    resource_type: 'user_permission',
    resource_id: targetUserId,
    new_values: { permission },
    gdpr_relevant: true
  }),

  userBanned: (adminId: string, targetUserId: string, reason: string) => ({
    actor_id: adminId,
    action_category: 'admin' as const,
    action_type: 'user_banned',
    resource_type: 'user',
    resource_id: targetUserId,
    new_values: { banned: true, ban_reason: reason },
    gdpr_relevant: true
  }),

  // Security events
  suspiciousLogin: (userId: string, ip: string, reason: string) => ({
    event_type: 'suspicious_login_attempt',
    severity: 'high' as const,
    category: 'authentication' as const,
    description: `Suspicious login attempt for user ${userId}`,
    details: { ip, reason },
    user_id: userId,
    action_taken: 'flagged',
    auto_response: true
  }),

  bruteForceDetected: (ip: string, attempts: number) => ({
    event_type: 'brute_force_attack',
    severity: 'critical' as const,
    category: 'authentication' as const,
    description: `Brute force attack detected from ${ip}`,
    details: { ip, attempts },
    action_taken: 'blocked',
    auto_response: true,
    investigation_priority: 'high'
  }),

  unusualAccess: (userId: string, anomalyType: string, details: Record<string, any>) => ({
    event_type: 'unusual_access_pattern',
    severity: 'medium' as const,
    category: 'data_access' as const,
    description: `Unusual access pattern detected for user ${userId}`,
    details: { anomaly_type: anomalyType, ...details },
    user_id: userId,
    action_taken: 'flagged',
    auto_response: true
  })
}

// GDPR compliance helpers
export const GDPRHelpers = {
  // Legal basis constants
  LEGAL_BASIS: {
    CONSENT: 'consent',
    CONTRACT: 'contract',
    LEGAL_OBLIGATION: 'legal_obligation',
    VITAL_INTERESTS: 'vital_interests',
    PUBLIC_TASK: 'public_task',
    LEGITIMATE_INTERESTS: 'legitimate_interests'
  } as const,

  // Data access purposes
  PURPOSES: {
    SERVICE_PROVISION: 'service_provision',
    AUTHENTICATION: 'authentication',
    BILLING: 'billing',
    SUPPORT: 'customer_support',
    ANALYTICS: 'analytics',
    LEGAL_COMPLIANCE: 'legal_compliance',
    SECURITY_MONITORING: 'security_monitoring'
  } as const,

  // Sensitive data fields
  SENSITIVE_FIELDS: [
    'email',
    'phone',
    'full_name',
    'address',
    'payment_method',
    'health_data',
    'biometric_data'
  ]
}

// Audit middleware helper
export function createAuditMiddleware(
  getRequestId: () => string,
  getStartTime: () => number
) {
  return async (event: AuditEvent) => {
    const duration = getStartTime() ? Date.now() - getStartTime() : undefined
    
    return await logAuditEvent({
      ...event,
      request_id: getRequestId(),
      duration_ms: duration
    })
  }
}

// Performance monitoring
export class AuditPerformanceMonitor {
  private static operations = new Map<string, number>()

  static startOperation(operationId: string): void {
    this.operations.set(operationId, Date.now())
  }

  static endOperation(operationId: string): number {
    const startTime = this.operations.get(operationId)
    if (!startTime) return 0

    const duration = Date.now() - startTime
    this.operations.delete(operationId)
    return duration
  }

  static async measureOperation<T>(
    operationId: string,
    operation: () => Promise<T>
  ): Promise<{ result: T; duration: number }> {
    this.startOperation(operationId)
    const result = await operation()
    const duration = this.endOperation(operationId)
    
    return { result, duration }
  }
}
