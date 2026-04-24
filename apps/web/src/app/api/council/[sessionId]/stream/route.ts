import { NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";
import { createSSEStream, sseResponse } from "@/lib/sse/stream";

export const dynamic = "force-dynamic";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ sessionId: string }> },
): Promise<Response> {
  const { sessionId } = await params;
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const session = await prisma.councilSession.findFirst({
    where: { id: sessionId, clerkUserId: userId },
    include: { positions: { orderBy: { createdAt: "asc" } } },
  });
  if (!session) return NextResponse.json({ error: "Not found" }, { status: 404 });

  const { stream, send, close } = createSSEStream();

  send("session", {
    status: session.status,
    positionCount: session.positions.length,
    positions: session.positions,
    synthesisResult: session.synthesisResult,
  });

  if (session.status === "complete" || session.status === "failed") {
    send("done", { status: session.status });
    close();
    return sseResponse(stream);
  }

  let lastPositionCount = session.positions.length;
  let lastStatus = session.status;
  let closed = false;

  const interval = setInterval(async () => {
    if (closed) {
      clearInterval(interval);
      return;
    }

    try {
      const updated = await prisma.councilSession.findUnique({
        where: { id: sessionId },
        include: { positions: { orderBy: { createdAt: "asc" } } },
      });

      if (!updated) {
        clearInterval(interval);
        closed = true;
        close();
        return;
      }

      if (updated.positions.length > lastPositionCount) {
        const newPositions = updated.positions.slice(lastPositionCount);
        for (const position of newPositions) {
          send("position", position);
        }
        lastPositionCount = updated.positions.length;
      }

      if (updated.status !== lastStatus) {
        send("status", { status: updated.status });
        lastStatus = updated.status;
      }

      if (updated.status === "complete") {
        send("synthesis", { synthesisResult: updated.synthesisResult });
        send("done", { status: "complete" });
        clearInterval(interval);
        closed = true;
        close();
      }

      if (updated.status === "failed") {
        send("done", { status: "failed" });
        clearInterval(interval);
        closed = true;
        close();
      }
    } catch (err) {
      console.error("SSE poll error:", err);
    }
  }, 2000);

  _request.signal.addEventListener("abort", () => {
    closed = true;
    clearInterval(interval);
    close();
  });

  return sseResponse(stream);
}
