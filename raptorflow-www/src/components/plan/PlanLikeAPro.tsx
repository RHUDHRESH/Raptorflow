"use client";

import { COPY } from "@/lib/copy";
import { Section } from "@/components/system/Section";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Calendar } from "lucide-react";

export function PlanLikeAPro() {
  return (
    <Section className="py-16 lg:py-24">
      <div className="text-center mb-12 space-y-4">
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-rf-ink">
          {COPY.plan.title}
        </h2>
        <p className="text-lg sm:text-xl text-rf-subtle max-w-3xl mx-auto">
          {COPY.plan.subheading}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
        {/* Short Move */}
        <Card className="bg-rf-card/50 border-rf-mineshaft/50 backdrop-blur-sm rounded-2xl overflow-hidden hover:border-rf-accent/30 transition-all duration-300 hover:shadow-rf">
          <CardHeader>
            <div className="flex items-center justify-between mb-2">
              <CardTitle className="text-rf-ink text-2xl">{COPY.plan.shortMove.title}</CardTitle>
              <Badge className="bg-rf-accent/20 text-rf-accent border-rf-accent/30">
                {COPY.plan.shortMove.badge}
              </Badge>
            </div>
            <CardDescription className="text-rf-accent text-lg font-semibold">
              {COPY.plan.shortMove.duration}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-rf-subtle leading-relaxed">{COPY.plan.shortMove.description}</p>
            
            {/* Mini calendar strip */}
            <div className="pt-4 border-t border-rf-mineshaft/30">
              <div className="flex items-center gap-2 mb-3">
                <Calendar className="w-4 h-4 text-rf-subtle" />
                <span className="text-xs text-rf-subtle">Sample tasks</span>
              </div>
              <div className="grid grid-cols-7 gap-1">
                {Array.from({ length: 7 }).map((_, i) => (
                  <div
                    key={i}
                    className={cn(
                      "h-8 rounded text-xs flex items-center justify-center",
                      i < 3
                        ? "bg-rf-accent/20 text-rf-accent border border-rf-accent/30"
                        : "bg-rf-mineshaft/30 text-rf-subtle/50"
                    )}
                  >
                    {i + 1}
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Long Move */}
        <Card className="bg-rf-card/50 border-rf-mineshaft/50 backdrop-blur-sm rounded-2xl overflow-hidden hover:border-rf-accent/30 transition-all duration-300 hover:shadow-rf">
          <CardHeader>
            <div className="flex items-center justify-between mb-2">
              <CardTitle className="text-rf-ink text-2xl">{COPY.plan.longMove.title}</CardTitle>
              <Badge className="bg-rf-accent-2/20 text-rf-accent-2 border-rf-accent-2/30">
                {COPY.plan.longMove.badge}
              </Badge>
            </div>
            <CardDescription className="text-rf-accent-2 text-lg font-semibold">
              {COPY.plan.longMove.duration}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-rf-subtle leading-relaxed">{COPY.plan.longMove.description}</p>
            
            {/* Mini calendar strip */}
            <div className="pt-4 border-t border-rf-mineshaft/30">
              <div className="flex items-center gap-2 mb-3">
                <Calendar className="w-4 h-4 text-rf-subtle" />
                <span className="text-xs text-rf-subtle">Sample tasks</span>
              </div>
              <div className="grid grid-cols-7 gap-1">
                {Array.from({ length: 7 }).map((_, i) => (
                  <div
                    key={i}
                    className={cn(
                      "h-8 rounded text-xs flex items-center justify-center",
                      i < 5
                        ? "bg-rf-accent-2/20 text-rf-accent-2 border border-rf-accent-2/30"
                        : "bg-rf-mineshaft/30 text-rf-subtle/50"
                    )}
                  >
                    {i + 1}
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </Section>
  );
}
