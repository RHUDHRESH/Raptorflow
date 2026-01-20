export enum TitanMode {
  LITE = 'LITE',
  RESEARCH = 'RESEARCH',
  DEEP = 'DEEP',
}

export interface TitanResearchRequest {
  topic: string;
  mode: TitanMode;
  workspace_id: string;
}

export interface TitanResearchResult {
  id: string;
  topic: string;
  summary: string;
  insights: string[];
  sources: Array<{ title: string; url: string; score: number }>;
  created_at: string;
}

export interface BlackboxStrategyRequest {
  workspace_id: string;
  objective: string;
  risk_tolerance: number; // 0 to 1
}

export interface StrategicMove {
  id: string;
  title: string;
  description: string;
  impact: 'low' | 'medium' | 'high';
  effort: 'low' | 'medium' | 'high';
  tasks: string[];
}

export interface BlackboxStrategy {
  id: string;
  objective: string;
  rationale: string;
  moves: StrategicMove[];
  risk_assessment: string;
  created_at: string;
}
