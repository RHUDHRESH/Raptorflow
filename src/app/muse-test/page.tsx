"use client";

export default function MuseTestPage() {
    return (
        <div className="h-screen bg-[var(--background)] p-8">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-2xl font-bold text-[var(--ink)] mb-4">
                    Muse Vertex AI Test Page
                </h1>
                <div className="bg-[var(--paper)] border border-[var(--ink)] p-6 rounded-lg">
                    <h2 className="text-lg font-semibold text-[var(--ink)] mb-2">
                        Status: Testing
                    </h2>
                    <p className="text-[var(--muted)]">
                        This is a simple test page to verify the route works.
                    </p>
                    <div className="mt-4">
                        <button className="bg-[var(--blueprint)] text-[var(--paper)] px-4 py-2 rounded">
                            Test Button
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
