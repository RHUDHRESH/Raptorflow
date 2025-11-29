import { supabase } from '../lib/supabase';

export const moveService = {
    async getMoves(workspaceId: string) {
        if (!supabase) return [];
        try {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return [];

            const apiUrl = (import.meta as any).env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
            
            // Currently listing moves via Supabase directly in previous version, 
            // but let's switch to backend if possible. 
            // However, I didn't implement a "list moves" endpoint in backend/routers/moves.py (I did get_move, create, update).
            // backend/routers/campaigns.py fetches moves for a campaign.
            // backend/routers/moves.py doesn't have a "list all moves for workspace" endpoint.
            // So I should stick to Supabase for listing, OR add the endpoint. 
            // Since I am in the frontend context now, sticking to Supabase for LIST is fine if the backend permissions allow it.
            // But for uniformity, I should have added it. 
            // Let's stick to Supabase for getMoves to avoid changing backend again unless necessary.
            
            const { data, error } = await supabase
                .from('moves')
                .select('*')
                .eq('workspace_id', workspaceId)
                .order('created_at', { ascending: false });

            if (error) throw error;
            return data;
        } catch (error) {
            console.error('Error fetching moves:', error);
            return [];
        }
    },

    async getMove(id: string) {
        if (!supabase) return null;
        try {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return null;

            const apiUrl = (import.meta as any).env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
            const response = await fetch(`${apiUrl}/moves/${id}`, {
                headers: {
                    'Authorization': `Bearer ${session.access_token}`
                }
            });
            
            if (!response.ok) throw new Error('Failed to fetch move');
            return await response.json();
        } catch (error) {
            console.error('Error fetching move:', error);
            return null;
        }
    },

    async createMove(move: any) {
        if (!supabase) return null;
        try {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return null;

            const apiUrl = (import.meta as any).env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
            const response = await fetch(`${apiUrl}/moves`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.access_token}`
                },
                body: JSON.stringify(move)
            });
            
            if (!response.ok) throw new Error('Failed to create move');
            return await response.json();
        } catch (error) {
            console.error('Error creating move:', error);
            throw error;
        }
    },

    async updateMove(id: string, updates: any) {
        if (!supabase) return null;
        try {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return null;

            const apiUrl = (import.meta as any).env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
            const response = await fetch(`${apiUrl}/moves/${id}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.access_token}`
                },
                body: JSON.stringify(updates)
            });
            
            if (!response.ok) throw new Error('Failed to update move');
            return await response.json();
        } catch (error) {
            console.error('Error updating move:', error);
            throw error;
        }
    },

    async deleteMove(id: string) {
        const { error } = await supabase
            .from('moves')
            .delete()
            .eq('id', id);

        if (error) throw error;
    },

    // New methods for specific move operations
    async getAssets(moveId: string) {
        if (!supabase) return [];
        try {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return [];

            const apiUrl = (import.meta as any).env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
            const response = await fetch(`${apiUrl}/moves/${moveId}/assets`, {
                headers: {
                    'Authorization': `Bearer ${session.access_token}`
                }
            });
            
            if (!response.ok) throw new Error('Failed to fetch assets');
            return await response.json();
        } catch (error) {
            console.error('Error fetching assets:', error);
            return [];
        }
    },

    async runPreflight(moveId: string) {
        if (!supabase) return null;
        try {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return null;

            const apiUrl = (import.meta as any).env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
            const response = await fetch(`${apiUrl}/moves/${moveId}/preflight`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${session.access_token}`
                }
            });
            
            if (!response.ok) throw new Error('Preflight check failed');
            return await response.json();
        } catch (error) {
            console.error('Error running preflight:', error);
            throw error;
        }
    },

    async generateBriefs(moveId: string) {
        if (!supabase) return [];
        try {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return [];

            const apiUrl = (import.meta as any).env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
            const response = await fetch(`${apiUrl}/moves/${moveId}/generate-briefs`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${session.access_token}`
                }
            });
            
            if (!response.ok) throw new Error('Failed to generate briefs');
            return await response.json();
        } catch (error) {
            console.error('Error generating briefs:', error);
            throw error;
        }
    }
};
