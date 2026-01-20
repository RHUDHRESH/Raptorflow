export interface MoveDependency {
  id: string;
  status: 'pending' | 'active' | 'completed' | 'failed';
}

export interface StrategicMove {
  id: string;
  workspace_id: string;
  campaign_id: string;
  arc_id: string;
  name: string;
  status: 'pending' | 'active' | 'completed' | 'failed';
  dependencies: string[]; // List of move IDs
  start_date: string;
  end_date: string;
  metadata: Record<string, any>;
}

export interface CampaignArc {
  id: string;
  name: string;
  moves: StrategicMove[];
}

export interface RICP {
  id: string;
  workspace_id: string;
  name: string;
  market_sophistication: number;
  confidence: number;
}
