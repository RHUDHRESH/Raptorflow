"use client";

import { COPY } from "@/lib/copy";
import { Section } from "@/components/system/Section";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dice6 } from "lucide-react";

export function IdeaEngine() {
  return (
    <Section className="py-16 lg:py-24">
      <div className="text-center mb-12 space-y-4">
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-rf-ink">
          {COPY.ideas.title}
        </h2>
        <p className="text-lg sm:text-xl text-rf-subtle max-w-3xl mx-auto">
          {COPY.ideas.subheading}
        </p>
      </div>

      {/* Idea Engine Card */}
      <div className="max-w-3xl mx-auto">
        <Card className="bg-rf-card/50 border-rf-mineshaft/50 backdrop-blur-sm rounded-2xl p-8 lg:p-12">
          {/* Icon at top */}
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 rounded-full bg-rf-accent/20 border border-rf-accent/30 flex items-center justify-center">
              <Dice6 className="w-8 h-8 text-rf-accent" />
            </div>
          </div>

          {/* Example idea chips */}
          <div className="space-y-4">
            {COPY.ideas.examples.map((example, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-rf-card/70 border border-rf-mineshaft/30 hover:border-rf-accent/30 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <Dice6 className="w-5 h-5 text-rf-accent mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-rf-ink text-sm leading-relaxed">{example}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Additional hint text */}
          <p className="text-center text-sm text-rf-subtle mt-6">
            Our AI continuously monitors trends and matches them to your personas
          </p>
        </Card>
      </div>
    </Section>
  );
}
