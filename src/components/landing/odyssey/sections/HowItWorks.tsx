"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Compass, Map, Rocket } from "lucide-react";

const steps = [
  {
    number: "01",
    icon: Compass,
    title: "Chart Your Course",
    description: "Answer a few strategic questions. Our AI builds your complete marketing foundation—positioning, messaging, and ideal customer profiles.",
    color: "purple",
  },
  {
    number: "02",
    icon: Map,
    title: "Plan Your Moves",
    description: "Transform strategy into executable campaigns. Each 'Move' is a complete playbook with content, timing, and channel strategy.",
    color: "blue",
  },
  {
    number: "03",
    icon: Rocket,
    title: "Execute & Optimize",
    description: "Launch with confidence. Real-time analytics show what's working, and AI suggests optimizations to maximize ROI.",
    color: "pink",
  },
];

export function HowItWorks() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sectionRef.current) return;

    const ctx = gsap.context(() => {
      // Title animation
      gsap.fromTo(
        ".how-title",
        { y: 50, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.8,
          ease: "power3.out",
          scrollTrigger: {
            trigger: ".how-title",
            start: "top 80%",
            toggleActions: "play none none reverse",
          },
        }
      );

      // Progress bar animation
      gsap.fromTo(
        progressRef.current,
        { scaleY: 0 },
        {
          scaleY: 1,
          ease: "none",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top center",
            end: "bottom center",
            scrub: 1,
          },
        }
      );

      // Step cards animation
      const steps = sectionRef.current!.querySelectorAll(".step-card");
      steps.forEach((step, index) => {
        gsap.fromTo(
          step,
          { 
            x: index % 2 === 0 ? -50 : 50, 
            opacity: 0 
          },
          {
            x: 0,
            opacity: 1,
            duration: 0.8,
            ease: "power3.out",
            scrollTrigger: {
              trigger: step,
              start: "top 75%",
              toggleActions: "play none none reverse",
            },
          }
        );
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      id="how-it-works"
      className="relative py-32 overflow-hidden"
    >
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-purple-900/10 to-transparent" />

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8">
        {/* Section Header */}
        <div className="how-title text-center mb-24">
          <span className="inline-block px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300 text-sm font-medium tracking-wide mb-6">
            How It Works
          </span>
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6">
            Three Steps to{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
              Marketing Mastery
            </span>
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            From scattered efforts to strategic execution. Here's how RaptorFlow transforms your marketing.
          </p>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Progress Line */}
          <div className="absolute left-1/2 top-0 bottom-0 w-px bg-white/10 -translate-x-1/2 hidden lg:block">
            <div
              ref={progressRef}
              className="absolute top-0 left-0 right-0 bg-gradient-to-b from-purple-500 via-blue-500 to-pink-500 origin-top"
              style={{ height: "100%" }}
            />
          </div>

          {/* Step Cards */}
          <div className="space-y-24 lg:space-y-32">
            {steps.map((step, index) => (
              <div
                key={index}
                className={`step-card relative flex flex-col lg:flex-row items-center gap-8 lg:gap-16 ${
                  index % 2 === 0 ? "lg:flex-row" : "lg:flex-row-reverse"
                }`}
              >
                {/* Content */}
                <div className={`flex-1 ${index % 2 === 0 ? "lg:text-right" : "lg:text-left"}`}>
                  <div className={`inline-flex items-center gap-3 mb-4 ${index % 2 === 0 ? "lg:flex-row-reverse" : ""}`}>
                    <span className="text-6xl font-bold text-white/10">{step.number}</span>
                    <div className={`p-3 rounded-xl bg-${step.color}-500/20 border border-${step.color}-500/30`}>
                      <step.icon className={`w-6 h-6 text-${step.color}-400`} />
                    </div>
                  </div>
                  <h3 className="text-2xl sm:text-3xl font-bold text-white mb-4">
                    {step.title}
                  </h3>
                  <p className="text-white/60 text-lg leading-relaxed max-w-md ml-auto mr-auto lg:ml-0 lg:mr-0">
                    {step.description}
                  </p>
                </div>

                {/* Center Node */}
                <div className="relative hidden lg:flex items-center justify-center">
                  <div className={`w-4 h-4 rounded-full bg-${step.color}-500 shadow-lg shadow-${step.color}-500/50`} />
                  <div className={`absolute w-8 h-8 rounded-full bg-${step.color}-500/30 animate-ping`} />
                </div>

                {/* Visual Placeholder */}
                <div className="flex-1 w-full max-w-md">
                  <div className={`aspect-square rounded-2xl bg-gradient-to-br from-${step.color}-500/20 to-transparent border border-${step.color}-500/20 p-8 flex items-center justify-center group hover:from-${step.color}-500/30 transition-all duration-500`}>
                    <div className="relative">
                      <step.icon className={`w-24 h-24 text-${step.color}-400/50 group-hover:scale-110 transition-transform duration-500`} />
                      <div className={`absolute inset-0 blur-3xl bg-${step.color}-500/30 opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
