import Link from "next/link";
import { ArrowLeft, ArrowRight } from "lucide-react";

import { getMarketingFeature } from "@/lib/marketingFeatures";

export default function FeatureDetailPage({ params }: { params: { slug: string } }) {
  const slug = params.slug;
  const feature = getMarketingFeature(slug);

  if (!feature) {
    return (
      <main className="min-h-screen bg-[var(--bg-primary)]">
        <div className="max-w-4xl mx-auto px-6 py-16">
          <Link
            href="/features"
            className="inline-flex items-center gap-2 text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
          >
            <ArrowLeft size={16} />
            Back to Features
          </Link>

          <h1 className="mt-10 font-display text-4xl md:text-5xl font-semibold text-[var(--text-primary)]">
            Feature Not Found
          </h1>
          <p className="mt-4 text-[var(--text-secondary)]">
            No feature page exists for <span className="font-mono">{slug}</span>.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/features"
              className="inline-flex items-center gap-2 text-sm font-semibold px-4 py-2 rounded-full bg-[var(--bg-tertiary)] border border-[var(--border-strong)] text-[var(--text-primary)] hover:border-[var(--accent)] transition-colors"
            >
              Browse Features
              <ArrowRight size={16} />
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 text-sm font-semibold px-4 py-2 rounded-full bg-[var(--text-primary)] text-[var(--bg-primary)] hover:opacity-90 transition-opacity"
            >
              Open Dashboard
              <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </main>
    );
  }

  const Icon = feature.icon;

  return (
    <main className="min-h-screen bg-[var(--bg-primary)]">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <div className="flex items-center justify-between gap-4">
          <Link
            href="/features"
            className="inline-flex items-center gap-2 text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
          >
            <ArrowLeft size={16} />
            Back to Features
          </Link>
          <div className="flex items-center gap-3">
            {feature.secondaryHref && feature.secondaryLabel && (
              <Link
                href={feature.secondaryHref}
                className="inline-flex items-center gap-2 text-sm font-semibold px-4 py-2 rounded-full bg-[var(--bg-secondary)] border border-[var(--border)] text-[var(--text-primary)] hover:border-[var(--accent)] transition-colors"
              >
                {feature.secondaryLabel}
                <ArrowRight size={16} />
              </Link>
            )}
            <Link
              href={feature.primaryHref}
              className="inline-flex items-center gap-2 text-sm font-semibold px-4 py-2 rounded-full bg-[var(--text-primary)] text-[var(--bg-primary)] hover:opacity-90 transition-opacity"
            >
              {feature.primaryLabel}
              <ArrowRight size={16} />
            </Link>
          </div>
        </div>

        <header className="mt-10 grid grid-cols-1 lg:grid-cols-2 gap-10 items-start">
          <div>
            <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-[var(--bg-tertiary)] border border-[var(--border)]">
              <Icon size={18} style={{ color: "var(--accent)" }} />
              <span className="text-xs font-semibold tracking-widest uppercase text-[var(--accent)]">
                {feature.subtitle}
              </span>
            </div>
            <h1 className="mt-6 font-display text-5xl md:text-6xl font-semibold text-[var(--text-primary)]">
              {feature.title}
            </h1>
            <p className="mt-6 text-lg text-[var(--text-secondary)] leading-relaxed">
              {feature.description}
            </p>

            <div className="mt-8">
              <h2 className="text-sm font-semibold tracking-widest uppercase text-[var(--text-muted)]">
                Included
              </h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {feature.highlights.map((highlight) => (
                  <span
                    key={highlight}
                    className="px-3 py-1.5 bg-[var(--bg-secondary)] border border-[var(--border)] rounded-full text-xs font-medium text-[var(--text-secondary)]"
                  >
                    {highlight}
                  </span>
                ))}
              </div>
            </div>

            <div className="mt-10 p-5 rounded-2xl bg-[var(--bg-secondary)] border border-[var(--border)]">
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                Reconstruction mode: the app runs without auth and payments. Workspace scoping is
                handled via a local workspace id, and API errors are surfaced instead of hidden.
              </p>
            </div>
          </div>

          <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-2xl overflow-hidden">
            <img
              src={feature.image}
              alt={feature.title}
              className="w-full h-[420px] object-cover"
              loading="lazy"
            />
          </div>
        </header>
      </div>
    </main>
  );
}
