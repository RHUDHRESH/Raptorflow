interface HandlerContext {
  userMessage: string;
  conversationHistory: Array<{ role: string; content: string }>;
  clerkUserId: string;
}

export async function handleTactical(_ctx: HandlerContext): Promise<string> {
  throw new Error("migrated_to_rust_api: handleTactical is no longer available");
}

export async function handleStrategic(_ctx: HandlerContext): Promise<string> {
  throw new Error("migrated_to_rust_api: handleStrategic is no longer available");
}

export async function handleCampaign(_ctx: HandlerContext): Promise<string> {
  throw new Error("migrated_to_rust_api: handleCampaign is no longer available");
}

export async function handleCouncil(
  _ctx: HandlerContext,
): Promise<{ response: string; sessionId: string }> {
  throw new Error("migrated_to_rust_api: handleCouncil is no longer available");
}

export async function handleFoundation(_ctx: HandlerContext): Promise<string> {
  throw new Error("migrated_to_rust_api: handleFoundation is no longer available");
}

export async function routeHandler(
  route: string,
  ctx: HandlerContext,
): Promise<{ response: string; sessionId?: string }> {
  throw new Error(`migrated_to_rust_api: routeHandler for ${route} is no longer available`);
}
