"use client";

import { Section } from "@/components/system/Section";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { COPY } from "@/lib/copy";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

export function PricingTable() {
  return (
    <Section id="pricing" className="py-16 lg:py-24">
      <div className="text-center mb-12 space-y-4">
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-rf-ink">
          {COPY.pricing.title}
        </h2>
        <p className="text-lg sm:text-xl text-rf-subtle max-w-3xl mx-auto">
          {COPY.pricing.subheading}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 max-w-6xl mx-auto mb-12">
        {COPY.pricing.plans.map((plan) => (
          <Card
            key={plan.name}
            className={cn(
              "bg-rf-card/50 border-rf-mineshaft/50 backdrop-blur-sm rounded-2xl",
              "hover:shadow-rf transition-all duration-300",
              "recommended" in plan && plan.recommended
                ? "border-rf-accent/50 ring-2 ring-rf-accent/20 md:-mt-4 md:mb-4"
                : ""
            )}
          >
            <CardHeader>
              {"recommended" in plan && plan.recommended && (
                <Badge className="bg-rf-accent/20 text-rf-accent border-rf-accent/30 w-fit mb-2">
                  Recommended
                </Badge>
              )}
              <CardTitle className="text-rf-ink text-2xl">{plan.name}</CardTitle>
              <div className="mt-4">
                <span className="text-4xl font-bold text-rf-ink">{plan.price}</span>
                {plan.period && (
                  <span className="text-rf-subtle ml-2 text-lg">{plan.period}</span>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3 mb-6">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start">
                    <Check className="w-5 h-5 text-rf-accent mr-2 flex-shrink-0 mt-0.5" />
                    <span className="text-rf-subtle">{feature}</span>
                  </li>
                ))}
              </ul>
              <Button
                className={cn(
                  "w-full",
                  "recommended" in plan && plan.recommended
                    ? "bg-rf-accent hover:bg-rf-accent/90 text-white"
                    : "bg-rf-mineshaft hover:bg-rf-mineshaft/80 text-rf-ink"
                )}
                size="lg"
              >
                {plan.cta}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Enterprise Panel */}
      <div className="max-w-4xl mx-auto">
        <Card className="bg-rf-card/30 border-rf-mineshaft/30 backdrop-blur-sm rounded-2xl">
          <CardHeader>
            <CardTitle className="text-rf-ink text-2xl">{COPY.pricing.enterprise.title}</CardTitle>
            <CardDescription className="text-rf-subtle text-base mt-2">
              {COPY.pricing.enterprise.description}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="border-rf-mineshaft text-rf-ink hover:bg-rf-card">
              {COPY.pricing.enterprise.cta}
            </Button>
          </CardContent>
        </Card>
      </div>
    </Section>
  );
}
