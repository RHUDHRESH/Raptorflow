"use client";

import { useState } from "react";
import { COPY } from "@/lib/copy";
import { Section } from "@/components/system/Section";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";
import { Brain } from "lucide-react";

export function PersonaGrid() {
  const [selectedPersona, setSelectedPersona] = useState<string | null>(null);

  return (
    <Section className="py-16 lg:py-24 relative">
      <div className="text-center mb-12 space-y-4">
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-rf-ink">
          {COPY.icp.title}
        </h2>
        <p className="text-lg sm:text-xl text-rf-subtle max-w-3xl mx-auto">
          {COPY.icp.subheading}
        </p>
      </div>

      {/* Visual representation: Crowd to Personas */}
      <div className="relative mb-12 max-w-5xl mx-auto">
        {/* Left: Blurred crowd representation */}
        <div className="relative h-64 rounded-2xl overflow-hidden border border-rf-mineshaft/50 bg-gradient-to-r from-rf-card/50 via-rf-card/30 to-transparent">
          {/* Abstract crowd silhouette effect */}
          <div className="absolute inset-0 flex items-center justify-start px-8">
            <div className="flex gap-2">
              {Array.from({ length: 8 }).map((_, i) => (
                <div
                  key={i}
                  className={cn(
                    "w-12 h-12 rounded-full bg-rf-mineshaft/40 blur-sm",
                    "opacity-60"
                  )}
                  style={{
                    transform: `translateY(${Math.sin(i) * 10}px)`,
                  }}
                />
              ))}
            </div>
          </div>

          {/* Middle: Spotlight beam with icon */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="relative z-10">
              <div className="w-16 h-16 rounded-full bg-rf-accent/20 border border-rf-accent/30 flex items-center justify-center backdrop-blur-sm">
                <Brain className="w-8 h-8 text-rf-accent" />
              </div>
              {/* Beam effect */}
              <div className="absolute inset-0 -z-10">
                <div className="w-full h-1 bg-gradient-to-r from-transparent via-rf-accent/30 to-transparent" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Persona Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 max-w-5xl mx-auto">
        {COPY.icp.personas.map((persona) => (
          <Dialog key={persona.id}>
            <DialogTrigger asChild>
              <Card
                className={cn(
                  "bg-rf-card/50 border-rf-mineshaft/50 backdrop-blur-sm cursor-pointer",
                  "hover:bg-rf-card/70 hover:border-rf-accent/30 transition-all duration-300",
                  "hover:shadow-rf hover:-translate-y-1 rounded-2xl",
                  "group"
                )}
              >
                <CardHeader>
                  {/* Avatar circle */}
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-rf-accent/20 to-rf-accent/10 border border-rf-accent/30 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <span className="text-2xl font-bold text-rf-accent">
                      {persona.name.split(" ")[1]?.[0] || persona.name[0]}
                    </span>
                  </div>
                  <CardTitle className="text-rf-ink text-xl">{persona.name}</CardTitle>
                  <p className="text-sm text-rf-subtle mt-1">{persona.role}</p>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {persona.tags.map((tag) => (
                      <Badge
                        key={tag}
                        variant="secondary"
                        className="bg-rf-mineshaft/50 text-rf-subtle border-rf-mineshaft/50 text-xs"
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </DialogTrigger>
            <DialogContent className="bg-rf-card border-rf-mineshaft max-w-2xl">
              <DialogHeader>
                <DialogTitle className="text-rf-ink text-2xl">{persona.name}</DialogTitle>
                <DialogDescription className="text-rf-subtle">
                  {persona.role}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-6 mt-4">
                <div>
                  <h4 className="text-sm font-semibold text-rf-ink mb-2">Tags</h4>
                  <div className="flex flex-wrap gap-2">
                    {persona.tags.map((tag) => (
                      <Badge
                        key={tag}
                        variant="outline"
                        className="border-rf-mineshaft text-rf-subtle"
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-rf-ink mb-2">Strategy</h4>
                  <p className="text-rf-subtle leading-relaxed">{persona.description}</p>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        ))}
      </div>
    </Section>
  );
}
