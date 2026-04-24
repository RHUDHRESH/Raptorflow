import { NextResponse } from "next/server";
import { ensureCollection } from "@/lib/qdrant/setup";

export const dynamic = "force-dynamic";

let collectionInitialized = false;

export async function GET(): Promise<NextResponse> {
  if (!collectionInitialized) {
    try {
      await ensureCollection();
      collectionInitialized = true;
    } catch (err) {
      console.error("[health] Qdrant collection init failed:", err);
    }
  }

  return NextResponse.json({
    ok: true,
    app: "web",
    qdrant: collectionInitialized ? "ready" : "init_failed",
    timestamp: new Date().toISOString(),
  });
}
