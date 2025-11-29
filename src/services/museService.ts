import { supabase } from '../lib/supabase';

export const museService = {
    async getAssets(workspaceId) {
        const { data, error } = await supabase
            .from('muse_assets')
            .select('*')
            .eq('workspace_id', workspaceId)
            .order('created_at', { ascending: false });

        if (error) throw error;
        return data;
    },

    async createAsset(asset) {
        const { data, error } = await supabase
            .from('muse_assets')
            .insert([asset])
            .select()
            .single();

        if (error) throw error;
        return data;
    },

    async updateAsset(id, updates) {
        const { data, error } = await supabase
            .from('muse_assets')
            .update(updates)
            .eq('id', id)
            .select()
            .single();

        if (error) throw error;
        return data;
    },

    async deleteAsset(id) {
        const { error } = await supabase
            .from('muse_assets')
            .delete()
            .eq('id', id);

        if (error) throw error;
    }
};
