export type CampaignPreflightLabel = 'blocked' | 'at_risk' | 'on_track'

export type CampaignPreflightResult = {
  ok: boolean
  blockers: string[]
  warnings: string[]
  health_score: number
  label: CampaignPreflightLabel
  why: string
  breakdown: Record<string, any>
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0
}

function toNumber(value: unknown): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value === 'string' && value.trim().length > 0) {
    const n = Number(value)
    return Number.isFinite(n) ? n : null
  }
  return null
}

function asArray(value: unknown): any[] {
  return Array.isArray(value) ? value : []
}

export function evaluateCampaignPreflight(input: {
  campaign: any
  linkedMoves?: any[]
  slotCount?: number
}): CampaignPreflightResult {
  const { campaign, linkedMoves = [], slotCount = 0 } = input

  const blockers: string[] = []
  const warnings: string[] = []

  const objectiveOk = isNonEmptyString(campaign?.objective_text)
  const kpiTypeOk = isNonEmptyString(campaign?.primary_kpi_type)
  const baseline = toNumber(campaign?.primary_kpi_baseline)
  const target = toNumber(campaign?.primary_kpi_target)
  const windowStartOk = Boolean(campaign?.primary_kpi_window_start)
  const windowEndOk = Boolean(campaign?.primary_kpi_window_end)

  const baselineOk = baseline !== null
  const targetOk = target !== null && baseline !== null ? target > baseline : target !== null

  if (!objectiveOk) blockers.push('Objective is missing.')
  if (!kpiTypeOk) blockers.push('Primary KPI type is missing.')
  if (!baselineOk) blockers.push('Primary KPI baseline is missing or invalid.')
  if (!targetOk) blockers.push('Primary KPI target must be a valid number and > baseline.')
  if (!windowStartOk || !windowEndOk) blockers.push('Primary KPI window start/end dates are required.')

  const channelsJson = asArray(campaign?.channels_json)
  const measurement = campaign?.measurement_json || {}
  const requiresUtm = Boolean(measurement?.requires_utm) || channelsJson.some(c => Boolean(c?.drives_traffic) || Boolean(c?.requires_utm) || Boolean(c?.has_link))
  const utmOk = isNonEmptyString(measurement?.utm_convention) || (typeof measurement?.utm === 'object' && measurement?.utm !== null)
  if (requiresUtm && !utmOk) blockers.push('Measurement missing: UTM convention required for traffic-driving channels.')

  const plannedMovesCount = linkedMoves.length + Number(slotCount || 0)

  const capacity = campaign?.execution_capacity_json || {}
  const wipLimit = toNumber(capacity?.wip_limit)
  const hoursPerWeek = toNumber(capacity?.hours_per_week)
  const override = Boolean(campaign?.execution_override)

  if (hoursPerWeek !== null && hoursPerWeek <= 0) blockers.push('Execution capacity invalid: hours/week must be > 0.')
  if (wipLimit !== null && plannedMovesCount > wipLimit) {
    if (!override) blockers.push(`Execution overload: planned work (${plannedMovesCount}) exceeds WIP limit (${wipLimit}).`)
    else warnings.push(`Execution overload acknowledged: planned work (${plannedMovesCount}) exceeds WIP limit (${wipLimit}).`)
  }

  const readyMove = linkedMoves.some(m => {
    const tasks = asArray(m?.tasks)
    const channels = asArray(m?.channels)
    const tracking = m?.tracking_json || {}
    const metric = tracking?.metric || tracking?.measurement_hook || tracking?.event
    const requiredAssets = m?.metadata?.required_assets || m?.metadata?.muse_slots || m?.metadata?.asset_slots
    const hasAssets = Array.isArray(requiredAssets)
      ? requiredAssets.length > 0
      : typeof requiredAssets === 'number'
        ? requiredAssets > 0
        : false

    return tasks.length > 0 && channels.length > 0 && Boolean(metric) && hasAssets
  })

  if (!readyMove) blockers.push('No ready Move linked yet (needs tasks + required Muse assets + measurement hook).')

  let score = 100
  if (!objectiveOk) score -= 15
  if (!kpiTypeOk) score -= 10
  if (!baselineOk || !targetOk || !windowStartOk || !windowEndOk) score -= 30
  if (requiresUtm && !utmOk) score -= 15
  if (!readyMove) score -= 30
  if (wipLimit !== null && plannedMovesCount > wipLimit && !override) score -= 20
  if (warnings.length) score -= Math.min(10, warnings.length * 5)

  score = Math.max(0, Math.min(100, score))

  const label: CampaignPreflightLabel = blockers.length
    ? 'blocked'
    : score < 70
      ? 'at_risk'
      : 'on_track'

  const why = blockers[0] || warnings[0] || 'Preflight checks are passing.'

  return {
    ok: blockers.length === 0,
    blockers,
    warnings,
    health_score: score,
    label,
    why,
    breakdown: {
      kpi: { objectiveOk, kpiTypeOk, baselineOk, targetOk, windowStartOk, windowEndOk },
      measurement: { requiresUtm, utmOk },
      execution: { plannedMovesCount, wipLimit, hoursPerWeek, override },
      moves: { linkedMoves: linkedMoves.length, readyMove },
    }
  }
}
