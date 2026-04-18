export const publicEnv = {
  appUrl: process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000",
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8080",
  offlineMode: process.env.NEXT_PUBLIC_OFFLINE_MODE === "true",
  appEnv: process.env.NEXT_PUBLIC_APP_ENV ?? "dev",
  devBearerToken: process.env.NEXT_PUBLIC_DEV_BEARER_TOKEN ?? "raptorflow-dev-token",
} as const;
