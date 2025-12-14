/**
 * ICP data mappers
 * Transform database rows to API DTOs and vice versa
 */

import type {
  ICP,
  CreateICPInput,
  ICPFirmographics,
  ICPPsychographics,
  ICPTechnographics
} from '../../types';

/**
 * Transform database ICP row to API response DTO
 */
export function toApiICP(dbIcp: any): ICP {
  return {
    id: dbIcp.id,
    user_id: dbIcp.user_id,
    intake_id: dbIcp.intake_id,
    label: dbIcp.label,
    slug: dbIcp.slug,
    summary: dbIcp.summary,
    firmographics: dbIcp.firmographics || {},
    technographics: dbIcp.technographics || {},
    psychographics: dbIcp.psychographics || {},
    behavioral_triggers: dbIcp.behavioral_triggers || [],
    buying_committee: dbIcp.buying_committee || [],
    category_context: dbIcp.category_context || {},
    fit_score: dbIcp.fit_score || 0,
    fit_reasoning: dbIcp.fit_reasoning,
    messaging_angle: dbIcp.messaging_angle,
    qualification_questions: dbIcp.qualification_questions || [],
    primary_barriers: dbIcp.primary_barriers || [],
    is_selected: dbIcp.is_selected || false,
    priority_rank: dbIcp.priority_rank || 1,
    is_archived: dbIcp.is_archived || false,
    version: dbIcp.version || 1,
    created_at: dbIcp.created_at,
    updated_at: dbIcp.updated_at
  };
}

/**
 * Transform API input to database insert
 */
export function toDbICPInsert(
  userId: string,
  input: CreateICPInput,
  priorityRank: number = 1
): Omit<ICP, 'id' | 'created_at' | 'updated_at'> {
  return {
    user_id: userId,
    intake_id: input.intake_id,
    label: input.label,
    slug: input.label.toLowerCase().replace(/\s+/g, '-'),
    summary: input.summary,
    firmographics: input.firmographics || {},
    technographics: input.technographics || {},
    psychographics: input.psychographics || {},
    behavioral_triggers: input.behavioral_triggers || [],
    buying_committee: input.buying_committee || [],
    category_context: input.category_context || {},
    fit_score: input.fit_score || 0,
    fit_reasoning: input.fit_reasoning,
    messaging_angle: input.messaging_angle,
    qualification_questions: input.qualification_questions || [],
    primary_barriers: input.primary_barriers || [],
    is_selected: input.is_selected || false,
    priority_rank: priorityRank,
    is_archived: false,
    version: 1
  };
}

/**
 * Transform API input to database update
 */
export function toDbICPUpdate(
  input: Partial<CreateICPInput>
): Partial<ICP> {
  const update: Partial<ICP> = {};

  if (input.label !== undefined) {
    update.label = input.label;
    update.slug = input.label.toLowerCase().replace(/\s+/g, '-');
  }
  if (input.summary !== undefined) update.summary = input.summary;
  if (input.is_selected !== undefined) update.is_selected = input.is_selected;
  if (input.firmographics !== undefined) update.firmographics = input.firmographics;
  if (input.psychographics !== undefined) update.psychographics = input.psychographics;
  if (input.technographics !== undefined) update.technographics = input.technographics;
  if (input.behavioral_triggers !== undefined) update.behavioral_triggers = input.behavioral_triggers;
  if (input.buying_committee !== undefined) update.buying_committee = input.buying_committee;
  if (input.category_context !== undefined) update.category_context = input.category_context;
  if (input.fit_score !== undefined) update.fit_score = input.fit_score;
  if (input.fit_reasoning !== undefined) update.fit_reasoning = input.fit_reasoning;
  if (input.messaging_angle !== undefined) update.messaging_angle = input.messaging_angle;
  if (input.qualification_questions !== undefined) update.qualification_questions = input.qualification_questions;
  if (input.primary_barriers !== undefined) update.primary_barriers = input.primary_barriers;

  return update;
}

/**
 * Transform ICP for priority updates
 */
export function toDbICPPriorityUpdate(
  id: string,
  priorityRank: number
): Pick<ICP, 'id' | 'priority_rank'> {
  return {
    id,
    priority_rank: priorityRank
  };
}
