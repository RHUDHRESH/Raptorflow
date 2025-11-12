"use client";

import Image from "next/image";
import { Button } from "@/components/ui/button";
import { TextRotate } from "@/components/system/TextRotate";
import { COPY } from "@/lib/copy";
import { IMAGES } from "@/lib/images";
import { Section } from "@/components/system/Section";

export function HeroHeader() {
  return (
    <Section className="pt-32 pb-16">
      <div className="text-center space-y-8">
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-rf-ink leading-tight">
          {COPY.hero.headline}
        </h1>
        <p className="text-xl sm:text-2xl text-rf-subtle">
          <TextRotate phrases={COPY.hero.rotatingStraplines} />
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8">
          <Button
            size="lg"
            className="bg-rf-accent hover:bg-rf-accent/90 text-white px-8 py-6 text-lg"
          >
            {COPY.hero.ctaPrimary}
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="border-rf-mineshaft text-rf-ink hover:bg-rf-card px-8 py-6 text-lg"
          >
            {COPY.hero.ctaSecondary}
          </Button>
        </div>

        <div className="pt-12">
          <div className="relative w-full aspect-video rounded-2xl overflow-hidden border border-rf-mineshaft/50">
            <Image
              src={IMAGES.hero.src}
              alt={IMAGES.hero.alt}
              fill
              className="object-cover"
              priority
            />
          </div>
        </div>
      </div>
    </Section>
  );
}

