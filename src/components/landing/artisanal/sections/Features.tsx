"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { HugeiconsIcon } from "@hugeicons/react";
import { 
  WorkflowCircle03Icon,
  AiBrain01Icon,
  ZapIcon,
  Shield01Icon,
  ChartHistogramIcon,
  CodeCircleIcon
} from "@hugeicons/core-free-icons";

const features = [
  {
    icon: AiBrain01Icon,
    title: "AI-Powered Workflows",
    description: "Intelligent automation that learns your patterns and optimizes your processes like a skilled craftsman refining their technique.",
    color: "barley",
  },
  {
    icon: WorkflowCircle03Icon,
    title: "Visual Orchestration",
    description: "Design complex workflows with our intuitive canvas. Drag, drop, and connect — like arranging the perfect coffee pour.",
    color: "akaroa",
  },
  {
    icon: ZapIcon,
    title: "Lightning Execution",
    description: "Sub-millisecond response times. Your workflows execute faster than you can say 'espresso'.",
    color: "barley",
  },
  {
    icon: Shield01Icon,
    title: "Enterprise Security",
    description: "Bank-grade encryption and compliance. Your data is roasted to perfection and locked in a vault.",
    color: "akaroa",
  },
  {
    icon: ChartHistogramIcon,
    title: "Rich Analytics",
    description: "Deep insights into your workflow performance. Every metric tells a story worth savoring.",
    color: "barley",
  },
  {
    icon: CodeCircleIcon,
    title: "Seamless Integrations",
    description: "Connect with 200+ tools effortlessly. Your entire tech stack, unified like notes in a perfect blend.",
    color: "akaroa",
  },
];

export function Features() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sectionRef.current) return;

    const ctx = gsap.context(() => {
      // Title animation
      gsap.fromTo(
        titleRef.current,
        { y: 60, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.8,
          ease: "power3.out",
          scrollTrigger: {
            trigger: titleRef.current,
            start: "top 85%",
            toggleActions: "play none none none",
          },
        }
      );

      // Cards stagger animation
      const cards = cardsRef.current?.querySelectorAll(".feature-card");
      if (cards) {
        gsap.fromTo(
          cards,
          { y: 80, opacity: 0, scale: 0.95 },
          {
            y: 0,
            opacity: 1,
            scale: 1,
            duration: 0.7,
            stagger: 0.1,
            ease: "power3.out",
            scrollTrigger: {
              trigger: cardsRef.current,
              start: "top 80%",
              toggleActions: "play none none none",
            },
          }
        );
      }
    });

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      id="features"
      className="relative py-32 bg-shaft-500 overflow-hidden"
    >
      {/* Background Texture */}
      <div className="absolute inset-0 opacity-30">
        <div 
          className="absolute inset-0"
          style={{
            backgroundImage: `radial-gradient(circle at 25% 25%, rgba(166, 135, 99, 0.1) 0%, transparent 50%),
                              radial-gradient(circle at 75% 75%, rgba(215, 201, 174, 0.05) 0%, transparent 50%)`,
          }}
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8">
        {/* Section Header */}
        <div ref={titleRef} className="text-center max-w-3xl mx-auto mb-20">
          <span className="inline-block text-barley text-sm font-medium tracking-widest uppercase mb-4">
            The Toolkit
          </span>
          <h2 className="font-display text-4xl sm:text-5xl lg:text-6xl font-semibold text-rock mb-6 leading-tight">
            Everything You Need to
            <span className="text-barley italic"> Brew Success</span>
          </h2>
          <p className="text-akaroa-200/60 text-lg leading-relaxed">
            Like a carefully curated selection of single-origin beans, 
            each feature is crafted to deliver an exceptional experience.
          </p>
        </div>

        {/* Features Grid */}
        <div ref={cardsRef} className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className="feature-card group relative p-8 rounded-2xl bg-shaft-400/30 border border-barley/5 hover:border-barley/20 transition-all duration-500 hover:bg-shaft-400/50"
                data-cursor-hover
              >
                {/* Hover Glow */}
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-barley/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                
                {/* Icon */}
                <div className={`relative w-14 h-14 rounded-xl bg-${feature.color}/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500`}>
                  <HugeiconsIcon icon={Icon} className={`w-7 h-7 text-${feature.color}`} />
                </div>

                {/* Content */}
                <h3 className="font-display text-2xl font-semibold text-rock mb-3 group-hover:text-barley transition-colors duration-300">
                  {feature.title}
                </h3>
                <p className="text-akaroa-200/50 leading-relaxed">
                  {feature.description}
                </p>

                {/* Number */}
                <span className="absolute top-6 right-6 font-display text-6xl font-bold text-barley/5 group-hover:text-barley/10 transition-colors duration-500">
                  {String(index + 1).padStart(2, "0")}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
