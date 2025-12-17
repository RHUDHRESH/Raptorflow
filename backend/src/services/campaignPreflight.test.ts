import { describe, expect, it } from 'vitest'
import { evaluateCampaignPreflight } from './campaignPreflight'

describe('evaluateCampaignPreflight', () => {
  it('blocks when KPI contract is incomplete', () => {
    const result = evaluateCampaignPreflight({
      campaign: {
        objective_text: '',
        primary_kpi_type: null,
        primary_kpi_baseline: null,
        primary_kpi_target: null,
        primary_kpi_window_start: null,
        primary_kpi_window_end: null,
        channels_json: [],
        measurement_json: {},
        execution_capacity_json: {},
      },
      linkedMoves: [],
      slotCount: 0,
    })

    expect(result.ok).toBe(false)
    expect(result.blockers.join(' ')).toMatch(/Objective|KPI/i)
  })

  it('blocks when no ready move is linked', () => {
    const result = evaluateCampaignPreflight({
      campaign: {
        objective_text: 'Drive qualified leads',
        primary_kpi_type: 'qualified_leads',
        primary_kpi_baseline: 10,
        primary_kpi_target: 20,
        primary_kpi_window_start: '2025-01-01',
        primary_kpi_window_end: '2025-02-01',
        channels_json: [],
        measurement_json: {},
        execution_capacity_json: {},
      },
      linkedMoves: [
        {
          id: 'm1',
          tasks: [],
          channels: ['linkedin'],
          tracking_json: { metric: 'replies' },
          metadata: { required_assets: ['copy'] },
        },
      ],
      slotCount: 0,
    })

    expect(result.ok).toBe(false)
    expect(result.blockers.join(' ')).toMatch(/No ready Move/i)
  })

  it('blocks when traffic-driving channel requires UTM but measurement is missing', () => {
    const result = evaluateCampaignPreflight({
      campaign: {
        objective_text: 'Drive signups',
        primary_kpi_type: 'signups',
        primary_kpi_baseline: 0,
        primary_kpi_target: 50,
        primary_kpi_window_start: '2025-01-01',
        primary_kpi_window_end: '2025-02-01',
        channels_json: [{ id: 'linkedin', drives_traffic: true }],
        measurement_json: {},
        execution_capacity_json: {},
      },
      linkedMoves: [
        {
          id: 'm1',
          tasks: [{ id: 't1', task: 'Do thing', status: 'pending' }],
          channels: ['linkedin'],
          tracking_json: { metric: 'signups' },
          metadata: { required_assets: ['visual'] },
        },
      ],
      slotCount: 0,
    })

    expect(result.ok).toBe(false)
    expect(result.blockers.join(' ')).toMatch(/UTM/i)
  })

  it('passes when KPI contract, measurement, and ready move are present', () => {
    const result = evaluateCampaignPreflight({
      campaign: {
        objective_text: 'Drive signups',
        primary_kpi_type: 'signups',
        primary_kpi_baseline: 10,
        primary_kpi_target: 50,
        primary_kpi_window_start: '2025-01-01',
        primary_kpi_window_end: '2025-02-01',
        channels_json: [{ id: 'linkedin', drives_traffic: true }],
        measurement_json: { utm_convention: 'rf_{campaign}_{move}_{channel}' },
        execution_capacity_json: { wip_limit: 3, hours_per_week: 10 },
      },
      linkedMoves: [
        {
          id: 'm1',
          tasks: [{ id: 't1', task: 'Do thing', status: 'pending' }],
          channels: ['linkedin'],
          tracking_json: { metric: 'signups' },
          metadata: { required_assets: ['visual'] },
        },
      ],
      slotCount: 0,
    })

    expect(result.ok).toBe(true)
    expect(result.blockers.length).toBe(0)
    expect(result.health_score).toBeGreaterThanOrEqual(70)
  })
})
