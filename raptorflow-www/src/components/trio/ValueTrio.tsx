"use client";

import { Target, Users, Sparkles } from "lucide-react";
import { COPY } from "@/lib/copy";
import { Section } from "@/components/system/Section";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const iconMap = {
  target: Target,
  users: Users,
  sparkles: Sparkles,
};

export function ValueTrio() {
  return (
    <Section id="features" className="py-16">
      <h2 className="text-3xl sm:text-4xl font-bold text-center text-rf-ink mb-12">
        {COPY.valueTrio.title}
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {COPY.valueTrio.cards.map((card, index) => {
          const Icon = iconMap[card.icon as keyof typeof iconMap] || Target;
          return (
            <Card
              key={index}
              className={cn(
                "bg-rf-card/50 border-rf-mineshaft/50 backdrop-blur-sm",
                "hover:bg-rf-card/70 transition-all duration-300"
              )}
            >
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-rf-accent/20 flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-rf-accent" />
                </div>
                <CardTitle className="text-rf-ink">{card.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-rf-subtle text-base">
                  {card.description}
                </CardDescription>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </Section>
  );
}

