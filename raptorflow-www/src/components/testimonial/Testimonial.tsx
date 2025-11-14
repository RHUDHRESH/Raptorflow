"use client";

import { COPY } from "@/lib/copy";
import { Section } from "@/components/system/Section";
import { Card } from "@/components/ui/card";
import { Quote } from "lucide-react";

export function Testimonial() {
  return (
    <Section className="py-16 lg:py-24">
      <div className="max-w-4xl mx-auto">
        <Card className="bg-rf-card/50 border-rf-mineshaft/50 backdrop-blur-sm rounded-2xl p-8 lg:p-12">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            {/* Left: Photo placeholder */}
            <div className="relative">
              <div className="aspect-square rounded-2xl bg-gradient-to-br from-rf-accent/20 to-rf-mineshaft/30 border border-rf-mineshaft/50 flex items-center justify-center">
                <div className="w-24 h-24 rounded-full bg-rf-accent/30 border border-rf-accent/50 flex items-center justify-center">
                  <span className="text-4xl font-bold text-rf-accent">
                    {COPY.testimonial.author[0]}
                  </span>
                </div>
              </div>
            </div>

            {/* Right: Quote */}
            <div className="space-y-4">
              <Quote className="w-8 h-8 text-rf-accent/50" />
              <blockquote className="text-lg sm:text-xl text-rf-ink leading-relaxed">
                "{COPY.testimonial.quote}"
              </blockquote>
              <div className="pt-4 border-t border-rf-mineshaft/30">
                <p className="text-rf-ink font-semibold">{COPY.testimonial.author}</p>
                <p className="text-rf-subtle text-sm">
                  {COPY.testimonial.role} {COPY.testimonial.company}
                </p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </Section>
  );
}

