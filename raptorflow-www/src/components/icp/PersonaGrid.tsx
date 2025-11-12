"use client";

import Image from "next/image";
import { SpotLight } from "@/components/system/SpotLight";
import { COPY } from "@/lib/copy";
import { IMAGES } from "@/lib/images";
import { Section } from "@/components/system/Section";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const personas = [
  {
    id: "proof-driven",
    name: "Proof-Driven",
    tags: ["Proof-driven", "Hates fluff", "Needs examples"],
    tone: "Direct, evidence-based",
    channels: ["LinkedIn", "Twitter", "Email"],
    contentAngles: ["Case studies", "Data-driven insights", "Before/after comparisons"],
    examples: ["Show ROI metrics", "Share customer testimonials", "Display concrete results"],
  },
  {
    id: "visionary",
    name: "Visionary",
    tags: ["Big picture", "Future-focused", "Inspirational"],
    tone: "Aspirational, forward-thinking",
    channels: ["LinkedIn", "Medium", "YouTube"],
    contentAngles: ["Industry trends", "Future predictions", "Vision statements"],
    examples: ["Industry forecasts", "Thought leadership", "Strategic insights"],
  },
  {
    id: "practical",
    name: "Practical",
    tags: ["Step-by-step", "Actionable", "How-to"],
    tone: "Clear, instructional",
    channels: ["Blog", "YouTube", "Email"],
    contentAngles: ["Tutorials", "Guides", "Best practices"],
    examples: ["Step-by-step guides", "Tool recommendations", "Process breakdowns"],
  },
];

export function PersonaGrid() {
  return (
    <Section className="py-16 relative">
      <h2 className="text-3xl sm:text-4xl font-bold text-center text-rf-ink mb-4">
        {COPY.icp.title}
      </h2>
      <p className="text-center text-rf-subtle mb-12">{COPY.icp.subtitle}</p>

      <div className="relative w-full aspect-video rounded-2xl overflow-hidden border border-rf-mineshaft/50 mb-8">
        <Image
          src={IMAGES.icpCrowd.src}
          alt={IMAGES.icpCrowd.alt}
          fill
          className="object-cover"
        />
        <div className="absolute inset-0">
          <SpotLight className="opacity-50" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {personas.map((persona) => (
          <Dialog key={persona.id}>
            <DialogTrigger asChild>
              <Card className="bg-rf-card/50 border-rf-mineshaft/50 backdrop-blur-sm cursor-pointer hover:bg-rf-card/70 transition-all">
                <CardHeader>
                  <CardTitle className="text-rf-ink">{persona.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {persona.tags.map((tag) => (
                      <Badge key={tag} variant="secondary" className="bg-rf-mineshaft/50 text-rf-subtle">
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
                  Detailed strategy for {persona.name.toLowerCase()} personas
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-6 mt-4">
                <div>
                  <h4 className="text-sm font-semibold text-rf-ink mb-2">Tone</h4>
                  <p className="text-rf-subtle">{persona.tone}</p>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-rf-ink mb-2">Channels</h4>
                  <div className="flex flex-wrap gap-2">
                    {persona.channels.map((channel) => (
                      <Badge key={channel} variant="outline" className="border-rf-mineshaft text-rf-subtle">
                        {channel}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-rf-ink mb-2">Content Angles</h4>
                  <ul className="list-disc list-inside text-rf-subtle space-y-1">
                    {persona.contentAngles.map((angle) => (
                      <li key={angle}>{angle}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-rf-ink mb-2">Examples</h4>
                  <ul className="list-disc list-inside text-rf-subtle space-y-1">
                    {persona.examples.map((example) => (
                      <li key={example}>{example}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        ))}
      </div>
    </Section>
  );
}

