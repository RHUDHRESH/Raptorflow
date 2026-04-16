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

const isAppRoute = createRouteMatcher(["/app(.*)"]);
const isFoundationManagement = createRouteMatcher(["/app/foundation(.*)"]);

export default clerkMiddleware(async (auth, request) => {
  if (isProtectedRoute(request)) {
    await auth.protect();

    // FOUNDATION GATE: Block internal app access until Foundation is complete
    const isFoundationComplete = request.cookies.get("foundation_complete");
    if (isAppRoute(request) && !isFoundationManagement(request) && !isFoundationComplete) {
      const url = new URL("/foundation/1", request.url);
      return Response.redirect(url);
    }
  }
});

export const config = {
  matcher: ["/((?!_next|.*\\..*).*)", "/(api|trpc)(.*)"]
};
