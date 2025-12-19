export type User = {
  id: string;
  email: string;
  created_at: string;
};

export type Campaign = {
  id: string;
  user_id: string;
  title: string;
  objective: string;
  status: "draft" | "active" | "completed" | "paused";
  week_number: number;
  kpi_primary: string | null;
  kpi_baseline: number | null;
  kpi_target: number | null;
  created_at: string;
  updated_at: string;
};

export type Move = {
  id: string;
  campaign_id: string;
  title: string;
  objective: string | null;
  status: "draft" | "ready" | "shipped" | "completed";
  channel: "email" | "social" | "web" | "direct" | "other";
  due_date: string | null;
  shipped_date: string | null;
  proof_url: string | null;
  proof_screenshot: string | null;
  asset_count: number;
  created_at: string;
  updated_at: string;
};

export type Asset = {
  id: string;
  move_id: string | null;
  type: "email" | "carousel" | "script" | "image" | "video" | "copy" | "other";
  content: Record<string, any>;
  version: number;
  created_at: string;
};

export type Toast = {
  id: string;
  type: "success" | "error" | "info" | "warning";
  message: string;
  duration?: number;
};
