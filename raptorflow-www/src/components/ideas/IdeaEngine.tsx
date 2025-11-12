"use client";

import Image from "next/image";
import { COPY } from "@/lib/copy";
import { IMAGES } from "@/lib/images";
import { Section } from "@/components/system/Section";

export function IdeaEngine() {
  return (
    <Section className="py-16">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
        <div className="space-y-6">
          <h2 className="text-3xl sm:text-4xl font-bold text-rf-ink">
            {COPY.ideas.title}
          </h2>
          <p className="text-lg text-rf-subtle">{COPY.ideas.description}</p>
        </div>
        <div className="relative w-full aspect-square rounded-2xl overflow-hidden border border-rf-mineshaft/50">
          <Image
            src={IMAGES.ideaEngine.src}
            alt={IMAGES.ideaEngine.alt}
            fill
            className="object-cover"
          />
        </div>
      </div>
    </Section>
  );
}

