/** Business Context Manifest types */

export interface BCMFoundation {
  company: string;
  industry: string;
  stage: string;
  mission: string;
  value_prop: string;
}

export interface BCMICP {
  name: string;
  role: string;
  pains: string[];
  goals: string[];
  channels: string[];
  triggers: string[];
}

export interface BCMAlternative {
  name: string;
  type: string;
}

export interface BCMCompetitive {
  category: string;
  path: string;
  alternatives: BCMAlternative[];
  differentiation: string;
}

export interface BCMMessaging {
  one_liner: string;
  positioning: string;
  tone: string[];
  guardrails: string[];
  soundbites: string[];
}

export interface BCMChannel {
  name: string;
  priority: string;
}

export interface BCMMarket {
  tam: string;
  sam: string;
  som: string;
}

export interface BCMMeta {
  source: string;
  token_estimate: number;
  facts_count: number;
  icps_count: number;
  competitors_count: number;
}

export interface BCMManifest {
  version: number;
  generated_at: string;
  workspace_id: string;
  checksum: string;
  foundation: BCMFoundation;
  icps: BCMICP[];
  competitive: BCMCompetitive;
  messaging: BCMMessaging;
  channels: BCMChannel[];
  market: BCMMarket;
  meta: BCMMeta;
}

export interface BCMResponse {
  manifest: BCMManifest;
  version: number;
  checksum: string;
  token_estimate: number;
  created_at: string | null;
  completion_pct: number;
}

export interface BCMVersionSummary {
  id: string;
  version: number;
  checksum: string;
  token_estimate: number;
  created_at: string | null;
}
