"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { Loader2 } from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";

/**
 * Foundation Index Page
 * Acts as a router to direct the user to the correct step or management page.
 */
export default function FoundationIndex() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { setStep, setStatus } = useFoundationStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function checkFoundationStatus() {
      try {
        const token = await getToken();
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/snapshot`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (!response.ok) {
          // Fallback to starting point if API fails or user is new
          router.replace("/foundation/1");
          return;
        }

        const data = await response.json();
        const { status, current_step } = data;

        // Update local store
        setStep(current_step || 1);
        setStatus(status || "incomplete");

        if (status === "complete") {
          // User finished onboarding, go to Management page
          router.replace("/app/foundation");
        } else {
          // User is mid-flow or starting
          const nextStep = current_step || 1;
          router.replace(`/foundation/${nextStep}`);
        }
      } catch (err) {
        console.error("[FoundationIndex] Error fetching snapshot:", err);
        router.replace("/foundation/1");
      } finally {
        setLoading(false);
      }
    }

    checkFoundationStatus();
  }, [getToken, router, setStep, setStatus]);

  return (
    <div className="flex h-screen w-screen items-center justify-center bg-[#1a1a1a]">
      <div className="flex flex-col items-center gap-4">
        <Loader2 className="w-8 h-8 text-[#f59e0b] animate-spin" />
        <p className="text-zinc-500 text-sm font-medium tracking-widest uppercase">
          Mapping your foundation...
        </p>
      </div>
    </div>
  );
}
