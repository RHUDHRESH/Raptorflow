"use client";

import { Section } from "@/components/system/Section";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { COPY } from "@/lib/copy";
import { Check } from "lucide-react";

const plans = [
  {
    name: "Starter",
    price: "$29",
    period: "/month",
    description: "Perfect for getting started",
    features: [
      "30-day planning",
      "ICP targeting",
      "Content ideas",
      "Basic asset generation",
    ],
  },
  {
    name: "Pro",
    price: "$79",
    period: "/month",
    description: "For serious marketers",
    features: [
      "Everything in Starter",
      "Advanced psychographics",
      "Multi-channel campaigns",
      "Priority support",
      "Custom integrations",
    ],
    popular: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "For teams and agencies",
    features: [
      "Everything in Pro",
      "Team collaboration",
      "White-label options",
      "Dedicated support",
      "Custom workflows",
    ],
  },
];

export function PricingTable() {
  return (
    <Section id="pricing" className="py-16">
      <h2 className="text-3xl sm:text-4xl font-bold text-center text-rf-ink mb-12">
        {COPY.pricing.title}
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((plan) => (
          <Card
            key={plan.name}
            className={`bg-rf-card/50 border-rf-mineshaft/50 backdrop-blur-sm ${
              plan.popular ? "border-rf-accent border-2" : ""
            }`}
          >
            <CardHeader>
              {plan.popular && (
                <div className="text-xs font-semibold text-rf-accent mb-2">POPULAR</div>
              )}
              <CardTitle className="text-rf-ink text-2xl">{plan.name}</CardTitle>
              <CardDescription className="text-rf-subtle">{plan.description}</CardDescription>
              <div className="mt-4">
                <span className="text-4xl font-bold text-rf-ink">{plan.price}</span>
                {plan.period && (
                  <span className="text-rf-subtle ml-2">{plan.period}</span>
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
                className={`w-full ${
                  plan.popular
                    ? "bg-rf-accent hover:bg-rf-accent/90"
                    : "bg-rf-mineshaft hover:bg-rf-mineshaft/80"
                }`}
              >
                Get started
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </Section>
  );
}

