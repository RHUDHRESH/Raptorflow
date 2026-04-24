import Pusher from "pusher";

export const pusherServer = new Pusher({
  appId: process.env.PUSHER_APP_ID ?? "app_id",
  key: process.env.PUSHER_KEY ?? "app_key",
  secret: process.env.PUSHER_SECRET ?? "app_secret",
  cluster: process.env.PUSHER_CLUSTER ?? "ap2",
  useTLS: true,
});

export const channels = {
  user: (userId: string) => `private-user-${userId}`,
  council: (sessionId: string) => `private-council-${sessionId}`,
  campaign: (campaignId: string) => `private-campaign-${campaignId}`,
};

export const events = {
  COUNCIL_POSITION_ADDED: "council.position.added",
  COUNCIL_STATUS_CHANGED: "council.status.changed",
  COUNCIL_COMPLETE: "council.complete",
  FOUNDATION_SAVED: "foundation.saved",
  FOUNDATION_SCAN_COMPLETE: "foundation.scan.complete",
  CAMPAIGN_EVALUATED: "campaign.evaluated",
  MOVES_GENERATED: "moves.generated",
  TASK_UPDATED: "task.updated",
  DAILY_WIN_READY: "daily.win.ready",
  NUDGE_CREATED: "nudge.created",
  INTEL_SIGNAL: "intel.signal",
};

export async function broadcast(
  channel: string,
  event: string,
  data: Record<string, unknown>,
): Promise<void> {
  try {
    await pusherServer.trigger(channel, event, data);
    console.log(`PUSHER broadcast: ${channel} → ${event}`);
  } catch (err) {
    console.error(`PUSHER broadcast failed: ${channel} → ${event}`, err);
  }
}
