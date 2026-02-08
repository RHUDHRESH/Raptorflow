import Link from "next/link";
import { ArrowLeft, ArrowRight } from "lucide-react";

import { MARKETING_FEATURES } from "@/lib/marketingFeatures";

export default function FeaturesIndexPage() {
  return (
    <main className="min-h-screen bg-[var(--bg-primary)]">
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="flex items-center justify-between gap-4">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
          >
            <ArrowLeft size={16} />
            Back to Home
          </Link>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 text-sm font-semibold px-4 py-2 rounded-full bg-[var(--bg-tertiary)] border border-[var(--border-strong)] text-[var(--text-primary)] hover:border-[var(--accent)] transition-colors"
          >
            Open Dashboard
            <ArrowRight size={16} />
          </Link>
        </div>

        <header className="mt-10">
          <h1 className="font-display text-5xl md:text-6xl font-semibold text-[var(--text-primary)]">
            Features
          </h1>
          <p className="mt-4 text-lg text-[var(--text-secondary)] max-w-2xl">
            Reconstruction mode: no login walls, no paywalls, no fake success states. If something
            fails, you will see it.
          </p>
        </header>

        <section className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-8">
          {MARKETING_FEATURES.map((feature) => {
            const Icon = feature.icon;
            return (
              <Link
                key={feature.slug}
                href={`/features/${feature.slug}`}
                className="group block bg-[var(--bg-secondary)] border border-[var(--border)] rounded-2xl overflow-hidden hover:border-[var(--accent)] transition-colors"
              >
                <div className="relative h-56 overflow-hidden">
                  <img
                    src={feature.image}
                    alt={feature.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                    loading="lazy"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-[var(--bg-secondary)] to-transparent" />
                  <div className="absolute top-4 left-4 w-14 h-14 bg-[var(--bg-primary)]/90 backdrop-blur-sm rounded-xl flex items-center justify-center border border-[var(--border)] group-hover:border-[var(--accent)] transition-colors duration-300">
                    <Icon size={28} style={{ color: "var(--accent)" }} />
                  </div>
                </div>

                <div className="p-8">
                  <span className="text-xs font-semibold tracking-widest uppercase text-[var(--accent)] mb-2 block">
                    {feature.subtitle}
                  </span>
                  <h2 className="font-display text-2xl font-semibold text-[var(--text-primary)] mb-3">
                    {feature.title}
                  </h2>
                  <p className="text-[var(--text-secondary)] mb-6 leading-relaxed">
                    {feature.description}
                  </p>

                  <div className="flex flex-wrap gap-2 mb-6">
                    {feature.highlights.map((highlight) => (
                      <span
                        key={highlight}
                        className="px-3 py-1.5 bg-[var(--bg-primary)] border border-[var(--border)] rounded-full text-xs font-medium text-[var(--text-secondary)] group-hover:border-[var(--accent)]/50 transition-colors"
                      >
                        {highlight}
                      </span>
                    ))}
                  </div>

                  <div className="inline-flex items-center gap-2 text-sm font-medium text-[var(--accent)] group-hover:text-[var(--accent-dark)] transition-colors">
                    View details <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>
            );
          })}
        </section>
      </div>
    </main>
  );
}

