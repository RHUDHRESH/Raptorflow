import PusherClient from "pusher-js";

let pusherInstance: PusherClient | null = null;

export function getPusherClient(): PusherClient {
  if (!pusherInstance) {
    pusherInstance = new PusherClient(process.env.NEXT_PUBLIC_PUSHER_KEY ?? "app_key", {
      cluster: process.env.NEXT_PUBLIC_PUSHER_CLUSTER ?? "ap2",
      authEndpoint: "/api/pusher/auth",
    });
  }
  return pusherInstance;
}
