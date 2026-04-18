import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";
import type { NextFetchEvent, NextRequest } from "next/server";

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
  "/api/internal(.*)"
]);

const isAppRoute = createRouteMatcher([
  "/app(.*)",
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
  "/ripples(.*)"
]);

const productionMiddleware = clerkMiddleware(async (auth, request) => {
  if (isProtectedRoute(request)) {
    await auth.protect();
  }

  return NextResponse.next();
});

export default function middleware(request: NextRequest, event: NextFetchEvent) {
  if (process.env.NODE_ENV !== "production") {
    return NextResponse.next();
  }

  return productionMiddleware(request, event);
}

export const config = {
  matcher: ["/((?!_next|.*\\..*).*)", "/(api|trpc)(.*)"]
};
