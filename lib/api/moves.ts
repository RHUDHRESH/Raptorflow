import { supabase } from "./supabase";
import { Move } from "@/lib/types";

export async function getMoves(campaignId?: string): Promise<Move[]> {
  let query = supabase.from("moves").select("*");

  if (campaignId) {
    query = query.eq("campaign_id", campaignId);
  }

  const { data, error } = await query.order("due_date", { ascending: true });

  if (error) throw error;
  return data || [];
}

export async function getTodaysMoves(): Promise<Move[]> {
  const today = new Date().toISOString().split("T")[0];
  const tomorrow = new Date(Date.now() + 86400000)
    .toISOString()
    .split("T")[0];

  const { data, error } = await supabase
    .from("moves")
    .select("*")
    .gte("due_date", today)
    .lt("due_date", tomorrow)
    .order("due_date", { ascending: true });

  if (error) throw error;
  return data || [];
}

export async function getMoveById(id: string): Promise<Move | null> {
  const { data, error } = await supabase
    .from("moves")
    .select("*")
    .eq("id", id)
    .single();

  if (error && error.code !== "PGRST116") throw error;
  return data || null;
}

export async function createMove(
  move: Omit<Move, "id" | "created_at" | "updated_at" | "asset_count">
): Promise<Move> {
  const { data, error } = await supabase
    .from("moves")
    .insert([{ ...move, asset_count: 0 }])
    .select()
    .single();

  if (error) throw error;
  return data;
}

export async function updateMove(
  id: string,
  updates: Partial<Move>
): Promise<Move> {
  const { data, error } = await supabase
    .from("moves")
    .update(updates)
    .eq("id", id)
    .select()
    .single();

  if (error) throw error;
  return data;
}

export async function shipMove(
  id: string,
  proofUrl: string,
  proofScreenshot?: string
): Promise<Move> {
  return updateMove(id, {
    status: "shipped",
    shipped_date: new Date().toISOString(),
    proof_url: proofUrl,
    proof_screenshot: proofScreenshot,
  });
}

export async function deleteMove(id: string): Promise<void> {
  const { error } = await supabase.from("moves").delete().eq("id", id);

  if (error) throw error;
}
