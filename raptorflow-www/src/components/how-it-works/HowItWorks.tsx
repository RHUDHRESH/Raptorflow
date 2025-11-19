"use client";

import { COPY } from "@/lib/copy";
import { Section } from "@/components/system/Section";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Plug, FileText, CheckCircle } from "lucide-react";

const iconMap = {
  1: Plug,
  2: FileText,
  3: CheckCircle,
};

export function HowItWorks() {
  return (
    <Section id="how-it-works" className="py-16 lg:py-24">
      <div className="text-center mb-12 space-y-4">
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-rf-ink">
          {COPY.howItWorks.title}
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
        {COPY.howItWorks.steps.map((step) => {
          const Icon = iconMap[step.number as keyof typeof iconMap] || Plug;
          return (
            <Card
              key={step.number}
              className={cn(
                "bg-rf-card/50 border-rf-mineshaft/50 backdrop-blur-sm",
                "hover:bg-rf-card/70 hover:border-rf-mineshaft/70 transition-all duration-300",
                "hover:shadow-rf hover:-translate-y-1",
                "rounded-2xl relative"
              )}
            >
              <CardHeader>
                {/* Numbered circle */}
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-12 h-12 rounded-full bg-rf-accent/20 border border-rf-accent/30 flex items-center justify-center flex-shrink-0">
                    <span className="text-xl font-bold text-rf-accent">{step.number}</span>
                  </div>
                  <div className="w-10 h-10 rounded-lg bg-rf-mineshaft/30 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-rf-subtle" />
                  </div>
                </div>
                <CardTitle className="text-rf-ink text-xl">{step.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-rf-subtle leading-relaxed">{step.description}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </Section>
  );
}

