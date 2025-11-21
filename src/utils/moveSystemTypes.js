// KOA Move System Data Models & Types

// Enums
export const Posture = {
  OFFENSIVE: 'Offensive',
  DEFENSIVE: 'Defensive',
  LOGISTICAL: 'Logistical',
  RECON: 'Recon'
}

export const FoggRole = {
  SPARK: 'Spark',
  FACILITATOR: 'Facilitator',
  SIGNAL: 'Signal'
}

export const MoveStatus = {
  PLANNING: 'Planning',
  OODA_OBSERVE: 'OODA: Observe',
  OODA_ORIENT: 'OODA: Orient',
  OODA_DECIDE: 'OODA: Decide',
  OODA_ACT: 'OODA: Act',
  COMPLETE: 'Complete',
  KILLED: 'Killed'
}

export const CapabilityTier = {
  FOUNDATION: 'Foundation',
  TRACTION: 'Traction',
  SCALE: 'Scale',
  DOMINANCE: 'Dominance'
}

export const CapabilityStatus = {
  LOCKED: 'Locked',
  IN_PROGRESS: 'In_Progress',
  UNLOCKED: 'Unlocked'
}

export const SeasonType = {
  HIGH_SEASON: 'High_Season',
  LOW_SEASON: 'Low_Season',
  SHOULDER: 'Shoulder'
}

export const AnomalyType = {
  TONE_CLASH: 'Tone_Clash',
  FATIGUE: 'Fatigue',
  DRIFT: 'Drift',
  RULE_VIOLATION: 'Rule_Violation',
  CAPACITY_OVERLOAD: 'Capacity_Overload'
}

// ManeuverType (Template)
export const createManeuverType = (data) => ({
  id: data.id || `maneuver-${Date.now()}`,
  name: data.name,
  category: data.category, // Posture enum
  base_duration_days: data.base_duration_days || 14,
  required_capability_ids: data.required_capability_ids || [],
  fogg_role: data.fogg_role, // FoggRole enum
  intensity_score: data.intensity_score || 5, // 1-10
  risk_profile: data.risk_profile || 'Medium',
  tier: data.tier, // CapabilityTier enum
  description: data.description || '',
  typical_icps: data.typical_icps || [],
  preview_plan: data.preview_plan || {}
})

// Move (Instance)
export const createMove = (data) => ({
  id: data.id || `move-${Date.now()}`,
  maneuver_type_id: data.maneuver_type_id,
  sprint_id: data.sprint_id,
  line_of_operation_id: data.line_of_operation_id,
  primary_icp_id: data.primary_icp_id,
  status: data.status || MoveStatus.PLANNING,
  ooda_config: data.ooda_config || {
    observe_sources: [],
    orient_rules: '',
    decide_logic: '',
    act_tasks: []
  },
  fogg_dynamic_config: data.fogg_dynamic_config || {
    target_motivation: 'Medium',
    target_ability: 'Medium',
    prompt_frequency: 'Daily'
  },
  owner_id: data.owner_id,
  anomalies_detected: data.anomalies_detected || [],
  start_date: data.start_date,
  end_date: data.end_date,
  health_status: data.health_status || 'green', // green/amber/red
  metrics: data.metrics || {}
})

// LineOfOperation
export const createLineOfOperation = (data) => ({
  id: data.id || `loo-${Date.now()}`,
  name: data.name,
  strategic_objective: data.strategic_objective || '',
  seasonality_tag: data.seasonality_tag || SeasonType.SHOULDER,
  center_of_gravity: data.center_of_gravity || '',
  move_ids: data.move_ids || [],
  quest_id: data.quest_id || null
})

// Sprint
export const createSprint = (data) => ({
  id: data.id || `sprint-${Date.now()}`,
  start_date: data.start_date,
  end_date: data.end_date,
  theme: data.theme || '',
  capacity_budget: data.capacity_budget || 40,
  current_load: data.current_load || 0,
  season_type: data.season_type || SeasonType.SHOULDER,
  move_ids: data.move_ids || []
})

// CapabilityNode (Tech Tree)
export const createCapabilityNode = (data) => ({
  id: data.id || `capability-${Date.now()}`,
  name: data.name,
  tier: data.tier, // CapabilityTier enum
  status: data.status || CapabilityStatus.LOCKED,
  parent_nodes: data.parent_nodes || [],
  unlocks_maneuver_ids: data.unlocks_maneuver_ids || [],
  description: data.description || '',
  icon: data.icon || 'Target'
})

// Quest
export const createQuest = (data) => ({
  id: data.id || `quest-${Date.now()}`,
  name: data.name,
  objective: data.objective || '',
  prerequisite_node_ids: data.prerequisite_node_ids || [],
  recommended_move_ids: data.recommended_move_ids || [],
  reward_node_id: data.reward_node_id || null,
  line_of_operation_id: data.line_of_operation_id || null,
  progress: data.progress || 0,
  status: data.status || 'locked' // locked/active/complete
})

// Anomaly
export const createAnomaly = (data) => ({
  id: data.id || `anomaly-${Date.now()}`,
  move_id: data.move_id,
  type: data.type, // AnomalyType enum
  severity: data.severity || 3, // 1-5
  detected_at: data.detected_at || new Date().toISOString(),
  resolution: data.resolution || '',
  message: data.message || ''
})

// Mock Data Generators
export const generateMockManeuverTypes = () => [
  createManeuverType({
    id: 'authority-sprint',
    name: 'Authority Sprint',
    category: Posture.OFFENSIVE,
    base_duration_days: 14,
    fogg_role: FoggRole.SPARK,
    tier: CapabilityTier.TRACTION,
    intensity_score: 7,
    required_capability_ids: ['lead-magnet', 'email-nurture'],
    description: 'Concentrated burst of high-value content targeting Center of Gravity',
    typical_icps: ['Skeptical', 'Status-Driven']
  }),
  createManeuverType({
    id: 'scarcity-flank',
    name: 'Scarcity Flank',
    category: Posture.OFFENSIVE,
    base_duration_days: 14,
    fogg_role: FoggRole.SIGNAL,
    tier: CapabilityTier.SCALE,
    intensity_score: 8,
    required_capability_ids: ['paid-ads', 'email-nurture'],
    description: 'Bypass competitor strength using scarcity and urgency psychology'
  }),
  createManeuverType({
    id: 'garrison',
    name: 'Garrison (Churn Defense)',
    category: Posture.DEFENSIVE,
    base_duration_days: 7,
    fogg_role: FoggRole.SPARK,
    tier: CapabilityTier.TRACTION,
    intensity_score: 5,
    required_capability_ids: ['crm-integration'],
    description: 'Triggered high-touch engagements for at-risk customers'
  }),
  createManeuverType({
    id: 'asset-forge',
    name: 'Asset Forge',
    category: Posture.LOGISTICAL,
    base_duration_days: 7,
    fogg_role: null,
    tier: CapabilityTier.FOUNDATION,
    intensity_score: 4,
    required_capability_ids: [],
    description: 'Sprint dedicated to creating reusable assets (case studies, white papers)'
  }),
  createManeuverType({
    id: 'intel-sweep',
    name: 'Intel Sweep',
    category: Posture.RECON,
    base_duration_days: 7,
    fogg_role: FoggRole.SIGNAL,
    tier: CapabilityTier.FOUNDATION,
    intensity_score: 3,
    required_capability_ids: [],
    description: 'Research-focused move: surveys, customer interviews'
  })
]

export const generateMockCapabilityNodes = () => [
  createCapabilityNode({
    id: 'analytics-core',
    name: 'Analytics Core',
    tier: CapabilityTier.FOUNDATION,
    status: CapabilityStatus.UNLOCKED,
    parent_nodes: [],
    unlocks_maneuver_ids: ['intel-sweep']
  }),
  createCapabilityNode({
    id: 'icp-definition',
    name: 'ICP Definition',
    tier: CapabilityTier.FOUNDATION,
    status: CapabilityStatus.UNLOCKED,
    parent_nodes: ['analytics-core'],
    unlocks_maneuver_ids: []
  }),
  createCapabilityNode({
    id: 'lead-magnet',
    name: 'Lead Magnet v1',
    tier: CapabilityTier.TRACTION,
    status: CapabilityStatus.UNLOCKED,
    parent_nodes: ['icp-definition'],
    unlocks_maneuver_ids: ['authority-sprint']
  }),
  createCapabilityNode({
    id: 'email-nurture',
    name: 'Email Nurture',
    tier: CapabilityTier.TRACTION,
    status: CapabilityStatus.UNLOCKED,
    parent_nodes: ['lead-magnet'],
    unlocks_maneuver_ids: ['authority-sprint']
  }),
  createCapabilityNode({
    id: 'paid-ads',
    name: 'Paid Ads',
    tier: CapabilityTier.SCALE,
    status: CapabilityStatus.LOCKED,
    parent_nodes: ['analytics-core', 'lead-magnet'],
    unlocks_maneuver_ids: ['scarcity-flank']
  }),
  createCapabilityNode({
    id: 'crm-integration',
    name: 'CRM Integration',
    tier: CapabilityTier.TRACTION,
    status: CapabilityStatus.UNLOCKED,
    parent_nodes: ['analytics-core'],
    unlocks_maneuver_ids: ['garrison']
  })
]


