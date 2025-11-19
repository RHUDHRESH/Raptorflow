"use client";

import { COPY } from "@/lib/copy";
import { Section } from "@/components/system/Section";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function ValueTrio() {
  return (
    <Section id="features" className="py-16 lg:py-24">
      <div className="text-center mb-12 space-y-4">
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-rf-ink">
          {COPY.valueTrio.title}
        </h2>
        <p className="text-lg sm:text-xl text-rf-subtle max-w-3xl mx-auto">
          {COPY.valueTrio.subheading}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
        {COPY.valueTrio.cards.map((card, index) => (
          <Card
            key={index}
            className={cn(
              "bg-rf-card/50 border-rf-mineshaft/50 backdrop-blur-sm",
              "hover:bg-rf-card/70 hover:border-rf-mineshaft/70 transition-all duration-300",
              "hover:shadow-rf hover:-translate-y-1",
              "rounded-2xl"
            )}
          >
            <CardHeader>
              <div className="text-4xl mb-4">{card.icon}</div>
              <CardTitle className="text-rf-ink text-xl">{card.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-rf-subtle text-base leading-relaxed">
                {card.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </Section>
  );
}
