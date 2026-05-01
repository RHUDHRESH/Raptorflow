"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";
import { getApiBaseUrl } from "@/lib/api";

/**
 * Foundation Screen 1: The URL Entry
 * The first impression of RaptorFlow. Minimal, premium, and focused.
 */
export default function FoundationStep1() {
  const router = useRouter();
  const { getToken } = useAuth();
  const setSectionData = useFoundationStore((s) => s.setSectionData);
  const setStep = useFoundationStore((s) => s.setStep);

  // Local state
  const [url, setUrl] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Staggered entry animation trigger
  useEffect(() => {
    setStep(1);
    setMounted(true);
  }, [setStep]);

  /**
   * Validate and submit the URL
   */
  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    setError(null);

    let validatedUrl = url.trim();
    if (!validatedUrl) return;

    // 1. Auto-prepend https:// if protocol is missing
    if (!/^https?:\/\//i.test(validatedUrl)) {
      validatedUrl = `https://${validatedUrl}`;
    }

    // 2. Basic URL format validation
    const urlPattern = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/i;
    if (!urlPattern.test(validatedUrl)) {
      setError("This doesn't look like a valid URL. Try: https://yourcompany.com");
      return;
    }

    setIsLoading(true);

    try {
      const token = await getToken();

      // Save to store immediately
      setSectionData("url", { url: validatedUrl });

      // Fire the scan start
      const response = await fetch(`${getApiBaseUrl()}/api/v1/foundation/scan/start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ url: validatedUrl }),
      });

      const data = await response.json();

      if (response.ok && data.status === "started") {
        // Navigate to Step 2 (Scan Results)
        router.push("/foundation/2");
      } else {
        // Handle reachable/system errors from API
        const errorMsg =
          data.message || "We couldn't reach this website. Please check the address and try again.";
        setError(errorMsg);
        setIsLoading(false);
      }
    } catch (err) {
      console.error("[Foundation1] Submit Error:", err);
      setError("Something went wrong. Please try again.");
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#FBF8F2] px-6">
      <div className="flex w-full max-w-[440px] flex-col items-center">
        {/* WORDMARK */}
        <div
          className={cn(
            "mb-4 transition-all duration-500 ease-out",
            mounted ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0",
          )}
        >
          <h1 className="text-4xl font-bold tracking-tighter text-[#2A2622]">RaptorFlow</h1>
        </div>

        {/* SEPARATOR */}
        <div
          className={cn(
            "mb-10 w-16 h-[1px] bg-[#f59e0b] transition-all duration-500 ease-out delay-[100ms]",
            mounted ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0",
          )}
        />

        {/* QUESTION */}
        <p
          className={cn(
            "mb-8 text-center text-xl text-[#2A2622] transition-all duration-500 ease-out delay-[200ms]",
            mounted ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0",
          )}
        >
          What is your business website?
        </p>

        {/* INPUT STACK */}
        <form
          onSubmit={handleSubmit}
          className={cn(
            "w-full space-y-4 transition-all duration-500 ease-out delay-[300ms]",
            mounted ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0",
          )}
        >
          <input
            autoFocus
            type="text"
            placeholder="yourcompany.com"
            disabled={isLoading}
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full bg-[#262626] border border-[#D5CBC0] rounded-xl px-5 py-3 text-lg text-[#2A2622] placeholder:text-[#6B655E] focus:outline-none focus:border-[#f59e0b] transition-colors"
          />

          <div
            className={cn(
              "pt-2 transition-all duration-500 ease-out delay-[400ms]",
              mounted ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0",
            )}
          >
            <button
              type="submit"
              disabled={isLoading || !url.trim()}
              className="relative w-full md:w-auto md:min-w-[280px] flex items-center justify-center gap-3 bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-[#D5CBC0] disabled:opacity-50 text-black font-semibold rounded-lg px-8 py-3 mx-auto transition-all"
            >
              {isLoading ? (
                <>
                  <span>Scanning your website...</span>
                  <div className="w-2 h-2 rounded-full bg-black animate-pulse" />
                </>
              ) : (
                "Begin building your office"
              )}
            </button>
          </div>

          {/* ERROR MESSAGE */}
          {error && <p className="pt-2 text-center text-sm text-red-400">{error}</p>}
        </form>
      </div>
    </div>
  );
}
