import Link from "next/link";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

export default function ContactPage() {
  return (
    <main className="relative">
      <Navbar />
      <div className="pt-24 bg-[var(--bg-primary)]">
        <div className="max-w-3xl mx-auto px-6 py-16 space-y-8">
          <header className="space-y-3">
            <h1 className="font-display text-4xl md:text-5xl font-semibold text-[var(--text-primary)]">
              Contact
            </h1>
            <p className="text-[var(--text-secondary)]">
              Reconstruction mode is active: billing and auth are disabled. If you need sales or
              support, use the links below.
            </p>
          </header>

          <section className="rounded-2xl border border-[var(--border)] bg-[var(--bg-secondary)] p-6 space-y-4">
            <div className="space-y-1">
              <h2 className="font-display text-xl font-semibold text-[var(--text-primary)]">
                Email
              </h2>
              <p className="text-sm text-[var(--text-secondary)]">
                <a
                  className="text-[var(--accent)] hover:underline"
                  href="mailto:support@raptorflow.com"
                >
                  support@raptorflow.com
                </a>
              </p>
            </div>

            <div className="space-y-1">
              <h2 className="font-display text-xl font-semibold text-[var(--text-primary)]">
                Open The App
              </h2>
              <p className="text-sm text-[var(--text-secondary)]">
                Go to{" "}
                <Link className="text-[var(--accent)] hover:underline" href="/dashboard">
                  /dashboard
                </Link>{" "}
                (no login required).
              </p>
            </div>

            <div className="text-xs text-[var(--text-muted)] font-mono">
              Tenant boundary: <span className="text-[var(--text-primary)]">x-workspace-id</span>
            </div>
          </section>
        </div>

        <Footer />
      </div>
    </main>
  );
}

