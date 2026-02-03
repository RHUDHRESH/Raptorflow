"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { HugeiconsIcon } from "@hugeicons/react";
import { 
  Rocket01Icon, 
  SparklesIcon, 
  ArrowDown01Icon,
  PlayIcon
} from "@hugeicons/core-free-icons";

export function Hero() {
  const heroRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const subtitleRef = useRef<HTMLParagraphElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!heroRef.current) return;

    const ctx = gsap.context(() => {
      // Timeline for hero entrance
      const tl = gsap.timeline({ defaults: { ease: "power3.out" } });

      tl.fromTo(
        titleRef.current,
        { y: 100, opacity: 0, clipPath: "inset(100% 0 0 0)" },
        { y: 0, opacity: 1, clipPath: "inset(0% 0 0 0)", duration: 1.2 }
      )
      .fromTo(
        subtitleRef.current,
        { y: 40, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.8 },
        "-=0.6"
      )
      .fromTo(
        ctaRef.current,
        { y: 30, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.6 },
        "-=0.4"
      )
      .fromTo(
        imageRef.current,
        { y: 60, opacity: 0, scale: 0.95 },
        { y: 0, opacity: 1, scale: 1, duration: 1 },
        "-=0.4"
      );

      // Parallax on scroll
      gsap.to(imageRef.current, {
        yPercent: 20,
        ease: "none",
        scrollTrigger: {
          trigger: heroRef.current,
          start: "top top",
          end: "bottom top",
          scrub: true,
        },
      });
    });

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={heroRef}
      className="relative min-h-screen flex items-center pt-24 pb-16 overflow-hidden bg-shaft-500"
    >
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Gradient Orbs */}
        <div className="absolute top-1/4 -left-32 w-96 h-96 bg-barley/10 rounded-full blur-[128px] animate-pulse-subtle" />
        <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-akaroa/10 rounded-full blur-[128px] animate-pulse-subtle" style={{ animationDelay: "1.5s" }} />
        
        {/* Grid Pattern */}
        <div 
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `linear-gradient(rgba(234, 224, 210, 0.5) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(234, 224, 210, 0.5) 1px, transparent 1px)`,
            backgroundSize: "60px 60px",
          }}
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 w-full">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left Content */}
          <div className="text-center lg:text-left">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-barley/10 border border-barley/20 mb-8">
              <HugeiconsIcon icon={SparklesIcon} className="w-4 h-4 text-barley" />
              <span className="text-barley text-sm font-medium tracking-wide">AI-Powered Workflow Automation</span>
            </div>

            {/* Title */}
            <h1
              ref={titleRef}
              className="font-display text-5xl sm:text-6xl lg:text-7xl xl:text-8xl font-semibold text-rock leading-[0.95] tracking-tight mb-6"
            >
              Crafted for
              <span className="block text-barley italic">Creators</span>
            </h1>

            {/* Subtitle */}
            <p
              ref={subtitleRef}
              className="text-akaroa-200/70 text-lg sm:text-xl max-w-xl mx-auto lg:mx-0 mb-10 leading-relaxed"
            >
              Like a master barista perfecting every cup, RaptorFlow orchestrates 
              your business workflows with precision, warmth, and undeniable style.
            </p>

            {/* CTAs */}
            <div ref={ctaRef} className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <button 
                className="group relative px-8 py-4 bg-barley text-shaft-500 font-semibold rounded-full overflow-hidden transition-all duration-300 hover:shadow-xl hover:shadow-barley/20"
                data-cursor-hover
              >
                <span className="relative z-10 flex items-center justify-center gap-2">
                  <HugeiconsIcon icon={Rocket01Icon} className="w-5 h-5" />
                  Start Free Trial
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-barley to-akaroa-400 transform translate-y-full transition-transform duration-300 group-hover:translate-y-0" />
              </button>
              
              <button 
                className="group px-8 py-4 border border-rock/30 text-rock rounded-full font-medium transition-all duration-300 hover:bg-rock/5 hover:border-rock/50 flex items-center justify-center gap-2"
                data-cursor-hover
              >
                <HugeiconsIcon icon={PlayIcon} className="w-5 h-5" />
                Watch Demo
              </button>
            </div>

            {/* Trust Indicators */}
            <div className="mt-12 pt-8 border-t border-rock/10">
              <p className="text-rock/40 text-sm mb-4 tracking-wide uppercase">Trusted by innovative teams</p>
              <div className="flex items-center justify-center lg:justify-start gap-8 opacity-50">
                {["Notion", "Figma", "Slack", "Linear"].map((brand) => (
                  <span key={brand} className="text-rock/60 font-display text-lg">{brand}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Right Content - Dashboard Preview */}
          <div ref={imageRef} className="relative">
            <div className="relative rounded-2xl overflow-hidden shadow-2xl shadow-black/30">
              {/* Main Dashboard Image */}
              <div className="aspect-[4/3] bg-gradient-to-br from-akaroa-700 to-shaft-400 relative">
                {/* Mock Dashboard UI */}
                <div className="absolute inset-4 bg-shaft-500/90 rounded-xl border border-barley/10 p-6">
                  {/* Header */}
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-barley/20 flex items-center justify-center">
                        <Rocket01Icon className="w-5 h-5 text-barley" />
                      </div>
                      <div>
                        <div className="h-3 w-24 bg-barley/30 rounded" />
                        <div className="h-2 w-16 bg-rock/20 rounded mt-2" />
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <div className="w-8 h-8 rounded-full bg-barley/20" />
                      <div className="w-8 h-8 rounded-full bg-akaroa/20" />
                    </div>
                  </div>
                  
                  {/* Stats Row */}
                  <div className="grid grid-cols-3 gap-4 mb-6">
                    {[
                      { label: "Tasks", value: "2,847", trend: "+12%" },
                      { label: "Automated", value: "94%", trend: "+5%" },
                      { label: "Time Saved", value: "126h", trend: "+23%" },
                    ].map((stat) => (
                      <div key={stat.label} className="bg-shaft-400/50 rounded-lg p-4 border border-barley/5">
                        <p className="text-rock/50 text-xs mb-1">{stat.label}</p>
                        <div className="flex items-end justify-between">
                          <span className="text-rock font-display text-2xl">{stat.value}</span>
                          <span className="text-barley text-xs">{stat.trend}</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Workflow Visualization */}
                  <div className="space-y-3">
                    {["Content Creation", "Lead Nurturing", "Analytics Report"].map((flow, i) => (
                      <div key={flow} className="flex items-center gap-4 p-3 bg-shaft-400/30 rounded-lg border border-barley/5">
                        <div className="w-2 h-2 rounded-full bg-barley" />
                        <span className="text-rock/80 text-sm flex-1">{flow}</span>
                        <div className="flex gap-1">
                          {[...Array(3)].map((_, j) => (
                            <div 
                              key={j} 
                              className={`w-1.5 h-1.5 rounded-full ${j <= i ? "bg-barley" : "bg-rock/20"}`}
                            />
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              {/* Glow Effect */}
              <div className="absolute -inset-1 bg-gradient-to-r from-barley/20 via-akaroa/20 to-barley/20 rounded-2xl blur-xl opacity-50 -z-10" />
            </div>

            {/* Floating Elements */}
            <div className="absolute -top-6 -right-6 w-24 h-24 bg-barley/10 rounded-2xl border border-barley/20 backdrop-blur-sm flex items-center justify-center animate-float">
              <HugeiconsIcon icon={SparklesIcon} className="w-8 h-8 text-barley" />
            </div>
            <div className="absolute -bottom-4 -left-4 px-4 py-3 bg-shaft-400/90 rounded-xl border border-barley/20 backdrop-blur-sm animate-float" style={{ animationDelay: "2s" }}>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-rock text-sm">All systems operational</span>
              </div>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 opacity-50">
          <span className="text-rock/40 text-xs tracking-widest uppercase">Scroll</span>
          <HugeiconsIcon icon={ArrowDown01Icon} className="w-5 h-5 text-rock/40 animate-bounce" />
        </div>
      </div>
    </section>
  );
}
