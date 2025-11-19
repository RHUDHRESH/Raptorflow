"use client";

import { Section } from "@/components/system/Section";
import { Button } from "@/components/ui/button";
import { COPY } from "@/lib/copy";

export function BottomCTA() {
  return (
    <Section className="py-16 lg:py-24">
      <div className="bg-rf-card/50 border border-rf-mineshaft/50 rounded-2xl p-12 lg:p-16 text-center backdrop-blur-sm max-w-5xl mx-auto">
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-rf-ink mb-6">
          {COPY.cta.title}
        </h2>
        <p className="text-lg sm:text-xl text-rf-subtle mb-10 max-w-3xl mx-auto leading-relaxed">
          {COPY.cta.subheading}
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button
            size="lg"
            className="bg-rf-accent hover:bg-rf-accent/90 text-white px-8 py-6 text-lg rounded-xl"
          >
            {COPY.cta.ctaPrimary}
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="border-rf-mineshaft text-rf-ink hover:bg-rf-card px-8 py-6 text-lg rounded-xl"
          >
            {COPY.cta.ctaSecondary}
          </Button>
        </div>
      </div>
    </Section>
  );
}
