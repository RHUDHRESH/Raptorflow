export interface RICP {
  id: string;
  name: string;
  persona_name?: string;
  avatar: string;
  demographics: Record<string, any>;
  psychographics: Record<string, any>;
  market_sophistication: number;
  confidence: number;
  created_at?: string;
  updated_at?: string;
}

export interface MessagingStrategy {
  id: string;
  workspace_id: string;
  primary_message: string;
  supporting_points: string[];
  tone_voice: string[];
  guardrails: string[];
  created_at: string;
  updated_at: string;
}

export interface Foundation {
  id: string;
  workspace_id: string;
  company_name: string;
  mission?: string;
  vision?: string;
  values: string[];
  industry?: string;
  target_market?: string;
  positioning?: string;
  brand_voice?: string;
  messaging_guardrails: string[];
  summary?: string;
  created_at: string;
  updated_at: string;
  // Extended fields
  ricps?: RICP[];
  messaging?: MessagingStrategy | null;
  icp_count?: number;
  move_count?: number;
  campaign_count?: number;
}
