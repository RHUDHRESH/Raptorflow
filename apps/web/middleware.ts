import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isProtectedRoute = createRouteMatcher([
  "/app(.*)",
  "/foundation(.*)",
  "/campaigns(.*)",
  "/office(.*)",
  "/muse(.*)",
  "/council(.*)",
  "/daily-wins(.*)",
  "/billing(.*)",
  "/settings(.*)",
  "/internal(.*)",
  "/api/internal(.*)"
]);

export default clerkMiddleware(async (auth, request) => {
  if (isProtectedRoute(request)) {
    await auth.protect();
  }
});

export const config = {
  matcher: ["/((?!_next|.*\\..*).*)", "/(api|trpc)(.*)"]
};
