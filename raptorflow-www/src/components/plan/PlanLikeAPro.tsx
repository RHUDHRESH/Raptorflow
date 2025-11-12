"use client";

import Image from "next/image";
import { COPY } from "@/lib/copy";
import { IMAGES } from "@/lib/images";
import { Section } from "@/components/system/Section";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function PlanLikeAPro() {
  return (
    <Section className="py-16">
      <h2 className="text-3xl sm:text-4xl font-bold text-center text-rf-ink mb-12">
        {COPY.plan.title}
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Card className="bg-rf-card/50 border-rf-mineshaft/50 backdrop-blur-sm overflow-hidden">
          <div className="relative w-full aspect-video">
            <Image
              src={IMAGES.planShort.src}
              alt={IMAGES.planShort.alt}
              fill
              className="object-cover"
            />
          </div>
          <CardHeader>
            <CardTitle className="text-rf-ink text-2xl">{COPY.plan.shortMove.title}</CardTitle>
            <CardDescription className="text-rf-accent text-lg font-semibold">
              {COPY.plan.shortMove.duration}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-rf-subtle">{COPY.plan.shortMove.description}</p>
          </CardContent>
        </Card>

        <Card className="bg-rf-card/50 border-rf-mineshaft/50 backdrop-blur-sm overflow-hidden">
          <div className="relative w-full aspect-video">
            <Image
              src={IMAGES.planLong.src}
              alt={IMAGES.planLong.alt}
              fill
              className="object-cover"
            />
          </div>
          <CardHeader>
            <CardTitle className="text-rf-ink text-2xl">{COPY.plan.longMove.title}</CardTitle>
            <CardDescription className="text-rf-accent text-lg font-semibold">
              {COPY.plan.longMove.duration}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-rf-subtle">{COPY.plan.longMove.description}</p>
          </CardContent>
        </Card>
      </div>
    </Section>
  );
}

