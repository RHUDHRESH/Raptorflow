/**
 * Campaign data mappers
 * Transform database rows to API DTOs and vice versa
 */

import type {
  Campaign,
  CreateCampaignInput,
  ICP,
  Move
} from '../../types';

export interface CampaignWithRelations extends Omit<Campaign, 'icp_ids'> {
  icps: ICP[];
  moves: Move[];
}

/**
 * Transform database campaign row to API response DTO
 */
export function toApiCampaign(dbCampaign: any): Campaign {
  return {
    id: dbCampaign.id,
    user_id: dbCampaign.user_id,
    name: dbCampaign.name,
    description: dbCampaign.description,
    goal: dbCampaign.goal,
    demand_source: dbCampaign.demand_source,
    persuasion_axis: dbCampaign.persuasion_axis,
    icp_ids: dbCampaign.icp_ids || [],
    cohort_ids: dbCampaign.cohort_ids || [],
    primary_barriers: dbCampaign.primary_barriers || [],
    protocols: dbCampaign.protocols || [],
    start_date: dbCampaign.start_date,
    end_date: dbCampaign.end_date,
    budget_plan: dbCampaign.budget_plan || { total: 0, currency: 'INR', allocation: {} },
    targets: dbCampaign.targets || {},
    status: dbCampaign.status,
    rag_status: dbCampaign.rag_status || 'unknown',
    rag_details: dbCampaign.rag_details || {},
    created_from_spike: dbCampaign.created_from_spike,
    created_at: dbCampaign.created_at,
    updated_at: dbCampaign.updated_at
  };
}

/**
 * Transform campaign with relations to full API response
 */
export function toApiCampaignWithRelations(
  dbCampaign: any,
  icps: ICP[] = [],
  moves: Move[] = []
): CampaignWithRelations {
  const campaign = toApiCampaign(dbCampaign);

  return {
    ...campaign,
    icps,
    moves
  };
}

/**
 * Transform API input to database insert
 */
export function toDbCampaignInsert(
  userId: string,
  input: CreateCampaignInput
): Omit<Campaign, 'id' | 'created_at' | 'updated_at'> {
  return {
    user_id: userId,
    name: input.name,
    description: input.description,
    goal: input.goal,
    demand_source: input.demand_source,
    persuasion_axis: input.persuasion_axis,
    icp_ids: input.icp_ids || [],
    cohort_ids: input.cohort_ids || [],
    primary_barriers: input.primary_barriers || [],
    protocols: input.protocols || [],
    start_date: input.start_date,
    end_date: input.end_date,
    budget_plan: input.budget_plan ? {
      total: input.budget_plan.total || 0,
      currency: input.budget_plan.currency || 'INR',
      allocation: input.budget_plan.allocation || {}
    } : { total: 0, currency: 'INR', allocation: {} },
    targets: input.targets || {},
    status: 'draft',
    progress_percentage: 0
  };
}

/**
 * Transform API input to database update
 */
export function toDbCampaignUpdate(
  input: Partial<CreateCampaignInput>
): Partial<Campaign> {
  const update: Partial<Campaign> = {};

  if (input.name !== undefined) update.name = input.name;
  if (input.description !== undefined) update.description = input.description;
  if (input.goal !== undefined) update.goal = input.goal;
  if (input.demand_source !== undefined) update.demand_source = input.demand_source;
  if (input.persuasion_axis !== undefined) update.persuasion_axis = input.persuasion_axis;
  if (input.icp_ids !== undefined) update.icp_ids = input.icp_ids;
  if (input.cohort_ids !== undefined) update.cohort_ids = input.cohort_ids;
  if (input.primary_barriers !== undefined) update.primary_barriers = input.primary_barriers;
  if (input.protocols !== undefined) update.protocols = input.protocols;
  if (input.start_date !== undefined) update.start_date = input.start_date;
  if (input.end_date !== undefined) update.end_date = input.end_date;
  if (input.budget_plan !== undefined) update.budget_plan = {
    total: input.budget_plan.total || update.budget_plan?.total || 0,
    currency: input.budget_plan.currency || update.budget_plan?.currency || 'INR',
    allocation: input.budget_plan.allocation || update.budget_plan?.allocation || {}
  };
  if (input.targets !== undefined) update.targets = input.targets;

  return update;
}
