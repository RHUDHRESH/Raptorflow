"use client";

import { useEffect } from "react";
import { getPusherClient } from "./client";

export function usePusherEvent<T>(
  channel: string,
  event: string,
  handler: (data: T) => void,
): void {
  useEffect(() => {
    const pusher = getPusherClient();
    const sub = pusher.subscribe(channel);
    sub.bind(event, handler);
    return () => {
      sub.unbind(event, handler);
      pusher.unsubscribe(channel);
    };
  }, [channel, event, handler]);
}

export function useUserEvent<T>(userId: string, event: string, handler: (data: T) => void): void {
  usePusherEvent(`private-user-${userId}`, event, handler);
}
