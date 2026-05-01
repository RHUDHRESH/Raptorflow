"use client";

import * as Sentry from "@sentry/nextjs";

export default function SentryExamplePage(): React.ReactElement {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-8 p-8">
      <h1 className="text-3xl font-bold">Sentry Test Page</h1>
      <p className="text-lg text-muted-foreground">
        Click a button to send a manual event and then throw a test error into Sentry.
      </p>

      <div className="flex gap-4">
        <button
          onClick={() => {
            Sentry.captureMessage("RaptorFlow Sentry test page: captureMessage");
            // This will throw an error that Sentry will capture.
            // @ts-expect-error Intentionally calling undefined function for Sentry test.
            myUndefinedFunction();
          }}
          className="rounded-lg bg-red-600 px-6 py-3 font-semibold text-white transition-colors hover:bg-red-700"
        >
          Trigger Test Error
        </button>

        <button
          onClick={() => {
            Sentry.captureException(new Error("Manual test error from Sentry test page."));
            throw new Error("Manual test error from Sentry test page!");
          }}
          className="rounded-lg bg-amber-600 px-6 py-3 font-semibold text-white transition-colors hover:bg-amber-700"
        >
          Throw Error
        </button>
      </div>

      <div className="mt-8 rounded-lg bg-muted p-4">
        <h2 className="mb-2 text-lg font-semibold">Sentry Status</h2>
        <p className="text-sm">
          If Sentry is configured correctly, both buttons above should create issues in your Sentry
          dashboard.
        </p>
        <p className="mt-2 text-sm">
          Project: <code className="rounded bg-background px-1">javascript-nextjs</code>
        </p>
        <p className="text-sm">
          Organization: <code className="rounded bg-background px-1">raptorflow</code>
        </p>
      </div>
    </main>
  );
}
