"use client";

import { Section } from "@/components/system/Section";
import { Button } from "@/components/ui/button";
import { COPY } from "@/lib/copy";

export function BottomCTA() {
  return (
    <Section className="py-16">
      <div className="bg-rf-card/50 border border-rf-mineshaft/50 rounded-2xl p-12 text-center backdrop-blur-sm">
        <h2 className="text-3xl sm:text-4xl font-bold text-rf-ink mb-4">
          {COPY.cta.title}
        </h2>
        <p className="text-lg text-rf-subtle mb-8 max-w-2xl mx-auto">
          {COPY.cta.description}
        </p>
        <Button
          size="lg"
          className="bg-rf-accent hover:bg-rf-accent/90 text-white px-8 py-6 text-lg"
        >
          {COPY.cta.button}
        </Button>
      </div>
    </Section>
  );
}

