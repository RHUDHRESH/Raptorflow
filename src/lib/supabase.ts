import { createClient } from '@supabase/supabase-js';

// Get environment variables
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

// Create Supabase client with fallback values if env vars are missing
// This prevents the app from crashing, but auth won't work until env vars are set
export const supabase = supabaseUrl && supabaseAnonKey
  ? createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
      db: {
        schema: 'public',
      },
      global: {
        headers: {
          'x-application-name': 'raptorflow',
        },
      },
    })
  : null;

// Helper to check if Supabase is configured
export const isSupabaseConfigured = () => {
  return !!supabase && !!supabaseUrl && !!supabaseAnonKey;
};

// Type-safe database types (generated from Supabase)
export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export interface Database {
  public: {
    Tables: {
      companies: {
        Row: {
          id: string;
          name: string;
          industry: string;
          size: string;
          created_at: string;
          updated_at: string;
        };
        Insert: Omit<Database['public']['Tables']['companies']['Row'], 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Database['public']['Tables']['companies']['Insert']>;
      };
      campaigns: {
        Row: {
          id: string;
          company_id: string;
          name: string;
          objective: string;
          status: string;
          start_date: string;
          end_date: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: Omit<Database['public']['Tables']['campaigns']['Row'], 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Database['public']['Tables']['campaigns']['Insert']>;
      };
      maneuvers: {
        Row: {
          id: string;
          name: string;
          category: string;
          description: string;
          prerequisites: string[];
          cost_estimate: number;
          timeline_weeks: number;
          risk_level: string;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['maneuvers']['Row'], 'id' | 'created_at'>;
        Update: Partial<Database['public']['Tables']['maneuvers']['Insert']>;
      };
      capabilities: {
        Row: {
          id: string;
          name: string;
          category: string;
          tier: number;
          description: string;
          dependencies: string[];
          metrics: Json;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['capabilities']['Row'], 'id' | 'created_at'>;
        Update: Partial<Database['public']['Tables']['capabilities']['Insert']>;
      };
      ooda_loops: {
        Row: {
          id: string;
          campaign_id: string;
          iteration_number: number;
          observe_data: Json;
          orient_insights: Json;
          decide_actions: Json;
          act_results: Json;
          status: string;
          created_at: string;
          updated_at: string;
        };
        Insert: Omit<Database['public']['Tables']['ooda_loops']['Row'], 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Database['public']['Tables']['ooda_loops']['Insert']>;
      };
      ideal_customer_profiles: {
        Row: {
          id: string;
          campaign_id: string;
          name: string;
          demographics: Json;
          psychographics: Json;
          pain_points: string[];
          buying_behavior: Json;
          created_at: string;
          updated_at: string;
        };
        Insert: Omit<Database['public']['Tables']['ideal_customer_profiles']['Row'], 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Database['public']['Tables']['ideal_customer_profiles']['Insert']>;
      };
      market_intelligence: {
        Row: {
          id: string;
          campaign_id: string;
          source: string;
          data_type: string;
          content: Json;
          confidence_score: number;
          collected_at: string;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['market_intelligence']['Row'], 'id' | 'created_at'>;
        Update: Partial<Database['public']['Tables']['market_intelligence']['Insert']>;
      };
      campaign_capabilities: {
        Row: {
          id: string;
          campaign_id: string;
          capability_id: string;
          status: string;
          progress_percentage: number;
          unlocked_at: string | null;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['campaign_capabilities']['Row'], 'id' | 'created_at'>;
        Update: Partial<Database['public']['Tables']['campaign_capabilities']['Insert']>;
      };
    };
  };
}
