/**
 * Notification Service
 * Handles in-app notifications and alert system
 */

import { supabase } from '../supabase';

export interface Notification {
  id: string;
  workspace_id: string;
  user_id: string;
  type: 'sprint_review_ready' | 'anomaly_critical' | 'move_approval_needed' | 'quick_win_ready' | 'system';
  title: string;
  message: string;
  link?: string;
  read: boolean;
  created_at: string;
}

export const notificationService = {
  /**
   * Get all notifications for current user
   */
  async getAll(options?: {
    unreadOnly?: boolean;
    limit?: number;
  }): Promise<Notification[]> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return [];
    }

    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      return [];
    }

    let query = supabase
      .from('notifications')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false });

    if (options?.unreadOnly) {
      query = query.eq('read', false);
    }

    if (options?.limit) {
      query = query.limit(options.limit);
    }

    const { data, error } = await query;

    if (error) {
      console.error('Error fetching notifications:', error);
      return [];
    }

    return data || [];
  },

  /**
   * Get unread count
   */
  async getUnreadCount(): Promise<number> {
    if (!supabase) {
      return 0;
    }

    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      return 0;
    }

    const { count, error } = await supabase
      .from('notifications')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', user.id)
      .eq('read', false);

    if (error) {
      console.error('Error fetching unread count:', error);
      return 0;
    }

    return count || 0;
  },

  /**
   * Mark notification as read
   */
  async markRead(id: string): Promise<Notification> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('notifications')
      .update({ read: true })
      .eq('id', id)
      .select()
      .single();

    if (error) {
      console.error('Error marking notification as read:', error);
      throw error;
    }

    return data;
  },

  /**
   * Mark all notifications as read
   */
  async markAllRead(): Promise<void> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      return;
    }

    const { error } = await supabase
      .from('notifications')
      .update({ read: true })
      .eq('user_id', user.id)
      .eq('read', false);

    if (error) {
      console.error('Error marking all notifications as read:', error);
      throw error;
    }
  },

  /**
   * Create a notification
   */
  async createNotification(
    notification: Omit<Notification, 'id' | 'workspace_id' | 'created_at' | 'read'>
  ): Promise<Notification> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('notifications')
      .insert({
        ...notification,
        read: false
      })
      .select()
      .single();

    if (error) {
      console.error('Error creating notification:', error);
      throw error;
    }

    return data;
  },

  /**
   * Create notification for all workspace members
   */
  async notifyWorkspace(
    notification: Omit<Notification, 'id' | 'workspace_id' | 'user_id' | 'created_at' | 'read'>,
    excludeUserId?: string
  ): Promise<Notification[]> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    // Get all workspace members
    const { data: members, error: memberError } = await supabase
      .from('user_workspaces')
      .select('user_id');

    if (memberError) {
      console.error('Error fetching workspace members:', memberError);
      throw memberError;
    }

    const userIds = members
      ?.map(m => m.user_id)
      .filter(id => id !== excludeUserId) || [];

    if (userIds.length === 0) {
      return [];
    }

    // Create notification for each user
    const notifications = userIds.map(userId => ({
      ...notification,
      user_id: userId,
      read: false
    }));

    const { data, error } = await supabase
      .from('notifications')
      .insert(notifications)
      .select();

    if (error) {
      console.error('Error creating workspace notifications:', error);
      throw error;
    }

    return data || [];
  },

  /**
   * Delete a notification
   */
  async deleteNotification(id: string): Promise<void> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { error } = await supabase
      .from('notifications')
      .delete()
      .eq('id', id);

    if (error) {
      console.error('Error deleting notification:', error);
      throw error;
    }
  },

  /**
   * Delete old read notifications (cleanup)
   */
  async deleteOldRead(daysOld: number = 30): Promise<number> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysOld);

    const { data, error } = await supabase
      .from('notifications')
      .delete()
      .eq('read', true)
      .lt('created_at', cutoffDate.toISOString())
      .select();

    if (error) {
      console.error('Error deleting old notifications:', error);
      throw error;
    }

    return data?.length || 0;
  },

  /**
   * Subscribe to real-time notifications
   */
  subscribeToNotifications(
    userId: string,
    callback: (notification: Notification) => void
  ): () => void {
    if (!supabase) {
      return () => {};
    }

    const channel = supabase
      .channel('notifications')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'notifications',
          filter: `user_id=eq.${userId}`
        },
        (payload) => {
          callback(payload.new as Notification);
        }
      )
      .subscribe();

    // Return unsubscribe function
    return () => {
      channel.unsubscribe();
    };
  }
};

