import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

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
  "/intel(.*)",
  "/nudges(.*)",
  "/content(.*)",
  "/uploads(.*)",
  "/ripples(.*)",
  "/internal(.*)",
  "/api/internal(.*)",
  "/create-workspace(.*)",
]);

export default clerkMiddleware(async (auth, request) => {
  if (isProtectedRoute(request)) {
    await auth.protect();
  }

  return NextResponse.next();
});

export const config = {
  matcher: ["/((?!_next|.*\\..*).*)", "/(api|trpc)(.*)"],
};
