/**
 * Quest Service
 * Manages quests (gamified move sequences) in Supabase
 */

import { supabase } from '../supabase';

export interface Quest {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  goal: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  status: 'Not_Started' | 'In_Progress' | 'Completed' | 'Failed';
  estimated_duration_weeks: number;
  xp_reward: number;
  progress_percentage: number;
  start_date?: string;
  target_completion_date?: string;
  actual_completion_date?: string;
  created_at: string;
  updated_at: string;
}

export interface QuestMove {
  id: string;
  quest_id: string;
  move_id: string;
  sequence_order: number;
  is_required: boolean;
  status: 'Pending' | 'In_Progress' | 'Completed' | 'Skipped';
  created_at: string;
  updated_at: string;
}

export interface QuestMilestone {
  id: string;
  quest_id: string;
  name: string;
  description?: string;
  order_index: number;
  is_completed: boolean;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export const questService = {
  /**
   * Get all quests for a workspace
   */
  async getQuests(workspaceId: string): Promise<Quest[]> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return [];
    }

    const { data, error } = await supabase
      .from('quests')
      .select('*')
      .eq('workspace_id', workspaceId)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching quests:', error);
      throw error;
    }

    return data || [];
  },

  /**
   * Get a single quest by ID
   */
  async getQuest(questId: string): Promise<Quest | null> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    const { data, error } = await supabase
      .from('quests')
      .select('*')
      .eq('id', questId)
      .single();

    if (error) {
      console.error('Error fetching quest:', error);
      return null;
    }

    return data;
  },

  /**
   * Create a new quest
   */
  async createQuest(quest: Partial<Quest>): Promise<Quest | null> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    const { data, error } = await supabase
      .from('quests')
      .insert(quest)
      .select()
      .single();

    if (error) {
      console.error('Error creating quest:', error);
      throw error;
    }

    return data;
  },

  /**
   * Update an existing quest
   */
  async updateQuest(questId: string, updates: Partial<Quest>): Promise<Quest | null> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    const { data, error } = await supabase
      .from('quests')
      .update(updates)
      .eq('id', questId)
      .select()
      .single();

    if (error) {
      console.error('Error updating quest:', error);
      throw error;
    }

    return data;
  },

  /**
   * Delete a quest
   */
  async deleteQuest(questId: string): Promise<boolean> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return false;
    }

    const { error } = await supabase
      .from('quests')
      .delete()
      .eq('id', questId);

    if (error) {
      console.error('Error deleting quest:', error);
      throw error;
    }

    return true;
  },

  /**
   * Get moves for a quest
   */
  async getQuestMoves(questId: string): Promise<QuestMove[]> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return [];
    }

    const { data, error } = await supabase
      .from('quest_moves')
      .select('*')
      .eq('quest_id', questId)
      .order('sequence_order', { ascending: true });

    if (error) {
      console.error('Error fetching quest moves:', error);
      throw error;
    }

    return data || [];
  },

  /**
   * Add a move to a quest
   */
  async addMoveToQuest(questMove: Partial<QuestMove>): Promise<QuestMove | null> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    const { data, error } = await supabase
      .from('quest_moves')
      .insert(questMove)
      .select()
      .single();

    if (error) {
      console.error('Error adding move to quest:', error);
      throw error;
    }

    // Recalculate quest progress
    if (data.quest_id) {
      await this.updateQuestProgress(data.quest_id);
    }

    return data;
  },

  /**
   * Update quest move status
   */
  async updateQuestMoveStatus(
    questMoveId: string,
    status: 'Pending' | 'In_Progress' | 'Completed' | 'Skipped'
  ): Promise<QuestMove | null> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    const { data, error } = await supabase
      .from('quest_moves')
      .update({ status })
      .eq('id', questMoveId)
      .select()
      .single();

    if (error) {
      console.error('Error updating quest move status:', error);
      throw error;
    }

    // Recalculate quest progress
    if (data.quest_id) {
      await this.updateQuestProgress(data.quest_id);
    }

    return data;
  },

  /**
   * Get milestones for a quest
   */
  async getQuestMilestones(questId: string): Promise<QuestMilestone[]> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return [];
    }

    const { data, error } = await supabase
      .from('quest_milestones')
      .select('*')
      .eq('quest_id', questId)
      .order('order_index', { ascending: true });

    if (error) {
      console.error('Error fetching quest milestones:', error);
      throw error;
    }

    return data || [];
  },

  /**
   * Create a milestone for a quest
   */
  async createMilestone(milestone: Partial<QuestMilestone>): Promise<QuestMilestone | null> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    const { data, error } = await supabase
      .from('quest_milestones')
      .insert(milestone)
      .select()
      .single();

    if (error) {
      console.error('Error creating milestone:', error);
      throw error;
    }

    return data;
  },

  /**
   * Complete a milestone
   */
  async completeMilestone(milestoneId: string): Promise<QuestMilestone | null> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    const { data, error } = await supabase
      .from('quest_milestones')
      .update({ is_completed: true, completed_at: new Date().toISOString() })
      .eq('id', milestoneId)
      .select()
      .single();

    if (error) {
      console.error('Error completing milestone:', error);
      throw error;
    }

    return data;
  },

  /**
   * Update quest progress based on completed moves
   */
  async updateQuestProgress(questId: string): Promise<void> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return;
    }

    try {
      const questMoves = await this.getQuestMoves(questId);
      const totalMoves = questMoves.length;
      const completedMoves = questMoves.filter(m => m.status === 'Completed').length;

      const progress = totalMoves > 0 ? Math.round((completedMoves / totalMoves) * 100) : 0;

      // Update quest progress
      await this.updateQuest(questId, { progress_percentage: progress });

      // Update quest status
      if (progress === 100) {
        await this.updateQuest(questId, {
          status: 'Completed',
          actual_completion_date: new Date().toISOString(),
        });
      } else if (progress > 0) {
        await this.updateQuest(questId, { status: 'In_Progress' });
      }
    } catch (error) {
      console.error('Error updating quest progress:', error);
    }
  },

  /**
   * Generate quest template based on goal
   */
  generateQuestTemplate(
    goal: string,
    difficulty: 'Beginner' | 'Intermediate' | 'Advanced'
  ): Partial<Quest> {
    const difficultySettings = {
      Beginner: { duration: 4, xp: 100 },
      Intermediate: { duration: 8, xp: 250 },
      Advanced: { duration: 12, xp: 500 },
    };

    const settings = difficultySettings[difficulty];

    return {
      goal,
      difficulty,
      estimated_duration_weeks: settings.duration,
      xp_reward: settings.xp,
      status: 'Not_Started',
      progress_percentage: 0,
    };
  },
};


