"use client";

export default function SentryExamplePage(): React.ReactElement {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8 gap-8">
      <h1 className="text-3xl font-bold">Sentry Test Page</h1>
      <p className="text-lg text-muted-foreground">
        Click the button below to trigger a test error that will be sent to
        Sentry.
      </p>

      <div className="flex gap-4">
        <button
          onClick={() => {
            // This will throw an error that Sentry will capture
            myUndefinedFunction();
          }}
          className="px-6 py-3 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors"
        >
          Trigger Test Error
        </button>

        <button
          onClick={() => {
            // This will throw a captured error
            throw new Error("Manual test error from Sentry test page!");
          }}
          className="px-6 py-3 bg-amber-600 text-white font-semibold rounded-lg hover:bg-amber-700 transition-colors"
        >
          Throw Error
        </button>
      </div>

      <div className="mt-8 p-4 bg-muted rounded-lg">
        <h2 className="text-lg font-semibold mb-2">Sentry Status</h2>
        <p className="text-sm">
          If Sentry is configured correctly, both buttons above should create
          issues in your Sentry dashboard.
        </p>
        <p className="text-sm mt-2">
          Project: <code className="bg-background px-1 rounded">javascript-nextjs</code>
        </p>
        <p className="text-sm">
          Organization: <code className="bg-background px-1 rounded">raptorflow</code>
        </p>
      </div>
    </main>
  );
}