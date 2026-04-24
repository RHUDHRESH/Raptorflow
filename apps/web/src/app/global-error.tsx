"use client";

import * as React from "react";
import Link from "next/link";
import * as Sentry from "@sentry/nextjs";
import { Button } from "@/components/ui/button";
import {
  ExclamationTriangleIcon,
  UpdateIcon,
  HomeIcon,
} from "@radix-ui/react-icons";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}): React.ReactElement {
  React.useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <html lang="en">
      <body className="min-h-screen bg-[#FBF8F2] text-[#13141A] antialiased">
        <main className="flex min-h-screen items-center justify-center p-6">
          <div className="w-full max-w-xl border border-red-200 bg-white p-8 shadow-[0_24px_80px_rgba(127,29,29,0.08)]">
            <div className="mb-5 inline-flex h-12 w-12 items-center justify-center rounded-full bg-red-50 text-red-600">
              <ExclamationTriangleIcon className="h-6 w-6" />
            </div>
            <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.3em] text-red-600">
              Global application error
            </p>
            <h1 className="mb-3 text-2xl font-semibold tracking-tight">
              Something broke at the root boundary
            </h1>
            <p className="mb-6 text-sm leading-6 text-[#5E5A53]">
              The application hit an unexpected error. Sentry has been notified
              so the failure can be inspected with the current release, route,
              and stack trace.
            </p>
            {error.digest ? (
              <p className="mb-6 rounded bg-[#F7F4EE] px-3 py-2 font-mono text-xs text-[#6B655E]">
                Digest: {error.digest}
              </p>
            ) : null}
            <div className="flex flex-col gap-3 sm:flex-row">
              <Button
                type="button"
                onClick={() => reset()}
                className="h-11 bg-black text-white hover:bg-black/90"
              >
                <UpdateIcon className="mr-2 h-4 w-4" />
                Try again
              </Button>
              <Button asChild variant="outline" className="h-11 bg-transparent">
                <Link href="/">
                  <HomeIcon className="mr-2 h-4 w-4" />
                  Back home
                </Link>
              </Button>
            </div>
          </div>
        </main>
      </body>
    </html>
  );
}
