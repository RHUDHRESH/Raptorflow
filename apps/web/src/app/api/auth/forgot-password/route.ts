import { NextResponse } from "next/server";

export async function POST(): Promise<NextResponse> {
  return NextResponse.json(
    {
      error: "clerk_auth_managed",
      message: "Password recovery is handled by Clerk through the configured sign-in flow.",
    },
    { status: 410 },
  );
}
