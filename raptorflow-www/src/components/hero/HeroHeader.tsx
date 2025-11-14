"use client";

import { Button } from "@/components/ui/button";
import { TextRotate } from "@/components/system/TextRotate";
import { Badge } from "@/components/ui/badge";
import { COPY } from "@/lib/copy";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function HeroHeader() {
  return (
    <section className="relative min-h-screen flex items-center justify-center px-4 py-20 overflow-hidden">
      {/* Content */}
      <div className="relative z-10 max-w-7xl w-full mx-auto">
        {/* Badge */}
        <div className="flex justify-center mb-6">
          <Badge className="bg-rf-card/50 border-rf-mineshaft/50 text-rf-subtle px-4 py-1.5 text-sm font-normal backdrop-blur-sm">
            <TextRotate phrases={COPY.hero.badge} interval={3000} />
          </Badge>
        </div>

        {/* Headline */}
        <div className="text-center space-y-6 mb-8">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold text-rf-ink leading-tight max-w-5xl mx-auto [text-shadow:_0_4px_20px_rgb(0_0_0_/_60%)]">
            Stop guessing what to post.{" "}
            <span className="text-rf-subtle">Start looking like you know marketing.</span>
          </h1>
          
          {/* Subhead */}
          <p className="text-lg sm:text-xl text-rf-subtle max-w-3xl mx-auto leading-relaxed [text-shadow:_0_2px_10px_rgb(0_0_0_/_50%)]">
            {COPY.hero.subhead}
          </p>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
          <Button
            size="lg"
            className="bg-rf-accent hover:bg-rf-accent/90 text-white px-8 py-6 text-lg rounded-xl shadow-lg"
          >
            {COPY.hero.ctaPrimary}
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="border-rf-mineshaft/50 text-rf-ink hover:bg-rf-card/50 bg-rf-card/20 backdrop-blur-sm px-8 py-6 text-lg rounded-xl"
          >
            {COPY.hero.ctaSecondary}
          </Button>
        </div>

        {/* Microtext */}
        <p className="text-center text-xs text-rf-subtle/70 mb-12">
          {COPY.hero.microtext}
        </p>

        {/* Hero Visual - Glassy Card with Mini Dashboard */}
        <div className="max-w-4xl mx-auto mb-16">
          <Card className="bg-rf-card/30 border-rf-mineshaft/30 backdrop-blur-xl rounded-2xl p-6 lg:p-8 shadow-rf">
            <div className="space-y-4">
              {/* Goal Pill */}
              <div className="flex justify-end">
                <Badge className="bg-rf-accent/20 text-rf-accent border-rf-accent/30 px-3 py-1">
                  Goal: Fill 200 tables
                </Badge>
              </div>

              {/* Weekly Calendar */}
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-rf-ink/80">This Week</h3>
                <div className="grid grid-cols-7 gap-2">
                  {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day, idx) => (
                    <div
                      key={day}
                      className={cn(
                        "rounded-lg p-3 text-center border",
                        idx === 2
                          ? "bg-rf-accent/20 border-rf-accent/30"
                          : "bg-rf-card/50 border-rf-mineshaft/30"
                      )}
                    >
                      <div className="text-xs text-rf-subtle mb-1">{day}</div>
                      {idx === 2 && (
                        <div className="w-2 h-2 rounded-full bg-rf-accent mx-auto" />
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Today's Focus */}
              <div className="space-y-2 pt-4 border-t border-rf-mineshaft/30">
                <h3 className="text-sm font-semibold text-rf-ink/80">Today's focus</h3>
                <div className="space-y-2">
                  {["Announce shipping update", "Post case study snippet", "Engage with 3 prospects"].map(
                    (task, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-sm text-rf-subtle">
                        <div className={cn(
                          "w-1.5 h-1.5 rounded-full",
                          idx === 0 ? "bg-rf-accent" : "bg-rf-mineshaft"
                        )} />
                        <span>{task}</span>
                      </div>
                    )
                  )}
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Mini KPI Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {COPY.hero.kpis.map((kpi, idx) => (
            <div
              key={idx}
              className="text-center p-4 rounded-xl bg-rf-card/30 border border-rf-mineshaft/30 backdrop-blur-sm"
            >
              <div className="text-lg font-semibold text-rf-ink mb-1">{kpi.value}</div>
              <div className="text-sm text-rf-subtle">{kpi.description}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
